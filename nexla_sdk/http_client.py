"""
HTTP client interface and implementations for Nexla SDK
"""

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Tuple, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.exceptions import NewConnectionError
from urllib3.exceptions import TimeoutError as Urllib3TimeoutError
from urllib3.util.retry import Retry

# Optional OpenTelemetry imports (guarded by availability)
from . import telemetry
from .retry_policy import (
    DEFAULT_RETRY_STATUS,
    DEFAULT_TIMEOUT,
    IDEMPOTENT_METHODS,
    as_timeout_pair,
    backoff_seconds,
    rate_limit_delay,
)
from .telemetry import _NoOpTracer
from .transport_core import (
    HttpClientError,
    HttpConnectionError,
    HttpTimeoutError,
    build_headers,
    http_error_from,
    parse_error_body,
    parse_success_body,
)

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


class _SdkRetry(Retry):
    """urllib3 Retry that uses the SDK backoff.

    urllib3 waits 0 s before the first retry. The SDK waits 0.5 s.
    Retry-After is not read here: 429 is handled by RequestsHttpClient.
    """

    def get_backoff_time(self) -> float:
        n = len(self.history)
        return backoff_seconds(n, self.backoff_factor) if n else 0.0


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


def _is_timeout(exc: BaseException) -> bool:
    """True for a requests timeout, or a retry-exhausted urllib3 timeout.

    requests reports exhausted read retries as ConnectionError(MaxRetryError(reason=timeout)).
    """
    if isinstance(exc, requests.exceptions.Timeout):
        return True
    reason = getattr(exc.args[0], "reason", None) if exc.args else None
    # A refused connection or DNS failure is a NewConnectionError, which urllib3
    # also derives from its TimeoutError. It is a connection failure, not a timeout.
    return isinstance(reason, Urllib3TimeoutError) and not isinstance(
        reason, NewConnectionError
    )


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
        self.timeout = as_timeout_pair(timeout)
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
            wait = rate_limit_delay(response, attempt + 1, self.backoff_factor)
            if wait is None:
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
                timeout = as_timeout_pair(kwargs.pop("timeout", self.timeout))
                # Default headers
                merged_headers = build_headers(headers)

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

                return parse_success_body(response), response.headers

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
                body = parse_error_body(resp)
                raise http_error_from(
                    getattr(resp, "status_code", None),
                    body,
                    getattr(resp, "headers", {}),
                    str(e),
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
