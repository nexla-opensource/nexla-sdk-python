"""Transport-free helpers shared by the sync and async HTTP clients.

Nothing in this module performs I/O or imports an HTTP library. Both transports
pass their response object through these helpers. The helpers read only
``status_code``, ``headers``, ``content``, ``text`` and ``json()``, which both
requests and httpx responses provide.
"""

import os
from typing import Any, Dict, Mapping, Optional, Tuple

from .exceptions import (
    NexlaConnectionError,
    NexlaError,
    NexlaTimeoutError,
    error_from_response,
)

try:
    from importlib.metadata import version  # Python 3.8+

    SDK_VERSION = version("nexla-sdk")
except Exception:  # pragma: no cover
    SDK_VERSION = "unknown"

DEFAULT_BASE_URL = "https://dataops.nexla.io/nexla-api"


class HttpClientError(Exception):
    """Base exception for HTTP client errors"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        body: Any = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response or {}
        self.headers = headers or {}
        # Parsed JSON, trimmed text, or None for an empty body.
        self.body = body


class HttpTimeoutError(HttpClientError):
    """The request timed out (connect or read)."""


class HttpConnectionError(HttpClientError):
    """The connection failed before a response was received."""


def build_headers(extra: Optional[Mapping[str, str]] = None) -> Dict[str, str]:
    """Default User-Agent first. Caller headers win."""
    return {"User-Agent": f"nexla-sdk/{SDK_VERSION}", **(extra or {})}


def parse_error_body(resp: Any) -> Any:
    """Return the JSON body, else the trimmed text, else None when empty."""
    if resp is None or not getattr(resp, "content", None):
        return None
    try:
        return resp.json()
    except ValueError:
        return (resp.text or "").strip() or None


def parse_success_body(resp: Any) -> Any:
    """Parse a 2xx response body.

    Returns None for 204 or an empty body, the parsed JSON when it parses, and
    ``{"raw_text", "status_code"}`` for a non-JSON body.
    """
    if resp.status_code == 204 or not resp.content:
        return None
    content_type = resp.headers.get("content-type", "").lower()
    if "application/json" in content_type or "text/json" in content_type:
        return resp.json()
    try:
        return resp.json()
    except ValueError:
        return {"raw_text": resp.text, "status_code": resp.status_code}


def http_error_from(
    status_code: Optional[int],
    body: Any,
    headers: Optional[Mapping[str, Any]],
    message: str,
) -> HttpClientError:
    """Build the transport-level error for a non-2xx response."""
    return HttpClientError(
        message=message,
        status_code=status_code,
        response=body if isinstance(body, dict) else {},
        headers=dict(headers or {}),
        body=body,
    )


def unexpected_request_error(
    error: Exception, method: str, path: str, url: str, kwargs: Dict[str, Any]
) -> NexlaError:
    """Wrap an error that is not an HTTP client error."""
    return NexlaError(
        message=f"Request failed: {error}",
        operation=f"{method.lower()}_request",
        context={
            "method": method,
            "path": path,
            "url": url,
            "kwargs": {k: v for k, v in kwargs.items() if k not in ["json", "data"]},
        },
        original_error=error,
    )


def map_http_error(
    error: HttpClientError,
    method: str,
    path: str,
    url: str,
    kwargs: Dict[str, Any],
) -> NexlaError:
    """Map an HTTP client error to a typed NexlaError. The caller raises it.

    Status code and body shape choose the class (see exceptions.error_from_response).
    Timeouts map to NexlaTimeoutError and connection failures to NexlaConnectionError.
    """
    error_data = getattr(error, "response", {}) or {}

    # Extract resource information (prefer server-provided fields, fallback to path)
    resource_type = None
    resource_id = None
    if isinstance(error_data, dict):
        resource_type = error_data.get("resource_type") or None
        resource_id = error_data.get("resource_id") or None
    if not resource_type or not resource_id:
        # Fallback to parsing the path
        if path:
            path_parts = path.strip("/").split("/")
            if not resource_type and len(path_parts) >= 1:
                resource_type = path_parts[0]
            if not resource_id and len(path_parts) >= 2 and path_parts[1].isdigit():
                resource_id = path_parts[1]
    if not resource_type:
        resource_type = "unknown"

    context = {
        "method": method,
        "path": path,
        "url": url,
        "status_code": getattr(error, "status_code", None),
        "api_response": error_data,
        "request_params": {
            k: v for k, v in kwargs.items() if k not in ["json", "data"]
        },
    }
    common: Dict[str, Any] = {
        "operation": f"{method.lower()}_request",
        "resource_type": resource_type,
        "resource_id": resource_id,
        "context": context,
        "original_error": error,
    }

    if isinstance(error, HttpTimeoutError):
        return NexlaTimeoutError(
            f"Request timed out: {error}", method=method, url=url, **common
        )
    if isinstance(error, HttpConnectionError):
        return NexlaConnectionError(
            f"Connection failed: {error}", method=method, url=url, **common
        )

    body = error.body if error.body is not None else (error_data or None)
    return error_from_response(
        getattr(error, "status_code", None),
        body,
        headers=getattr(error, "headers", {}),
        method=method,
        url=url,
        **common,
    )


def resolve_base_url(base_url: Optional[str]) -> str:
    """Explicit base_url, else NEXLA_API_URL, else the default URL."""
    return base_url or os.getenv("NEXLA_API_URL") or DEFAULT_BASE_URL


def resolve_credentials(
    service_key: Optional[str],
    api_key: Optional[str],
    access_token: Optional[str],
    email: Optional[str],
    password: Optional[str],
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Choose exactly one credential mode. Returns (service_key, api_key, access_token).

    Explicit options win. Environment variables are read only when no option
    is passed: NEXLA_SERVICE_KEY, then NEXLA_API_KEY, then NEXLA_ACCESS_TOKEN.
    """
    has_password = bool(email or password)
    if has_password and not (email and password):
        raise NexlaError("email and password must be provided together")
    explicit = [
        name
        for name, value in (
            ("service_key", service_key),
            ("api_key", api_key),
            ("access_token", access_token),
            ("email/password", has_password),
        )
        if value
    ]
    if len(explicit) > 1:
        raise NexlaError(
            "Cannot provide more than one of service_key, api_key, access_token, "
            "or email/password. Choose one authentication method."
        )
    if not explicit:
        service_key = os.getenv("NEXLA_SERVICE_KEY") or None
        if not service_key:
            api_key = os.getenv("NEXLA_API_KEY") or None
        if not service_key and not api_key:
            access_token = os.getenv("NEXLA_ACCESS_TOKEN") or None

    if not (service_key or api_key or access_token or has_password):
        raise NexlaError(
            "Either service_key, api_key, access_token, or email and password must be "
            "provided as parameters or via NEXLA_SERVICE_KEY, NEXLA_API_KEY, or "
            "NEXLA_ACCESS_TOKEN environment variables"
        )
    return service_key, api_key, access_token
