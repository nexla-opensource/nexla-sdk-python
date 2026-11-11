"""
Authentication utilities for the Nexla SDK
"""

import logging
import time
from typing import Any, Dict, Optional, Union

from .exceptions import (
    AuthenticationError,
    NexlaConnectionError,
    NexlaError,
    NexlaTimeoutError,
    error_from_response,
)
from .http_client import (
    HttpClientError,
    HttpClientInterface,
    HttpConnectionError,
    HttpTimeoutError,
    RequestsHttpClient,
)

logger = logging.getLogger(__name__)


class TokenAuthHandler:
    """
    Handles authentication and token management for Nexla API

    Supports two authentication flows as per Nexla API documentation:

    1. **Service Key Flow**: Uses service keys to obtain session tokens via POST to
       /token endpoint with `Authorization: Basic <Service-Key>`. Automatically
       refreshes tokens before expiry using /token/refresh endpoint.

    2. **Direct Token Flow**: Uses pre-obtained access tokens directly. These tokens
       expire after a configured interval (usually 1 hour).

    Responsible for:
    - Obtaining session tokens using service keys (Basic auth)
    - Using directly provided access tokens (Bearer auth)
    - Refreshing session tokens before expiry (service key flow only)
    - Ensuring valid tokens are available for API requests
    - Handling authentication retries on 401 responses
    """

    def __init__(
        self,
        service_key: Optional[str] = None,
        access_token: Optional[str] = None,
        base_url: str = "https://dataops.nexla.io/nexla-api",
        api_version: str = "v1",
        token_refresh_margin: int = 3600,
        http_client: Optional[HttpClientInterface] = None,
    ):
        """
        Initialize the token authentication handler

        Args:
            service_key: Nexla service key for authentication (mutually exclusive with access_token)
            access_token: Nexla access token for direct authentication (mutually exclusive with service_key)
            base_url: Nexla API base URL
            api_version: API version to use
            token_refresh_margin: Seconds before token expiry to trigger refresh
            http_client: HTTP client implementation (defaults to RequestsHttpClient)
        """
        self.service_key = service_key
        self.api_url = base_url.rstrip("/")
        self.api_version = api_version
        self.token_refresh_margin = token_refresh_margin
        self.http_client = http_client or RequestsHttpClient()

        # Session token management
        if access_token:
            self._using_direct_token = True
            self._access_token = access_token
            self._token_expiry = time.time() + 86400
        else:
            self._access_token = None
            self._token_expiry = 0
            self._using_direct_token = False

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
        Obtains a session token using the service key

        Raises:
            AuthenticationError: If authentication fails or no service key available
        """
        if self._using_direct_token:
            raise AuthenticationError(
                "Cannot obtain session token when using direct access token. Service key required."
            )

        if not self.service_key:
            raise AuthenticationError("Service key required to obtain session token.")

        url = f"{self.api_url}/token"
        headers = {
            "Authorization": f"Basic {self.service_key}",
            "Accept": f"application/vnd.nexla.api.{self.api_version}+json",
            "Content-Length": "0",
        }

        try:
            token_data = self.http_client.request("POST", url, headers=headers)
            self._access_token = token_data.get("access_token")
            # Calculate expiry time (current time + expires_in seconds)
            expires_in = token_data.get("expires_in", 86400)
            self._token_expiry = time.time() + expires_in

            logger.debug("Session token obtained successfully")

        except HttpClientError as e:
            if isinstance(e, HttpTimeoutError):
                raise NexlaTimeoutError(f"Failed to obtain session token: {e}") from e
            if isinstance(e, HttpConnectionError):
                raise NexlaConnectionError(
                    f"Failed to obtain session token: {e}"
                ) from e
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

    def refresh_session_token(self) -> None:
        """
        Refresh token (compat shim).
        - Direct tokens cannot be refreshed.
        - Service key mode re-obtains a new token via /token.
        """
        if self._using_direct_token:
            raise AuthenticationError("Direct access tokens cannot be refreshed")
        # For service key, re-obtain a token via /token
        self.obtain_session_token()

    def ensure_valid_token(self) -> str:
        """
        Ensures a valid session token is available, refreshing if necessary

        Returns:
            Current valid access token

        Raises:
            AuthenticationError: If no token is available or refresh fails
        """
        if not self._access_token:
            if self._using_direct_token:
                raise AuthenticationError("No access token available")
            # Obtain new token using service key lazily
            self.obtain_session_token()
            return self._access_token

        # For service key, if nearing expiry, obtain a fresh token via /token
        if not self._using_direct_token:
            current_time = time.time()
            if (self._token_expiry - current_time) < self.token_refresh_margin:
                self.obtain_session_token()

        return self._access_token

    def logout(self) -> None:
        """
        Ends the current session and invalidates the NexlaSessionToken.
        Calls POST /token/logout and clears local token if successful.
        """
        url = f"{self.api_url}/token/logout"
        headers = {
            "Accept": f"application/vnd.nexla.api.{self.api_version}+json",
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

    def execute_authenticated_request(
        self, method: str, url: str, headers: Dict[str, str], **kwargs
    ) -> Union[Dict[str, Any], None]:
        """
        Execute a request with authentication handling

        Args:
            method: HTTP method
            url: Full URL to call
            headers: HTTP headers
            **kwargs: Additional arguments to pass to the HTTP client

        Returns:
            API response as a dictionary or None for 204 No Content responses

        Raises:
                    AuthenticationError: If authentication fails
        ServerError: If the API returns an error
        """
        # Get a valid token
        access_token = self.ensure_valid_token()

        # Add authorization header
        headers["Authorization"] = f"Bearer {access_token}"

        try:
            return self.http_client.request(method, url, headers=headers, **kwargs)

        except HttpClientError as e:
            if getattr(e, "status_code", None) == 401:
                # On 401: if service key mode, obtain new token and retry once
                if not self._using_direct_token:
                    logger.warning(
                        "401 received; obtaining new session token and retrying once"
                    )
                    self.obtain_session_token()
                    headers["Authorization"] = f"Bearer {self.get_access_token()}"
                    return self.http_client.request(
                        method, url, headers=headers, **kwargs
                    )
                # Direct token cannot be refreshed: the client maps the 401
                raise

            # For other errors, let the caller handle them
            raise
