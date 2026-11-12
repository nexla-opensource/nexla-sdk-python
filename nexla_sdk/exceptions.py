import http
from typing import Any, Dict, Optional, Tuple, Type, cast


class NexlaError(Exception):
    """Base exception for all Nexla errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        step: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        body: Any = None,
        request_id: Optional[str] = None,
        method: Optional[str] = None,
        url: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.operation = operation
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.step = step
        self.context = context or {}
        self.original_error = original_error
        self.status_code = status_code
        self.response = response
        self.error_code = error_code
        self.body = body
        self.request_id = request_id
        self.method = method
        self.url = url

    @property
    def status(self) -> Optional[int]:
        """HTTP status code. Same value as ``status_code``."""
        return self.status_code

    def __str__(self) -> str:
        """Provide detailed error information."""
        parts = []

        if self.step:
            parts.append(f"Step: {self.step}")
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        if self.resource_type:
            parts.append(f"Resource: {self.resource_type}")
        if self.resource_id:
            parts.append(f"ID: {self.resource_id}")

        parts.append(f"Error: {self.message}")

        if self.details:
            parts.append(f"Details: {self.details}")
        if self.context:
            parts.append(f"Context: {self.context}")
        if self.original_error:
            parts.append(f"Original Error: {self.original_error}")

        return " | ".join(parts)

    def get_error_summary(self) -> Dict[str, Any]:
        """Get structured error information."""
        return {
            "message": self.message,
            "step": self.step,
            "operation": self.operation,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "context": self.context,
            "status_code": self.status_code,
            "response": self.response,
            "original_error": str(self.original_error) if self.original_error else None,
        }


class AuthenticationError(NexlaError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", **kwargs: Any) -> None:
        # If operation is not provided, default to "authentication"
        if "operation" not in kwargs:
            kwargs["operation"] = "authentication"
        super().__init__(message, **kwargs)


class AccountLockedError(AuthenticationError):
    """Raised on HTTP 423: the account is locked."""

    pass


class AuthorizationError(NexlaError):
    """Raised when user lacks permission."""

    pass


class NotFoundError(NexlaError):
    """Raised when a resource is not found."""

    pass


class ValidationError(NexlaError):
    """Raised when request validation fails."""

    pass


class RateLimitError(NexlaError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self, message: str, retry_after: Optional[int] = None, **kwargs: Any
    ) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ServerError(NexlaError):
    """Raised when server returns 5xx error or any other non-2xx status not mapped above."""

    pass


class NexlaTimeoutError(ServerError):
    """Raised when a request times out. Subclasses ServerError for compatibility."""

    pass


class NexlaConnectionError(ServerError):
    """Raised when the connection fails. Subclasses ServerError for compatibility."""

    pass


class ResourceConflictError(NexlaError):
    """Raised when resource conflicts occur."""

    pass


class CredentialError(NexlaError):
    """Raised when credential validation fails."""

    def __init__(
        self, message: str, credential_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        # Set defaults if not provided
        kwargs.setdefault("operation", "credential_validation")
        kwargs.setdefault("resource_type", "credential")
        if credential_id:
            kwargs.setdefault("resource_id", credential_id)
        super().__init__(message, **kwargs)


class FlowError(NexlaError):
    """Raised when flow operations fail."""

    def __init__(
        self,
        message: str,
        flow_id: Optional[str] = None,
        flow_step: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        # Set defaults if not provided
        kwargs.setdefault("operation", "flow_operation")
        kwargs.setdefault("resource_type", "flow")
        if flow_id:
            kwargs.setdefault("resource_id", flow_id)
        if flow_step:
            kwargs.setdefault("step", flow_step)
        super().__init__(message, **kwargs)


class TransformError(NexlaError):
    """Raised when transform operations fail."""

    def __init__(
        self, message: str, transform_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        # Set defaults if not provided
        kwargs.setdefault("operation", "transform_operation")
        kwargs.setdefault("resource_type", "transform")
        if transform_id:
            kwargs.setdefault("resource_id", transform_id)
        super().__init__(message, **kwargs)


def _message_from_body(body: Any) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """Return (message, error_code, retry_after) from an error body.

    The first matching shape wins. See spec section 5, body shapes 1-6.
    """
    if isinstance(body, str):
        text = body.strip()
        return (text or None, None, None)
    if not isinstance(body, dict):
        return (None, None, None)

    message = body.get("message")
    if isinstance(message, str) and message.strip():
        code = body.get("error_code")
        return (message, code if isinstance(code, str) else None, None)

    error = body.get("error")
    if isinstance(error, dict):
        detail = error.get("detail")
        if isinstance(detail, str) and detail.strip():
            code = error.get("type")
            retry_after = error.get("retry_after")
            return (
                detail,
                code if isinstance(code, str) else None,
                retry_after if isinstance(retry_after, int) else None,
            )
    if isinstance(error, str) and error.strip():
        return (error, None, None)

    detail = body.get("detail")
    if isinstance(detail, str) and detail.strip():
        return (detail, None, None)
    return (None, None, None)


_STATUS_CLASSES: Dict[int, Type[NexlaError]] = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthorizationError,
    404: NotFoundError,
    409: ResourceConflictError,
    422: ValidationError,
    423: AccountLockedError,
    429: RateLimitError,
}


def _header(headers: Optional[Dict[str, Any]], name: str) -> Optional[str]:
    """Case-insensitive header lookup."""
    for key, value in (headers or {}).items():
        if key.lower() == name.lower():
            return cast(str, value)
    return None


def error_from_response(
    status_code: Optional[int],
    body: Any,
    headers: Optional[Dict[str, Any]] = None,
    method: Optional[str] = None,
    url: Optional[str] = None,
    **kwargs: Any,
) -> NexlaError:
    """Build the typed NexlaError for an HTTP error response.

    Args:
        status_code: HTTP status code.
        body: Parsed JSON, trimmed text, or None for an empty body.
        headers: Response headers. ``X-Request-Id`` is read case-insensitively.
        method: HTTP method of the failed request.
        url: Full URL of the failed request.
        **kwargs: Passed to the exception constructor (for example ``operation``).

    Returns:
        A NexlaError subclass chosen by status code. Its message is never empty.
    """
    message, error_code, retry_after = _message_from_body(body)
    if not message:
        try:
            reason = http.HTTPStatus(cast(int, status_code)).phrase
        except (ValueError, TypeError):
            reason = "HTTP error"
        message = f"{status_code} {reason}"

    cls: Type[NexlaError] = _STATUS_CLASSES.get(cast(int, status_code), ServerError)

    if cls is RateLimitError:
        if retry_after is None:
            hdr = _header(headers, "Retry-After")
            if hdr and str(hdr).strip().isdigit():
                retry_after = int(str(hdr).strip())
        kwargs.setdefault("retry_after", retry_after)

    response = body if isinstance(body, dict) else {}
    return cls(
        message,
        status_code=status_code,
        response=response,
        error_code=error_code,
        body=body,
        request_id=_header(headers, "X-Request-Id"),
        method=method,
        url=url,
        **kwargs,
    )
