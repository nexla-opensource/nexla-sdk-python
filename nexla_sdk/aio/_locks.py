"""Re-entrant async lock for the async token handler.

The sync handler uses ``threading.RLock``, which allows nested acquisition:
``ensure_valid_token`` holds the lock and calls ``obtain_session_token``, which
takes it again. ``asyncio.Lock`` does not allow that. This lock records the
owning task and counts nested entries.

The asyncio lock is created on first use. Python 3.8 and 3.9 bind an asyncio
lock to the event loop that exists when it is constructed.
"""

import asyncio
from typing import Optional


class AsyncReentrantLock:
    """Async lock that the owning task may acquire again."""

    def __init__(self) -> None:
        self._lock: Optional[asyncio.Lock] = None
        self._owner: Optional[asyncio.Task[object]] = None
        self._depth = 0

    async def __aenter__(self) -> None:
        task = asyncio.current_task()
        if self._depth and self._owner is task:
            self._depth += 1
            return
        if self._lock is None:
            self._lock = asyncio.Lock()
        await self._lock.acquire()
        self._owner = task
        self._depth = 1

    async def __aexit__(self, *exc_info: object) -> None:
        self._depth -= 1
        if self._depth == 0:
            self._owner = None
            assert self._lock is not None
            self._lock.release()
