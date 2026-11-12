"""Unit tests for pagination functionality."""

import pytest

from nexla_sdk.utils.pagination import Page, PageInfo, Paginator
from tests.utils import MockResponseBuilder


@pytest.mark.unit
class TestPageInfo:
    """Tests for PageInfo model."""

    def test_page_info_has_next_when_more_pages(self):
        """Test has_next returns True when there are more pages."""
        # Arrange
        page_info = PageInfo(current_page=1, total_pages=5, page_size=20)

        # Assert
        assert page_info.has_next is True

    def test_page_info_has_next_false_on_last_page(self):
        """Test has_next returns False when on last page."""
        # Arrange
        page_info = PageInfo(current_page=5, total_pages=5, page_size=20)

        # Assert
        assert page_info.has_next is False

    def test_page_info_has_next_unknown_total(self):
        """Test has_next returns True when total_pages is unknown."""
        # Arrange
        page_info = PageInfo(current_page=1, total_pages=None, page_size=20)

        # Assert
        assert page_info.has_next is True

    def test_page_info_has_previous_on_page_2(self):
        """Test has_previous returns True when not on first page."""
        # Arrange
        page_info = PageInfo(current_page=2, total_pages=5, page_size=20)

        # Assert
        assert page_info.has_previous is True

    def test_page_info_has_previous_false_on_page_1(self):
        """Test has_previous returns False when on first page."""
        # Arrange
        page_info = PageInfo(current_page=1, total_pages=5, page_size=20)

        # Assert
        assert page_info.has_previous is False


@pytest.mark.unit
class TestPage:
    """Tests for Page class."""

    def test_page_iteration(self):
        """Test that Page can be iterated."""
        # Arrange
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        page_info = PageInfo(current_page=1, page_size=20)
        page = Page(items=items, page_info=page_info)

        # Act
        iterated = list(page)

        # Assert
        assert iterated == items

    def test_page_length(self):
        """Test that Page has correct length."""
        # Arrange
        items = [{"id": 1}, {"id": 2}]
        page_info = PageInfo(current_page=1, page_size=20)
        page = Page(items=items, page_info=page_info)

        # Assert
        assert len(page) == 2

    def test_page_indexing(self):
        """Test that Page supports indexing."""
        # Arrange
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        page_info = PageInfo(current_page=1, page_size=20)
        page = Page(items=items, page_info=page_info)

        # Assert
        assert page[0] == {"id": 1}
        assert page[2] == {"id": 3}


@pytest.mark.unit
class TestPaginatorBasics:
    """Tests for basic Paginator functionality."""

    def test_paginator_initialization(self, mock_client):
        """Test that paginator can be initialized."""
        # Act
        paginator = mock_client.sources.paginate(per_page=10)

        # Assert
        assert paginator.page_size == 10

    def test_paginator_passes_page_params(self, mock_client, mock_http_client):
        """Test that paginator passes page and per_page to list()."""
        # Arrange - return a simple list (the SDK's list() parses the response)
        sources = [MockResponseBuilder.source() for _ in range(5)]
        mock_http_client.add_response("/data_sources", sources)

        # Act
        paginator = mock_client.sources.paginate(per_page=5)
        page = paginator.get_page(1)

        # Assert
        assert len(page.items) == 5
        mock_http_client.assert_request_made("GET", "/data_sources")


class _FakeFeed:
    """Serves (items, headers) per page. headers_func returns the last fetch's headers."""

    def __init__(self, pages):
        self.pages = pages
        self.requests = []
        self.headers = {}

    def fetch(self, page, per_page):
        self.requests.append((page, per_page))
        items, self.headers = self.pages.get(page, ([], {}))
        return list(items)

    def headers_func(self):
        return self.headers

    def paginator(self, per_page=2):
        return Paginator(
            fetch_func=self.fetch, page_size=per_page, headers_func=self.headers_func
        )


@pytest.mark.unit
class TestPaginatorFollowsHeaders:
    """Next-page rules from spec section 6 (first match wins)."""

    def test_link_next_continues_and_link_without_next_stops(self):
        feed = _FakeFeed(
            {
                1: ([1, 2], {"Link": '<https://x/data_sources?page=2>; rel="Next"'}),
                2: (
                    [3, 4],
                    {"Link": '<https://x/data_sources?page=1>; rel="Previous"'},
                ),
            }
        )
        items = list(feed.paginator().iter_items())
        assert items == [1, 2, 3, 4]
        assert feed.requests == [(1, 2), (2, 2)]

    def test_current_page_at_total_stops_even_on_full_page(self):
        common = {"X-Total-Page-Count": "3", "X-Total-Count": "6"}
        feed = _FakeFeed(
            {
                1: ([1, 2], {**common, "X-Current-Page": "1"}),
                2: ([3, 4], {**common, "X-Current-Page": "2"}),
                3: ([5, 6], {**common, "X-Current-Page": "3"}),
            }
        )
        items = list(feed.paginator().iter_items())
        assert items == [1, 2, 3, 4, 5, 6]
        assert feed.requests == [(1, 2), (2, 2), (3, 2)]

    def test_no_headers_full_page_continues_and_short_page_stops(self):
        feed = _FakeFeed({1: ([1, 2], {}), 2: ([3], {})})
        assert list(feed.paginator().iter_items()) == [1, 2, 3]
        assert feed.requests == [(1, 2), (2, 2)]

    def test_empty_page_stops_even_when_link_says_next(self):
        feed = _FakeFeed({1: ([], {"Link": '<x>; rel="Next"'}), 2: ([9], {})})
        assert list(feed.paginator().iter_items()) == []
        assert feed.requests == [(1, 2)]

    def test_link_rel_is_case_insensitive(self):
        feed = _FakeFeed({1: ([1, 2], {"Link": '<x>; rel="next"'}), 2: ([3], {})})
        assert list(feed.paginator().iter_items()) == [1, 2, 3]

    def test_link_with_several_relations_matches_next(self):
        feed = _FakeFeed(
            {
                1: ([1, 2], {"Link": '<a>; rel="Previous", <b>; rel="Next"'}),
                2: ([3], {}),
            }
        )
        assert list(feed.paginator().iter_items()) == [1, 2, 3]

    def test_pages_expose_page_metadata_from_headers(self):
        feed = _FakeFeed(
            {
                1: (
                    [1, 2],
                    {
                        "X-Current-Page": "1",
                        "X-Total-Page-Count": "2",
                        "X-Total-Count": "3",
                    },
                ),
                2: (
                    [3],
                    {
                        "X-Current-Page": "2",
                        "X-Total-Page-Count": "2",
                        "X-Total-Count": "3",
                    },
                ),
            }
        )
        pages = list(feed.paginator().iter_pages())
        assert [p.page for p in pages] == [1, 2]
        assert all(p.per_page == 2 for p in pages)
        assert pages[0].total_count == 3
        assert pages[0].total_pages == 2
        assert len(pages[1]) == 1


