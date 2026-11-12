"""
HTTP client interface and implementations for Nexla SDK
"""

import email.utils
import random
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Tuple, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.exceptions import TimeoutError as Urllib3TimeoutError
from urllib3.util.retry import Retry

try:
    from importlib.metadata import version  # Python 3.8+

    _SDK_VERSION = version("nexla-sdk")
except Exception:  # pragma: no cover
    _SDK_VERSION = "unknown"

# Optional OpenTelemetry imports (guarded by availability)
from . import telemetry
from .telemetry import _NoOpTracer

try:  # pragma: no cover - optional dependency
    from opentelemetry.propagate import inject
    from opentelemetry.trace import SpanKind, Status, StatusCode
except Exception:  # pragma: no cover
    SpanKind = None  # type: ignore[assignment,misc]  # OpenTelemetry absent
    Status = None  # type: ignore[assignment,misc]  # OpenTelemetry absent
    StatusCode = None  # type: ignore[assignment,misc]  # OpenTelemetry absent

    def inject(carrier: Dict[str, str]) -> None:  # type: ignore[misc]  # fallback signature
        return None


if TYPE_CHECKING:
    from opentelemetry.trace import Tracer

DEFAULT_TIMEOUT: Tuple[float, float] = (10.0, 60.0)  # (connect, read) seconds
IDEMPOTENT_METHODS: Tuple[str, ...] = ("GET", "HEAD", "OPTIONS", "PUT", "DELETE")
DEFAULT_RETRY_STATUS: Tuple[int, ...] = (502, 503, 504)
BACKOFF_CAP_SECONDS = 8.0
RATE_LIMIT_MAX_WAIT_SECONDS = 60.0


def _as_timeout_pair(value: Any) -> Tuple[float, float]:
    """A single number sets both connect and read. A pair is (connect, read)."""
    if isinstance(value, (int, float)):
        return (float(value), float(value))
    connect, read = value
    return (float(connect), float(read))


def _backoff(attempt: int, backoff_factor: float) -> float:
    """Seconds to wait before retry `attempt` (1-based): min(8, f * 2^(n-1)) plus 0-100 ms."""
    base: float = min(BACKOFF_CAP_SECONDS, backoff_factor * (2 ** (attempt - 1)))
    return base + random.uniform(0, 0.1)


class _SdkRetry(Retry):
    """urllib3 Retry that uses the SDK backoff.

    urllib3 waits 0 s before the first retry. The SDK waits 0.5 s.
    Retry-After is not read here: 429 is handled by RequestsHttpClient.
    """

    def get_backoff_time(self) -> float:
        n = len(self.history)
        return _backoff(n, self.backoff_factor) if n else 0.0


def _rate_limit_wait(response: Any, attempt: int, backoff_factor: float) -> float:
    """Seconds to wait after a 429. First match wins.

    1. body error.retry_after (the backend sends no header)
    2. Retry-After header as seconds
    3. Retry-After header as an HTTP date
    4. exponential backoff
    """
    body = _parse_error_body(response)
    if isinstance(body, dict) and isinstance(body.get("error"), dict):
        retry_after = body["error"].get("retry_after")
        if isinstance(retry_after, (int, float)) and not isinstance(retry_after, bool):
            return float(retry_after)

    header = (response.headers.get("Retry-After") or "").strip()
    if header.isdigit():
        return float(header)
    if header:
        try:
            when = email.utils.parsedate_to_datetime(header)
        except (TypeError, ValueError):
            when = None
        if when is not None:
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())
    return _backoff(attempt, backoff_factor)


