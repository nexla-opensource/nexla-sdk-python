import re
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Mapping,
    Optional,
    TypeVar,
)

from nexla_sdk.models.base import BaseModel

T = TypeVar("T")

DEFAULT_PAGE_SIZE = 100


class PageInfo(BaseModel):
    """Information about the current page of results."""

    current_page: int
    total_pages: Optional[int] = None
    total_count: Optional[int] = None
    page_size: int = 20

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        if self.total_pages is not None:
            return self.current_page < self.total_pages
        return True  # Assume there might be more if we don't know total

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.current_page > 1


class Page(Generic[T]):
    """A single page of results."""

    def __init__(
        self,
        items: List[T],
        page_info: PageInfo,
        raw_response: Optional[Dict[str, Any]] = None,
        has_next: bool = False,
    ):
        self.items = items
        self.page_info = page_info
        self.raw_response = raw_response
        self.has_next = has_next

    @property
    def page(self) -> int:
        return self.page_info.current_page

    @property
    def per_page(self) -> int:
        return self.page_info.page_size

    @property
    def total_count(self) -> Optional[int]:
        """Total item count from X-Total-Count, or None when the server did not send it."""
        return self.page_info.total_count

    @property
    def total_pages(self) -> Optional[int]:
        """Total page count from X-Total-Page-Count, or None when not sent."""
        return self.page_info.total_pages

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> T:
        return self.items[index]


def _header(headers: Optional[Mapping[str, Any]], name: str) -> Optional[str]:
    """Case-insensitive header lookup."""
    for key, value in (headers or {}).items():
        if str(key).lower() == name.lower():
            return str(value)
    return None


def _int_header(headers: Optional[Mapping[str, Any]], name: str) -> Optional[int]:
    value = _header(headers, name)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


_REL_PATTERN = re.compile(r'rel\s*=\s*(?:"([^"]*)"|([^\s;,]+))', re.IGNORECASE)


def _link_has_next(link: str) -> bool:
    """True when any link in a Link header has rel="next" (case-insensitive)."""
    for match in _REL_PATTERN.finditer(link):
        rels = (match.group(1) or match.group(2) or "").lower().split()
        if "next" in rels:
            return True
    return False


def has_next_page(
    items: List[Any], headers: Optional[Mapping[str, Any]], per_page: int
) -> bool:
    """Decide whether another page exists. Spec section 6 rules, first match wins.

    An empty page always ends the iteration. The Link URL is never followed:
    the caller increments ``page`` on its own base URL.
    """
    if not items:
        return False
    current = _int_header(headers, "X-Current-Page")
    total = _int_header(headers, "X-Total-Page-Count")
    if current is not None and total is not None:
        return current < total
    link = _header(headers, "Link")
    if link is not None:
        return _link_has_next(link)
    return len(items) >= per_page


class Paginator(Generic[T]):
    """Paginator for iterating through pages of results."""

    def __init__(
        self,
        fetch_func: Callable[..., Any],
        page_size: int = DEFAULT_PAGE_SIZE,
        headers_func: Optional[Callable[[], Mapping[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize paginator.

        Args:
            fetch_func: Called as fetch_func(page=, per_page=, **kwargs). Returns the items.
            page_size: Items per page. Sent as per_page on every request.
            headers_func: Called after each fetch. Returns the headers of that response.
            **kwargs: Additional arguments to pass to fetch function
        """
        self.fetch_func = fetch_func
        self.page_size = page_size
        self.headers_func = headers_func
        self.kwargs = kwargs
        self.current_page = 1

    def get_page(self, page_number: int) -> Page[T]:
        """Get a specific page of results."""
        items = list(
            self.fetch_func(page=page_number, per_page=self.page_size, **self.kwargs)
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

    def iter_pages(self) -> Iterator[Page[T]]:
        """Iterate through pages. Empty pages are not yielded."""
        page_number = 1
        while True:
            page = self.get_page(page_number)
            self.current_page = page_number
            if not page.items:
                return
            yield page
            if not page.has_next:
                return
            page_number += 1

    def iter_items(self) -> Iterator[T]:
        """Iterate through all items across all pages."""
        for page in self.iter_pages():
            yield from page.items

    def __iter__(self) -> Iterator[T]:
        return self.iter_items()
