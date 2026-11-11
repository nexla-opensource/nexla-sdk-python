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


@pytest.mark.unit
class TestPaginatorWithRawFetch:
    """Tests for Paginator using raw fetch functions.

    These tests use a simple fetch function to test Paginator's logic
    independent of the SDK's model parsing.
    """

    def test_paginator_extracts_data_from_paginated_response(self):
        """Test that Paginator extracts items from paginated response format."""

        # Arrange
        def mock_fetch(page=1, per_page=20):
            return {
                "data": [{"id": i} for i in range(per_page)],
                "meta": {
                    "currentPage": page,
                    "totalCount": 100,
                    "pageCount": 5,
                    "perPage": per_page,
                },
            }

        # Act
        paginator = Paginator(fetch_func=mock_fetch, page_size=20)
        page = paginator.get_page(1)

        # Assert
        assert len(page.items) == 20
        assert page.page_info.total_pages == 5
        assert page.page_info.total_count == 100
        assert page.page_info.current_page == 1

    def test_paginator_handles_list_response(self):
        """Test that Paginator handles plain list responses."""

        # Arrange
        def mock_fetch(page=1, per_page=20):
            return [{"id": i} for i in range(10)]

        # Act
        paginator = Paginator(fetch_func=mock_fetch, page_size=20)
        page = paginator.get_page(1)

        # Assert
        assert len(page.items) == 10
        # Without meta, total_pages is unknown
        assert page.page_info.total_pages is None

    def test_iterate_all_items_multiple_pages(self):
        """Test iterating all items across multiple pages."""
        # Arrange
        call_count = 0

        def mock_fetch(page=1, per_page=5):
            nonlocal call_count
            call_count += 1
            if page == 1:
                return [{"id": i} for i in range(5)]  # Full page
            elif page == 2:
                return [{"id": i + 5} for i in range(3)]  # Partial page
            return []

        # Act
        paginator = Paginator(fetch_func=mock_fetch, page_size=5)
        all_items = list(paginator)

        # Assert
        assert len(all_items) == 8
        assert call_count == 2

    def test_iterate_stops_on_empty_page(self):
        """Test that iteration stops when page is empty."""

        # Arrange
        def mock_fetch(page=1, per_page=5):
            if page == 1:
                return [{"id": 1}]
            return []

        # Act
        paginator = Paginator(fetch_func=mock_fetch, page_size=5)
        all_items = list(paginator)

        # Assert
        assert len(all_items) == 1

    def test_iter_pages_yields_page_objects(self):
        """Test iter_pages yields Page objects."""

        # Arrange
        def mock_fetch(page=1, per_page=5):
            if page == 1:
                return [{"id": 1}, {"id": 2}]
            return []

        # Act
        paginator = Paginator(fetch_func=mock_fetch, page_size=5)
        pages = list(paginator.iter_pages())

        # Assert
        assert len(pages) == 1
        assert isinstance(pages[0], Page)
        assert len(pages[0]) == 2


@pytest.mark.unit
class TestPaginationMetadata:
    """Tests for pagination metadata handling."""

    def test_page_extracts_total_pages_from_camel_case_meta(self):
        """Test extracting total pages from camelCase meta keys."""

        # Arrange
        def mock_fetch(page=1, per_page=5):
            return {
                "data": [{"id": i} for i in range(5)],
                "meta": {
                    "currentPage": page,
                    "totalCount": 25,
                    "pageCount": 5,
                    "perPage": per_page,
                },
            }

        # Act
        paginator = Paginator(fetch_func=mock_fetch, page_size=5)
        page = paginator.get_page(2)

        # Assert
        assert page.page_info.total_pages == 5
        assert page.page_info.total_count == 25
        assert page.page_info.current_page == 2

    def test_page_handles_snake_case_meta_keys(self):
        """Test handling of snake_case meta keys."""

        # Arrange
        def mock_fetch(page=1, per_page=5):
            return {
                "data": [{"id": i} for i in range(5)],
                "meta": {
                    "current_page": page,
                    "total_count": 50,
                    "total_pages": 10,
                },
            }

        # Act
        paginator = Paginator(fetch_func=mock_fetch, page_size=5)
        page = paginator.get_page(1)

        # Assert
        assert page.page_info.total_pages == 10
        assert page.page_info.total_count == 50


@pytest.mark.unit
class TestPaginationEdgeCases:
    """Tests for pagination edge cases."""

    def test_empty_results(self):
        """Test handling of empty results."""

        # Arrange
        def mock_fetch(page=1, per_page=20):
            return {
                "data": [],
                "meta": {"currentPage": 1, "totalCount": 0, "pageCount": 0},
            }

        # Act
        paginator = Paginator(fetch_func=mock_fetch, page_size=20)
        page = paginator.get_page(1)

        # Assert
        assert len(page) == 0
        # total_count can be None or 0 depending on API response
        assert page.page_info.total_count in (0, None)

    def test_single_item(self):
        """Test handling of single item results."""

        # Arrange
        def mock_fetch(page=1, per_page=20):
            return {
                "data": [{"id": 1}],
                "meta": {"currentPage": 1, "totalCount": 1, "pageCount": 1},
            }

        # Act
        paginator = Paginator(fetch_func=mock_fetch, page_size=20)
        page = paginator.get_page(1)

        # Assert
        assert len(page) == 1
        assert page.page_info.has_next is False

    def test_has_next_based_on_total_pages(self):
        """Test has_next calculation when total_pages is known."""

        # Arrange
        def mock_fetch(page=1, per_page=5):
            return {
                "data": [{"id": i} for i in range(5)],
                "meta": {"currentPage": page, "pageCount": 3},
            }

        # Act
        paginator = Paginator(fetch_func=mock_fetch, page_size=5)
        page1 = paginator.get_page(1)
        page3 = paginator.get_page(3)

        # Assert
        assert page1.page_info.has_next is True
        assert page3.page_info.has_next is False

    def test_list_response_without_meta(self):
        """Test handling when response is just a list (no meta)."""

        # Arrange
        def mock_fetch(page=1, per_page=20):
            return [{"id": i} for i in range(3)]

        # Act
        paginator = Paginator(fetch_func=mock_fetch, page_size=20)
        page = paginator.get_page(1)

        # Assert
        assert len(page) == 3
        # Without meta, we don't know total pages
        assert page.page_info.total_pages is None