class HttpClientInterface(ABC):
    """
    Abstract interface for HTTP clients used by the Nexla SDK.
    This allows for different HTTP client implementations or mocks for testing.
    """

    def request_with_headers(
        self, method: str, url: str, headers: Dict[str, str], **kwargs: Any
    ) -> Tuple[Union[Dict[str, Any], None], Any]:
        """
        Send an HTTP request and also return the response headers.

        The default has no headers. Transports that can read headers
        (RequestsHttpClient) override this method.
        """
        return self.request(method, url, headers, **kwargs), {}

    @abstractmethod
    def request(
        self, method: str, url: str, headers: Dict[str, str], **kwargs: Any
    ) -> Union[Dict[str, Any], None]:
        """
        Send an HTTP request

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Request URL
            headers: Request headers
            **kwargs: Additional arguments for the request

        Returns:
            Response data as dictionary or None for 204 No Content responses

        Raises:
            HttpClientError: If the request fails
        """
        pass


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


def _is_timeout(exc: BaseException) -> bool:
    """True for a requests timeout, or a retry-exhausted urllib3 timeout.

    requests reports exhausted read retries as ConnectionError(MaxRetryError(reason=timeout)).
    """
    if isinstance(exc, requests.exceptions.Timeout):
        return True
    reason = getattr(exc.args[0], "reason", None) if exc.args else None
    return isinstance(reason, Urllib3TimeoutError)


def _parse_error_body(resp: Any) -> Any:
    """Return the JSON body, else the trimmed text, else None when empty."""
    if resp is None or not getattr(resp, "content", None):
        return None
    try:
        return resp.json()
    except ValueError:
        return (resp.text or "").strip() or None


