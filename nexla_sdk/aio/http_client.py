"""Async HTTP transport for the Nexla SDK, built on httpx.

Install the extra to use it: ``pip install "nexla-sdk[async]"``.

The retry decisions come from ``nexla_sdk.retry_policy``. Errors and response
parsing come from ``nexla_sdk.transport_core``, the same code the sync client uses.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Tuple, Union

try:
    import httpx
except ImportError as exc:  # pragma: no cover - the guard is tested in a subprocess
    raise ImportError(
        "nexla_sdk.aio needs httpx. Install the async extra: "
        'pip install "nexla-sdk[async]"'
    ) from exc

from nexla_sdk import telemetry
from nexla_sdk.retry_policy import (
    DEFAULT_RETRY_STATUS,
    DEFAULT_TIMEOUT,
    IDEMPOTENT_METHODS,
    as_timeout_pair,
    backoff_seconds,
    rate_limit_delay,
    status_is_retryable,
    transport_error_is_retryable,
)
from nexla_sdk.transport_core import (
    HttpClientError,
    HttpConnectionError,
    HttpTimeoutError,
    build_headers,
    http_error_from,
    parse_error_body,
    parse_success_body,
)

if TYPE_CHECKING:
    from opentelemetry.trace import Tracer

    from nexla_sdk.telemetry import _NoOpTracer


class AsyncHttpClientInterface(ABC):
    """Abstract async HTTP client used by the async client and token handler."""

    async def request_with_headers(
        self, method: str, url: str, headers: Dict[str, str], **kwargs: Any
    ) -> Tuple[Union[Dict[str, Any], None], Any]:
        """Send a request and return (body, response headers)."""
        return await self.request(method, url, headers, **kwargs), {}

    @abstractmethod
    async def request(
        self, method: str, url: str, headers: Dict[str, str], **kwargs: Any
    ) -> Union[Dict[str, Any], None]:
        """Send a request. Return the body, or None for 204 No Content."""
        ...

    async def aclose(self) -> None:
        """Release transport resources. A no-op unless overridden."""
        return None


# Request not sent: safe to retry for every method.
_CONNECT_ERRORS = (httpx.ConnectTimeout, httpx.ConnectError, httpx.PoolTimeout)


def _transport_failure(exc: httpx.TransportError, url: str) -> HttpClientError:
    """Map an httpx transport failure to the shared HTTP client error types."""
    if isinstance(exc, httpx.TimeoutException):
        return HttpTimeoutError(message=f"{exc} ({url})")
    if isinstance(
        exc, (httpx.NetworkError, httpx.ProxyError, httpx.RemoteProtocolError)
    ):
        return HttpConnectionError(message=f"{exc} ({url})")
    return HttpClientError(message=f"{exc} ({url})")


class AsyncHttpxClient(AsyncHttpClientInterface):
    """Async HTTP client with the SDK retry rules (spec sections 3 and 4).

    - Connect failures: every method.
    - Read timeouts and resets after send, and 502/503/504: idempotent methods only.
    - 429: every method. The wait comes from the body ``error.retry_after``,
      then ``Retry-After``. A wait over 60 s is not retried.

    Retries use ``asyncio.sleep``. The request body is resent unchanged.
    """

    def __init__(
        self,
        timeout: Union[float, Tuple[float, float]] = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        retry_methods: Optional[Iterable[str]] = None,
        retry_on_status: Optional[Iterable[int]] = None,
        tracer: Optional[Union["Tracer", "_NoOpTracer"]] = None,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        self.timeout = as_timeout_pair(timeout)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_methods = tuple(
            m.upper() for m in (retry_methods or IDEMPOTENT_METHODS)
        )
        self.retry_on_status = tuple(retry_on_status or DEFAULT_RETRY_STATUS)
        self.tracer = tracer if tracer is not None else telemetry.get_tracer(False)
        self._client = httpx.AsyncClient(transport=transport, follow_redirects=True)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def request(
        self, method: str, url: str, headers: Dict[str, str], **kwargs: Any
    ) -> Union[Dict[str, Any], None]:
        body, _ = await self.request_with_headers(method, url, headers, **kwargs)
        return body

    async def request_with_headers(
        self, method: str, url: str, headers: Dict[str, str], **kwargs: Any
    ) -> Tuple[Union[Dict[str, Any], None], Any]:
        connect, read = as_timeout_pair(kwargs.pop("timeout", self.timeout))
        timeout = httpx.Timeout(connect=connect, read=read, write=read, pool=connect)
        merged_headers = build_headers(headers)
        with self.tracer.start_as_current_span(f"Nexla API {method.upper()}"):
            response = await self._send(method, url, merged_headers, timeout, kwargs)
        if response.status_code >= 400:
            body = parse_error_body(response)
            raise http_error_from(
                response.status_code,
                body,
                response.headers,
                f"HTTP {response.status_code} for {method.upper()} {url}",
            )
        return parse_success_body(response), response.headers

    async def _send(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        timeout: httpx.Timeout,
        kwargs: Dict[str, Any],
    ) -> httpx.Response:
        """Send with retries. Returns the final response, or raises a transport error.

        ``retries`` counts transport and status retries together. It drives the
        backoff, as urllib3's Retry does in the sync client. 429 has its own count.
        """
        retries = 0
        rate_limit_retries = 0
        while True:
            try:
                response = await self._client.request(
                    method, url, headers=headers, timeout=timeout, **kwargs
                )
            except httpx.TransportError as exc:
                phase = "connect" if isinstance(exc, _CONNECT_ERRORS) else "after_send"
                if retries < self.max_retries and transport_error_is_retryable(
                    method, phase, self.retry_methods
                ):
                    retries += 1
                    await asyncio.sleep(backoff_seconds(retries, self.backoff_factor))
                    continue
                raise _transport_failure(exc, url) from exc

            if response.status_code == 429:
                if rate_limit_retries < self.max_retries:
                    delay = rate_limit_delay(
                        response, rate_limit_retries + 1, self.backoff_factor
                    )
                    if delay is not None:
                        rate_limit_retries += 1
                        await asyncio.sleep(delay)
                        continue
                return response  # the caller raises RateLimitError

            if retries < self.max_retries and status_is_retryable(
                method, response.status_code, self.retry_methods, self.retry_on_status
            ):
                retries += 1
                await asyncio.sleep(backoff_seconds(retries, self.backoff_factor))
                continue
            return response
