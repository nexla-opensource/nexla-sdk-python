"""Catch typed Nexla errors and act on each one.

The SDK retries some failures before it raises. Read operations and token
calls retry on 502, 503, 504, and on 429 (waiting for retry_after). Write
operations do not retry on 5xx, so a failed create or update can be unsafe to
resend. Check the resource before you retry a write.

Usage:
    NEXLA_SERVICE_KEY=... python examples/error_handling.py [source_id]

With no source_id, the example reads a source ID that should not exist, so it
shows the not-found path.
"""

import sys
from typing import Optional

from nexla_sdk import (
    AccountLockedError,
    AuthenticationError,
    AuthorizationError,
    NexlaClient,
    NexlaConnectionError,
    NexlaError,
    NexlaTimeoutError,
    NotFoundError,
    RateLimitError,
    ServerError,
)

MISSING_SOURCE_ID = 999999999


def describe(error: NexlaError) -> str:
    """One line with the fields that support error reports."""
    parts = [f"status={error.status_code}"]
    if error.error_code:
        parts.append(f"error_code={error.error_code}")
    if error.request_id:
        parts.append(f"request_id={error.request_id}")
    return f"{type(error).__name__}: {error.message} ({', '.join(parts)})"


def fetch_source(client: NexlaClient, source_id: int) -> Optional[str]:
    """Return the source name, or None after printing why it failed."""
    # Order matters: a subclass must come before its base class.
    # AccountLockedError is an AuthenticationError. NexlaTimeoutError and
    # NexlaConnectionError are ServerErrors.
    try:
        return client.sources.get(source_id).name
    except NotFoundError:
        print(f"Source {source_id} does not exist.")
    except AccountLockedError as error:
        print(f"The account is locked. Wait for the lock to clear. {describe(error)}")
    except AuthenticationError as error:
        print(f"Credentials were rejected. Check the service key. {describe(error)}")
    except AuthorizationError as error:
        print(f"This credential cannot read source {source_id}. {describe(error)}")
    except RateLimitError as error:
        print(
            f"Rate limited. The SDK waited and gave up. Retry after {error.retry_after}s."
        )
    except NexlaTimeoutError:
        print("The request timed out. Raise timeout or check network latency.")
    except NexlaConnectionError:
        print("Cannot reach the API. Check NEXLA_API_URL and network access.")
    except ServerError as error:
        print(f"Server error. Retry later or contact support. {describe(error)}")
    except NexlaError as error:
        print(f"Request failed. {describe(error)}")
    return None


def main() -> int:
    if len(sys.argv) > 1:
        source_id = int(sys.argv[1])
    else:
        source_id = MISSING_SOURCE_ID

    try:
        client = NexlaClient(timeout=(5, 30), max_retries=2)
    except NexlaError as error:
        print(f"Client setup failed: {error}", file=sys.stderr)
        return 1

    name = fetch_source(client, source_id)
    if name is not None:
        print(f"Source {source_id}: {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
