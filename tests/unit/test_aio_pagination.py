"""Async paginator and async re-entrant lock. No network."""

import asyncio

import pytest

from nexla_sdk.aio._locks import AsyncReentrantLock
from nexla_sdk.aio.pagination import AsyncPaginator

pytestmark = pytest.mark.unit


def _run(coro):
    return asyncio.run(coro)


class FakeList:
    """Stands in for an async list() call. Serves pages by page number."""

    def __init__(self, pages, headers_for=None):
        self.pages = pages
        self.headers_for = headers_for or (lambda page: {})
        self.requests = []
        self.headers = {}

    async def __call__(self, page, per_page, **params):
        self.requests.append({"page": page, "per_page": per_page, **params})
        self.headers = self.headers_for(page)
        return self.pages.get(page, [])


def _collect(paginator):
    async def run():
        return [item async for item in paginator.iter_items()]

    return _run(run())


def test_stops_on_short_page_and_sends_per_page():
    fetch = FakeList({1: [1, 2], 2: [3]})
    paginator = AsyncPaginator(fetch, page_size=2, access_role="owner")

    assert _collect(paginator) == [1, 2, 3]
    assert fetch.requests == [
        {"page": 1, "per_page": 2, "access_role": "owner"},
        {"page": 2, "per_page": 2, "access_role": "owner"},
    ]


def test_x_headers_decide_the_last_page():
    fetch = FakeList(
        {1: [1, 2], 2: [3, 4]},
        headers_for=lambda page: {
            "X-Current-Page": str(page),
            "X-Total-Page-Count": "2",
            "X-Total-Count": "4",
        },
    )
    paginator = AsyncPaginator(fetch, page_size=2, headers_func=lambda: fetch.headers)

    assert _collect(paginator) == [1, 2, 3, 4]
    assert len(fetch.requests) == 2


def test_link_header_next_continues_and_is_case_insensitive():
    def headers(page):
        if page == 1:
            return {"Link": '<https://x/y?page=2>; rel="next"'}
        return {"Link": '<https://x/y?page=1>; rel="prev"'}

    fetch = FakeList({1: [1, 2], 2: [3, 4]}, headers_for=headers)
    paginator = AsyncPaginator(fetch, page_size=2, headers_func=lambda: fetch.headers)

    assert _collect(paginator) == [1, 2, 3, 4]
    assert len(fetch.requests) == 2


def test_empty_page_ends_iteration_and_is_not_yielded():
    fetch = FakeList({1: [1, 2]}, headers_for=lambda page: {"Link": '<x>; rel="next"'})
    paginator = AsyncPaginator(fetch, page_size=2, headers_func=lambda: fetch.headers)

    async def run():
        return [page.page async for page in paginator.iter_pages()]

    assert _run(run()) == [1]
    assert paginator.current_page == 2  # page 2 was fetched and found empty


def test_get_page_reports_totals_from_headers():
    fetch = FakeList(
        {1: [1]},
        headers_for=lambda page: {
            "X-Total-Page-Count": "5",
            "X-Total-Count": "41",
        },
    )
    paginator = AsyncPaginator(fetch, page_size=1, headers_func=lambda: fetch.headers)

    page = _run(paginator.get_page(1))

    assert page.total_pages == 5
    assert page.total_count == 41
    assert page.has_next is True


def test_async_iteration_protocol_yields_items():
    fetch = FakeList({1: ["a"]})
    paginator = AsyncPaginator(fetch, page_size=5)

    async def run():
        return [item async for item in paginator]

    assert _run(run()) == ["a"]


def test_lock_allows_reentry_from_the_owning_task():
    lock = AsyncReentrantLock()

    async def run():
        async with lock:
            async with lock:
                return "nested ok"

    assert _run(run()) == "nested ok"
    assert lock._owner is None and lock._depth == 0


def test_lock_serializes_other_tasks():
    lock = AsyncReentrantLock()
    order = []

    async def worker(name):
        async with lock:
            order.append(f"{name}-in")
            await asyncio.sleep(0)
            order.append(f"{name}-out")

    async def run():
        await asyncio.gather(worker("a"), worker("b"))

    _run(run())
    assert order in (
        ["a-in", "a-out", "b-in", "b-out"],
        ["b-in", "b-out", "a-in", "a-out"],
    )