class RequestsHttpClient(HttpClientInterface):
    """HTTP client implementation using the requests library with retries and timeouts.

    Retries (spec section 4):
    - Connect errors: every method.
    - Read errors and 502/503/504: idempotent methods only (``retry_methods``).
    - 429: every method. The wait comes from the body ``error.retry_after``,
      then ``Retry-After``. A wait over 60 s is not retried.
    """

    def __init__(
        self,
        timeout: Union[float, Tuple[float, float]] = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        tracer: Optional[Union["Tracer", _NoOpTracer]] = None,
        retry_methods: Optional[Iterable[str]] = None,
        retry_on_status: Optional[Iterable[int]] = None,
    ):
        self.timeout = _as_timeout_pair(timeout)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_methods = tuple(
            m.upper() for m in (retry_methods or IDEMPOTENT_METHODS)
        )
        self.retry_on_status = tuple(retry_on_status or DEFAULT_RETRY_STATUS)
        self.session = requests.Session()
        self.tracer = tracer if tracer is not None else telemetry.get_tracer(False)

        # Configure retries if available. 429 is owned by _send_with_rate_limit_retries.
        if Retry is not None:
            retry = _SdkRetry(
                total=max_retries,
                backoff_factor=backoff_factor,
                status_forcelist=[s for s in self.retry_on_status if s != 429],
                allowed_methods=frozenset(self.retry_methods),
                raise_on_status=False,
                respect_retry_after_header=False,
            )
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)

    def _send_with_rate_limit_retries(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        timeout: Tuple[float, float],
        kwargs: Dict[str, Any],
    ) -> requests.Response:
        """Send the request. Retry 429 with the server's wait. The body is resent unchanged."""
        attempt = 0
        while True:
            response = self.session.request(
                method, url, headers=headers, timeout=timeout, **kwargs
            )
            if response.status_code != 429 or attempt >= self.max_retries:
                return response
            wait = _rate_limit_wait(response, attempt + 1, self.backoff_factor)
            if wait > RATE_LIMIT_MAX_WAIT_SECONDS:
                return response  # raise_for_status turns this into RateLimitError
            attempt += 1
            time.sleep(wait)

    def request(
        self, method: str, url: str, headers: Dict[str, str], **kwargs: Any
    ) -> Union[Dict[str, Any], None]:
        """Send an HTTP request using a session with sane defaults."""
        body, _ = self.request_with_headers(method, url, headers, **kwargs)
        return body

    def request_with_headers(
        self, method: str, url: str, headers: Dict[str, str], **kwargs: Any
    ) -> Tuple[Union[Dict[str, Any], None], Any]:
        """Send an HTTP request. Return (body, response headers)."""
        span_name = f"Nexla API {method.upper()}"
        kind = (
            SpanKind.CLIENT
            if telemetry._opentelemetry_available and SpanKind is not None
            else None
        )
        # kind is None only without OpenTelemetry, where the no-op tracer is used.
        with self.tracer.start_as_current_span(
            span_name,
            kind=kind,  # type: ignore[arg-type]
        ):
            # We intentionally fetch the current span after creating it to set attributes
            span = None
            try:
                # Get the span from the current context if available (best-effort)
                if (
                    telemetry._opentelemetry_available
                    and hasattr(telemetry, "trace")
                    and telemetry.trace
                ):
                    span = telemetry.trace.get_current_span()
            except Exception:
                span = None

            try:
                timeout = _as_timeout_pair(kwargs.pop("timeout", self.timeout))
                # Default headers
                merged_headers = {
                    "User-Agent": f"nexla-sdk/{_SDK_VERSION}",
                    **(headers or {}),
                }

                # Inject trace context for distributed tracing if OTEL is available
                try:
                    if telemetry._opentelemetry_available and inject is not None:
                        inject(merged_headers)
                except Exception:
                    # Do not fail the request if injection fails
                    pass

                # Set basic attributes
                try:
                    if span and getattr(span, "is_recording", lambda: False)():
                        span.set_attribute("http.method", method.upper())
                        span.set_attribute("url.full", url)
                        try:
                            span.set_attribute("server.address", url.split("/")[2])
                        except Exception:
                            pass
                        span.set_attribute("component", "nexla-sdk")
                except Exception:
                    pass

                response = self._send_with_rate_limit_retries(
                    method, url, merged_headers, timeout, kwargs
                )
                response.raise_for_status()

                # Add response attributes
                try:
                    if span and getattr(span, "is_recording", lambda: False)():
                        span.set_attribute("http.status_code", response.status_code)
                except Exception:
                    pass

                # Return None for 204 No Content or empty responses
                if response.status_code == 204 or not response.content:
                    return None, response.headers

                # Check if response content type indicates JSON
                content_type = response.headers.get("content-type", "").lower()
                if "application/json" in content_type or "text/json" in content_type:
                    return response.json(), response.headers

                # Try to parse as JSON anyway, but handle cases where it's not JSON
                try:
                    return response.json(), response.headers
                except (ValueError, requests.exceptions.JSONDecodeError):
                    # If it's not JSON, return the response as text in a dict
                    return (
                        {
                            "raw_text": response.text,
                            "status_code": response.status_code,
                        },
                        response.headers,
                    )

            except requests.exceptions.HTTPError as e:
                # Record exception on span
                try:
                    if (
                        span
                        and getattr(span, "is_recording", lambda: False)()
                        and telemetry._opentelemetry_available
                        and Status is not None
                        and StatusCode is not None
                    ):
                        span.record_exception(e)
                        span.set_status(Status(status_code=StatusCode.ERROR))
                except Exception:
                    pass

                resp = getattr(e, "response", None)
                body = _parse_error_body(resp)
                raise HttpClientError(
                    message=str(e),
                    status_code=getattr(resp, "status_code", None),
                    response=body if isinstance(body, dict) else {},
                    headers=dict(getattr(resp, "headers", {}) or {}),
                    body=body,
                ) from e

            except requests.exceptions.RequestException as e:
                # Record exception on span
                try:
                    if (
                        span
                        and getattr(span, "is_recording", lambda: False)()
                        and telemetry._opentelemetry_available
                        and Status is not None
                        and StatusCode is not None
                    ):
                        span.record_exception(e)
                        span.set_status(Status(status_code=StatusCode.ERROR))
                except Exception:
                    pass

                # Timeout is checked first: ConnectTimeout is also a ConnectionError.
                if _is_timeout(e):
                    raise HttpTimeoutError(message=str(e)) from e
                if isinstance(e, requests.exceptions.ConnectionError):
                    raise HttpConnectionError(message=str(e)) from e
                raise HttpClientError(message=str(e)) from e
