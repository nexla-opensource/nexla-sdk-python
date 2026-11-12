"""
Authentication utilities for the Nexla SDK
"""

import base64
import logging
import threading
import time
from typing import Any, Dict, Optional, Tuple, Union

from pydantic import ValidationError as PydanticValidationError

from .exceptions import (
    AuthenticationError,
    NexlaConnectionError,
    NexlaError,
    NexlaTimeoutError,
    error_from_response,
)
from .http_client import HttpClientInterface, RequestsHttpClient
from .models.tokens.responses import TokenResponse
from .transport_core import HttpClientError, HttpConnectionError, HttpTimeoutError

logger = logging.getLogger(__name__)


class TokenAuthHandler:
    """
    Handles authentication and token management for Nexla API

    Credential modes (spec section 2). Exactly one is used:

    1. **Service key**: ``Authorization: Basic <service_key>``, sent as is.
    2. **API key**: ``Authorization: Basic <api_key>``, sent as is.
    3. **Password**: ``Authorization: Basic base64("email:password[:org_id]")``.
    4. **Access token**: ``Authorization: Bearer <token>``. Never refreshed.

    The modes 1-3 obtain a session token with ``POST /token``. The optional
    ``dataplane`` value is sent as ``X-Nexla-Dataplane`` on ``/token`` calls only.

    Responsible for:
    - Obtaining session tokens (one shared request for concurrent callers)
    - Refreshing session tokens before expiry (modes 1-3)
    - Switching org with ``POST /token/refresh?org_id=``
    - Retrying once on 401 with a refreshable mode
    """

    def __init__(
        self,
        service_key: Optional[str] = None,
        access_token: Optional[str] = None,
        base_url: str = "https://dataops.nexla.io/nexla-api",
        api_version: str = "v1",
        token_refresh_margin: int = 3600,
        http_client: Optional[HttpClientInterface] = None,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        org_id: Optional[int] = None,
        dataplane: Optional[str] = None,
    ):
        """
        Initialize the token authentication handler

        Args:
            service_key: Service key (Basic, sent as is)
            access_token: Direct access token (Bearer, not refreshed)
            base_url: Nexla API base URL
            api_version: API version (kept for compatibility; the path carries the version)
            token_refresh_margin: Seconds before token expiry to trigger refresh
            http_client: HTTP client implementation (defaults to RequestsHttpClient)
            api_key: API key (Basic, sent as is)
            email: Login email for password mode
            password: Login password for password mode
            org_id: Optional org for password mode (Basic "email:password:org_id")
            dataplane: Optional dataplane uid, sent as X-Nexla-Dataplane on /token
        """
        self.service_key = service_key
        self.api_key = api_key
        self.email = email
        self.password = password
        self.org_id = org_id
        self.dataplane = dataplane
        self.api_url = base_url.rstrip("/")
        self.api_version = api_version
        self.token_refresh_margin = token_refresh_margin
        self.http_client = http_client or RequestsHttpClient()
        self.token_response: Optional[TokenResponse] = None
        self._lock = threading.RLock()

        # Session token management
        self._access_token: Optional[str] = None
        if access_token:
            self._using_direct_token = True
            self._access_token = access_token
            self._token_expiry = time.time() + 86400
        else:
            self._access_token = None
            self._token_expiry = 0
            self._using_direct_token = False

    def _basic_authorization(self) -> Optional[str]:
        """Return the Basic header value for the configured credential, or None."""
        if self.service_key:
            return f"Basic {self.service_key}"
        if self.api_key:
            return f"Basic {self.api_key}"
        if self.email and self.password:
            raw = f"{self.email}:{self.password}"
            if self.org_id is not None:
                raw = f"{raw}:{self.org_id}"
            return "Basic " + base64.b64encode(raw.encode()).decode()
        return None

    def _store(self, token: TokenResponse) -> None:
        self._access_token = token.access_token
        self._token_expiry = time.time() + token.expires_in
        self.token_response = token

    def _post_token(
        self, url: str, headers: Dict[str, str], params: Optional[Dict[str, Any]] = None
    ) -> TokenResponse:
        """POST to a token endpoint. Map errors to typed NexlaErrors."""
        try:
            data = self.http_client.request(
                "POST", url, headers=headers, params=params or {}
            )
        except HttpTimeoutError as e:
            raise NexlaTimeoutError(f"Failed to obtain session token: {e}") from e
        except HttpConnectionError as e:
            raise NexlaConnectionError(f"Failed to obtain session token: {e}") from e
        except HttpClientError as e:
            body = e.body if e.body is not None else (e.response or None)
            raise error_from_response(
                getattr(e, "status_code", None),
                body,
                headers=e.headers,
                method="POST",
                url=url,
                operation="authentication",
            ) from e
        except Exception as e:
            raise NexlaError(f"Failed to obtain session token: {e}") from e

        if not isinstance(data, dict) or not data.get("access_token"):
            raise AuthenticationError("Token response did not include an access token.")
        try:
            return TokenResponse.model_validate(data)
        except PydanticValidationError as e:
            raise NexlaError(f"Invalid token response: {e}") from e

    def get_access_token(self) -> str:
        """
        Get the current access token

        Returns:
            Current access token

        Raises:
            AuthenticationError: If no valid token is available
        """
        if not self._access_token:
            raise AuthenticationError(
                "No access token available. Authentication required."
            )
        return self._access_token

    def obtain_session_token(self) -> None:
        """
        Obtain a session token with POST /token using the configured credential.

        Raises:
            AuthenticationError: If the credential is missing or rejected
        """
        if self._using_direct_token:
            raise AuthenticationError(
                "Cannot obtain session token when using direct access token. Credentials required."
            )

        basic = self._basic_authorization()
        if basic is None:
            raise AuthenticationError(
                "Service key, API key, or email and password required to obtain session token."
            )

        headers = {
            "Authorization": basic,
            "Accept": "application/json",
            "Content-Length": "0",
        }
        if self.dataplane:
            headers["X-Nexla-Dataplane"] = self.dataplane

        token = self._post_token(f"{self.api_url}/token", headers)
        with self._lock:
            self._store(token)
        logger.debug("Session token obtained successfully")

    def refresh_session_token(self) -> None:
        """
        Refresh token (compat shim).
        - Direct tokens cannot be refreshed.
        - Other modes re-obtain a new token via POST /token.
        """
        if self._using_direct_token:
            raise AuthenticationError("Direct access tokens cannot be refreshed")
        self.obtain_session_token()

    def _needs_refresh(self) -> bool:
        return (
            not self._access_token
            or (self._token_expiry - time.time()) < self.token_refresh_margin
        )

    def ensure_valid_token(self) -> str:
        """
        Ensures a valid session token is available, refreshing if necessary.

        Concurrent callers share one refresh: the lock is taken, and the expiry
        is checked again before a request is sent.

        Returns:
            Current valid access token

        Raises:
            AuthenticationError: If no token is available or refresh fails
        """
        if self._using_direct_token:
            if not self._access_token:
                raise AuthenticationError("No access token available")
            return self._access_token

        if self._needs_refresh():
            with self._lock:
                if self._needs_refresh():
                    self.obtain_session_token()
        return self._access_token  # type: ignore[return-value]  # set by obtain_session_token above

    def switch_org(self, org_id: int) -> TokenResponse:
        """
        Switch the session to another org with POST /token/refresh?org_id=.

        The current Bearer token is sent. The response replaces the session token.
        The switch lasts until the next token fetch.

        Raises:
            NexlaError: On a failed request (for example 400 "Org context is not set")
        """
        token = self.ensure_valid_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Length": "0",
        }
        new_token = self._post_token(
            f"{self.api_url}/token/refresh", headers, params={"org_id": org_id}
        )
        with self._lock:
            self._store(new_token)
        return new_token

    def logout(self) -> None:
        """
        Ends the current session and invalidates the NexlaSessionToken.
        Calls POST /token/logout and clears local token if successful.
        """
        url = f"{self.api_url}/token/logout"
        headers = {
            "Accept": "application/json",
            "Authorization": (
                f"Bearer {self._access_token}" if self._access_token else ""
            ),
        }
        try:
            # Best-effort logout; ignore response body
            self.http_client.request("POST", url, headers=headers)
        except HttpClientError:
            # Still clear local token to avoid reuse
            pass
        finally:
            # Invalidate local token regardless
            self._access_token = None
            self._token_expiry = 0
            self.token_response = None

    def execute_authenticated_request(
        self, method: str, url: str, headers: Dict[str, str], **kwargs: Any
    ) -> Union[Dict[str, Any], None]:
        """
        Execute a request with authentication handling. Return the body only.

        Raises:
            AuthenticationError: If authentication fails
            ServerError: If the API returns an error
        """
        body, _ = self.execute_authenticated_request_with_headers(
            method, url, headers, **kwargs
        )
        return body

    def execute_authenticated_request_with_headers(
        self, method: str, url: str, headers: Dict[str, str], **kwargs: Any
    ) -> Tuple[Union[Dict[str, Any], None], Any]:
        """
        Execute a request with authentication handling. Return (body, response headers).

        On 401 with a refreshable mode, one new token is obtained and the request
        is retried once. Threads that saw the same stale token share that refresh.

        Args:
            method: HTTP method
            url: Full URL to call
            headers: HTTP headers
            **kwargs: Additional arguments to pass to the HTTP client

        Returns:
            (body, headers). The body is None for 204 No Content.

        Raises:
            AuthenticationError: If authentication fails
            ServerError: If the API returns an error
        """
        access_token = self.ensure_valid_token()
        headers["Authorization"] = f"Bearer {access_token}"

        try:
            return self.http_client.request_with_headers(
                method, url, headers=headers, **kwargs
            )

        except HttpClientError as e:
            if getattr(e, "status_code", None) != 401 or self._using_direct_token:
                # Direct tokens cannot be refreshed: the client maps the 401
                raise
            logger.warning(
                "401 received; obtaining new session token and retrying once"
            )
            with self._lock:
                if self._access_token == access_token:
                    self.obtain_session_token()
                new_token = self._access_token
            headers["Authorization"] = f"Bearer {new_token}"
            return self.http_client.request_with_headers(
                method, url, headers=headers, **kwargs
            )
