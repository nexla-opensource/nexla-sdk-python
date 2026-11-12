"""Async paginator. Page rules and page types come from nexla_sdk.utils.pagination."""

from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Generic,
    Mapping,
    Optional,
    TypeVar,
)

from nexla_sdk.utils.pagination import (
    DEFAULT_PAGE_SIZE,
    Page,
    PageInfo,
    _int_header,
    has_next_page,
)

T = TypeVar("T")


class AsyncPaginator(Generic[T]):
    """Iterate pages of an async list call. Stops by the same rules as Paginator."""

    def __init__(
        self,
        fetch_func: Callable[..., Awaitable[Any]],
        page_size: int = DEFAULT_PAGE_SIZE,
        headers_func: Optional[Callable[[], Mapping[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize paginator.

        Args:
            fetch_func: Awaited as fetch_func(page=, per_page=, **kwargs). Returns the items.
            page_size: Items per page. Sent as per_page on every request.
            headers_func: Called after each fetch. Returns the headers of that response.
            **kwargs: Additional arguments to pass to fetch function
        """
        self.fetch_func = fetch_func
        self.page_size = page_size
        self.headers_func = headers_func
        self.kwargs = kwargs
        self.current_page = 1

    async def get_page(self, page_number: int) -> Page[T]:
        """Fetch one page of results."""
        items = list(
            (
                await self.fetch_func(
                    page=page_number, per_page=self.page_size, **self.kwargs
                )
            )
            or []
        )
        headers = self.headers_func() if self.headers_func else {}
        page_info = PageInfo(
            current_page=page_number,
            page_size=self.page_size,
            total_pages=_int_header(headers, "X-Total-Page-Count"),
            total_count=_int_header(headers, "X-Total-Count"),
        )
        return Page(
            items=items,
            page_info=page_info,
            has_next=has_next_page(items, headers, self.page_size),
        )

    async def iter_pages(self) -> AsyncIterator[Page[T]]:
        """Iterate through pages. Empty pages are not yielded."""
        page_number = 1
        while True:
            page = await self.get_page(page_number)
            self.current_page = page_number
            if not page.items:
                return
            yield page
            if not page.has_next:
                return
            page_number += 1

    async def iter_items(self) -> AsyncIterator[T]:
        """Iterate through all items across all pages."""
        async for page in self.iter_pages():
            for item in page.items:
                yield item

    def __aiter__(self) -> AsyncIterator[T]:
        return self.iter_items()