@pytest.mark.unit
class TestPaginateThroughClient:
    """paginate() uses the real list() path and the headers of each response."""

    def test_paginate_follows_x_headers_and_sends_explicit_per_page(
        self, mock_client, mock_http_client
    ):
        common = {"X-Total-Page-Count": "2", "X-Total-Count": "3"}
        mock_http_client.add_paged_response(
            "/data_sources",
            [
                (
                    [
                        MockResponseBuilder.source(source_id=1),
                        MockResponseBuilder.source(source_id=2),
                    ],
                    {**common, "X-Current-Page": "1"},
                ),
                (
                    [MockResponseBuilder.source(source_id=3)],
                    {**common, "X-Current-Page": "2"},
                ),
            ],
        )

        ids = [s.id for s in mock_client.sources.paginate(per_page=2).iter_items()]

        assert ids == [1, 2, 3]
        sent = mock_http_client.get_requests_by_url_pattern("/data_sources")
        assert [(r["params"]["page"], r["params"]["per_page"]) for r in sent] == [
            (1, 2),
            (2, 2),
        ]

    def test_paginate_default_per_page_is_100(self, mock_client, mock_http_client):
        mock_http_client.add_response("/data_sources", [])

        assert list(mock_client.sources.paginate()) == []

        req = mock_http_client.get_last_request()
        assert req["params"]["per_page"] == 100

    def test_paginate_does_not_follow_link_url(self, mock_client, mock_http_client):
        mock_http_client.add_paged_response(
            "/data_sources",
            [
                (
                    [
                        MockResponseBuilder.source(source_id=1),
                        MockResponseBuilder.source(source_id=2),
                    ],
                    {
                        "Link": '<https://evil.example/data_sources?page=7&per_page=2>; rel="Next"'
                    },
                ),
                ([], {}),
            ],
        )

        list(mock_client.sources.paginate(per_page=2).iter_items())

        sent = mock_http_client.get_requests_by_url_pattern("/data_sources")
        assert [r["params"]["page"] for r in sent] == [1, 2]
        assert all("evil.example" not in r["url"] for r in sent)

    def test_client_exposes_last_response_headers(self, mock_client, mock_http_client):
        mock_http_client.add_headers("/data_sources", {"X-Total-Count": "7"})
        mock_http_client.add_response("/data_sources", [])

        mock_client.sources.list()

        assert mock_client.last_response_headers["X-Total-Count"] == "7"

    def test_request_still_returns_body_only(self, mock_client, mock_http_client):
        mock_http_client.add_headers("/data_sources/1", {"X-Total-Count": "7"})
        mock_http_client.add_response("/data_sources/1", {"id": 1})

        assert mock_client.request("GET", "/data_sources/1") == {"id": 1}


@pytest.mark.unit
class TestPaginatorPlainFetch:
    """Paginator with a plain fetch function and no headers (short-page rule)."""

    def test_plain_list_response_has_unknown_total(self):
        def mock_fetch(page=1, per_page=20):
            return [{"id": i} for i in range(10)]

        page = Paginator(fetch_func=mock_fetch, page_size=20).get_page(1)

        assert len(page.items) == 10
        assert page.total_pages is None
        assert page.total_count is None

    def test_iterate_all_items_multiple_pages(self):
        call_count = 0

        def mock_fetch(page=1, per_page=5):
            nonlocal call_count
            call_count += 1
            if page == 1:
                return [{"id": i} for i in range(5)]
            if page == 2:
                return [{"id": i + 5} for i in range(3)]
            return []

        all_items = list(Paginator(fetch_func=mock_fetch, page_size=5))

        assert len(all_items) == 8
        assert call_count == 2

    def test_iterate_stops_on_empty_page(self):
        def mock_fetch(page=1, per_page=5):
            return [{"id": 1}] if page == 1 else []

        assert len(list(Paginator(fetch_func=mock_fetch, page_size=5))) == 1

    def test_iter_pages_yields_page_objects(self):
        def mock_fetch(page=1, per_page=5):
            return [{"id": 1}, {"id": 2}] if page == 1 else []

        pages = list(Paginator(fetch_func=mock_fetch, page_size=5).iter_pages())

        assert len(pages) == 1
        assert isinstance(pages[0], Page)
        assert len(pages[0]) == 2
