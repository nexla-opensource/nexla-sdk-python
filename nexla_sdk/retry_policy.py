"""Retry, backoff and timeout decisions shared by the sync and async clients.

Transport-free: no I/O and no HTTP library import. A transport asks these
functions whether to retry and how long to wait (spec sections 3 and 4).
"""

import email.utils
import random
from datetime import datetime, timezone
from typing import Any, Optional, Tuple

from .transport_core import parse_error_body

DEFAULT_TIMEOUT: Tuple[float, float] = (10.0, 60.0)  # (connect, read) seconds
IDEMPOTENT_METHODS: Tuple[str, ...] = ("GET", "HEAD", "OPTIONS", "PUT", "DELETE")
DEFAULT_RETRY_STATUS: Tuple[int, ...] = (502, 503, 504)
BACKOFF_CAP_SECONDS = 8.0
RATE_LIMIT_MAX_WAIT_SECONDS = 60.0


def as_timeout_pair(value: Any) -> Tuple[float, float]:
    """A single number sets both connect and read. A pair is (connect, read)."""
    if isinstance(value, (int, float)):
        return (float(value), float(value))
    connect, read = value
    return (float(connect), float(read))


def backoff_seconds(attempt: int, backoff_factor: float) -> float:
    """Seconds to wait before retry `attempt` (1-based): min(8, f * 2^(n-1)) plus 0-100 ms."""
    base: float = min(BACKOFF_CAP_SECONDS, backoff_factor * (2 ** (attempt - 1)))
    return base + random.uniform(0, 0.1)


def _rate_limit_wait(response: Any, attempt: int, backoff_factor: float) -> float:
    """Seconds to wait after a 429. First match wins.

    1. body error.retry_after (the backend sends no header)
    2. Retry-After header as seconds
    3. Retry-After header as an HTTP date
    4. exponential backoff
    """
    body = parse_error_body(response)
    if isinstance(body, dict) and isinstance(body.get("error"), dict):
        retry_after = body["error"].get("retry_after")
        if isinstance(retry_after, (int, float)) and not isinstance(retry_after, bool):
            return float(retry_after)

    header = (response.headers.get("Retry-After") or "").strip()
    if header.isdigit():
        return float(header)
    if header:
        try:
            when: Optional[datetime] = email.utils.parsedate_to_datetime(header)
        except (TypeError, ValueError):
            when = None
        if when is not None:
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())
    return backoff_seconds(attempt, backoff_factor)


def rate_limit_delay(
    response: Any, attempt: int, backoff_factor: float
) -> Optional[float]:
    """Seconds to wait before retrying a 429, or None when the wait exceeds 60 s.

    None means the caller must not retry. The caller then raises RateLimitError.
    """
    wait = _rate_limit_wait(response, attempt, backoff_factor)
    if wait > RATE_LIMIT_MAX_WAIT_SECONDS:
        return None
    return wait


def status_is_retryable(
    method: str,
    status: int,
    retry_methods: Tuple[str, ...],
    retry_on_status: Tuple[int, ...],
) -> bool:
    """502, 503 and 504 (configurable) are retried for idempotent methods only."""
    return status in retry_on_status and method.upper() in retry_methods


def transport_error_is_retryable(
    method: str, phase: str, retry_methods: Tuple[str, ...]
) -> bool:
    """phase "connect": the request was not sent, so every method is retried.

    phase "after_send": a read timeout or reset after the request was sent. Only
    idempotent methods are retried.
    """
    return phase == "connect" or method.upper() in retry_methods


__all__ = [
    "DEFAULT_TIMEOUT",
    "DEFAULT_RETRY_STATUS",
    "IDEMPOTENT_METHODS",
    "BACKOFF_CAP_SECONDS",
    "RATE_LIMIT_MAX_WAIT_SECONDS",
    "as_timeout_pair",
    "backoff_seconds",
    "rate_limit_delay",
    "status_is_retryable",
    "transport_error_is_retryable",
]
