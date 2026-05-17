"""Unit tests for search operations across resources.

This module tests the search() and search_tags() methods available on BaseResource.
These methods allow searching resources using filter criteria and tags respectively.
"""

import pytest

from nexla_sdk.exceptions import NotFoundError, ValidationError
from nexla_sdk.models.sources.responses import Source
from tests.utils import (
    MockDataFactory,
    MockResponseBuilder,
    create_http_error,
    destination_list,
    nexset_list,
    source_list,
)


@pytest.mark.unit
class TestSearchOperation:
    """Tests for the search() method on resources."""

    def test_search_with_simple_filter_returns_results(
        self, mock_client, mock_http_client
    ):
        """Test that search with a simple filter returns matching results."""
        # Arrange
        mock_sources = source_list(count=3)
        mock_http_client.add_response("/data_sources/search", mock_sources)

        filters = {"status": "ACTIVE"}

        # Act
        results = mock_client.sources.search(filters)

        # Assert
        assert len(results) == 3
        mock_http_client.assert_request_made("POST", "/data_sources/search")
        last_request = mock_http_client.get_last_request()
        assert last_request["json"] == filters

    def test_search_with_multiple_filters_and_logic(
        self, mock_client, mock_http_client
    ):
        """Test search with multiple filters uses AND logic."""
        # Arrange
        mock_sources = source_list(count=2)
        mock_http_client.add_response("/data_sources/search", mock_sources)

        filters = {
            "status": "ACTIVE",
            "source_type": "postgres",
            "managed": False,
        }

        # Act
        results = mock_client.sources.search(filters)

        # Assert
        assert len(results) == 2
        mock_http_client.assert_request_made("POST", "/data_sources/search")
        last_request = mock_http_client.get_last_request()
        assert last_request["json"] == filters
        assert last_request["json"]["status"] == "ACTIVE"
        assert last_request["json"]["source_type"] == "postgres"
        assert last_request["json"]["managed"] is False

    def test_search_with_empty_filters_returns_empty(
        self, mock_client, mock_http_client
    ):
        """Test that search with empty filters returns empty list."""
        # Arrange
        mock_http_client.add_response("/data_sources/search", [])

        filters = {}

        # Act
        results = mock_client.sources.search(filters)

        # Assert
        assert results == []
        mock_http_client.assert_request_made("POST", "/data_sources/search")

    def test_search_with_pagination_params(self, mock_client, mock_http_client):
        """Test that search respects pagination parameters."""
        # Arrange
        mock_sources = source_list(count=5)
        mock_http_client.add_response("/data_sources/search", mock_sources)

        filters = {"status": "ACTIVE"}

        # Act
        results = mock_client.sources.search(filters, page=2, per_page=5)

        # Assert
        assert len(results) == 5
        mock_http_client.assert_request_made("POST", "/data_sources/search")
        last_request = mock_http_client.get_last_request()
        assert last_request["params"]["page"] == 2
        assert last_request["params"]["per_page"] == 5

    def test_search_returns_proper_model_objects(self, mock_client, mock_http_client):
        """Test that search returns properly parsed model objects."""
        # Arrange
        factory = MockDataFactory()
        mock_source = factory.create_mock_source(
            id=123,
            name="Test Source",
            status="ACTIVE",
            source_type="postgres",
        )
        mock_http_client.add_response("/data_sources/search", [mock_source])

        filters = {"id": 123}

        # Act
        results = mock_client.sources.search(filters)

        # Assert
        assert len(results) == 1
        assert isinstance(results[0], Source)
        assert results[0].id == 123
        assert results[0].name == "Test Source"
        assert results[0].status == "ACTIVE"

    def test_search_not_found_returns_404(self, mock_client, mock_http_client):
        """Test that search for non-existent resources returns 404."""
        # Arrange
        mock_http_client.add_error(
            "/data_sources/search",
            create_http_error(404, "No resources found"),
        )

        filters = {"id": 99999}

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.sources.search(filters)

    def test_search_validation_error_returns_400(self, mock_client, mock_http_client):
        """Test that search with invalid filters returns 400."""
        # Arrange
        mock_http_client.add_error(
            "/data_sources/search",
            create_http_error(400, "Invalid filter parameters"),
        )

        filters = {"invalid_field": "invalid_value"}

        # Act & Assert
        with pytest.raises(ValidationError):
            mock_client.sources.search(filters)


@pytest.mark.unit
class TestSearchTagsOperation:
    """Tests for the search_tags() method on resources."""

    def test_search_tags_with_single_tag(self, mock_client, mock_http_client):
        """Test search_tags with a single tag returns matching results."""
        # Arrange
        mock_sources = source_list(count=2)
        mock_http_client.add_response("/data_sources/search_tags", mock_sources)

        tags = ["production"]

        # Act
        results = mock_client.sources.search_tags(tags)

        # Assert
        assert len(results) == 2
        mock_http_client.assert_request_made("POST", "/data_sources/search_tags")
        last_request = mock_http_client.get_last_request()
        assert last_request["json"] == tags

    def test_search_tags_with_multiple_tags(self, mock_client, mock_http_client):
        """Test search_tags with multiple tags returns matching results."""
        # Arrange
        mock_sources = source_list(count=3)
        mock_http_client.add_response("/data_sources/search_tags", mock_sources)

        tags = ["production", "analytics", "important"]

        # Act
        results = mock_client.sources.search_tags(tags)

        # Assert
        assert len(results) == 3
        mock_http_client.assert_request_made("POST", "/data_sources/search_tags")
        last_request = mock_http_client.get_last_request()
        assert last_request["json"] == tags
        assert len(last_request["json"]) == 3

    def test_search_tags_with_nonexistent_tag_returns_empty(
        self, mock_client, mock_http_client
    ):
        """Test that search_tags with non-existent tag returns empty list."""
        # Arrange
        mock_http_client.add_response("/data_sources/search_tags", [])

        tags = ["nonexistent-tag-12345"]

        # Act
        results = mock_client.sources.search_tags(tags)

        # Assert
        assert results == []
        mock_http_client.assert_request_made("POST", "/data_sources/search_tags")

    def test_search_tags_with_query_params(self, mock_client, mock_http_client):
        """Test search_tags with additional query parameters."""
        # Arrange
        mock_sources = source_list(count=2)
        mock_http_client.add_response("/data_sources/search_tags", mock_sources)

        tags = ["production"]

        # Act
        results = mock_client.sources.search_tags(tags, page=1, per_page=10)

        # Assert
        assert len(results) == 2
        last_request = mock_http_client.get_last_request()
        assert last_request["params"]["page"] == 1
        assert last_request["params"]["per_page"] == 10


@pytest.mark.unit
class TestSearchAcrossResources:
    """Tests verifying search operations work across different resource types."""

    @pytest.mark.parametrize(
        "resource_name,endpoint,mock_data_func",
        [
            ("sources", "/data_sources", source_list),
            ("destinations", "/data_sinks", destination_list),
            ("nexsets", "/data_sets", nexset_list),
        ],
    )
    def test_search_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint, mock_data_func
    ):
        """Test search works for different resource types."""
        # Arrange
        mock_data = mock_data_func(count=2)
        mock_http_client.add_response(f"{endpoint}/search", mock_data)

        filters = {"status": "ACTIVE"}

        # Act
        resource = getattr(mock_client, resource_name)
        results = resource.search(filters)

        # Assert
        assert len(results) == 2
        mock_http_client.assert_request_made("POST", f"{endpoint}/search")

    @pytest.mark.parametrize(
        "resource_name,endpoint,mock_data_func",
        [
            ("sources", "/data_sources", source_list),
            ("destinations", "/data_sinks", destination_list),
            ("nexsets", "/data_sets", nexset_list),
        ],
    )
    def test_search_tags_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint, mock_data_func
    ):
        """Test search_tags works for different resource types."""
        # Arrange
        mock_data = mock_data_func(count=3)
        mock_http_client.add_response(f"{endpoint}/search_tags", mock_data)

        tags = ["production", "test"]

        # Act
        resource = getattr(mock_client, resource_name)
        results = resource.search_tags(tags)

        # Assert
        assert len(results) == 3
        mock_http_client.assert_request_made("POST", f"{endpoint}/search_tags")
        last_request = mock_http_client.get_last_request()
        assert last_request["json"] == tags


@pytest.mark.unit
class TestSearchResponseBuilder:
    """Tests for the SearchResponseBuilder utility."""

    def test_search_response_with_items(self):
        """Test building search response with items."""
        items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]

        response = MockResponseBuilder.search_response(items=items)

        assert response["data"] == items
        assert response["meta"]["total_count"] == 2
        assert response["meta"]["page"] == 1
        assert response["meta"]["per_page"] == 20

    def test_search_response_with_custom_total(self):
        """Test building search response with custom total count."""
        items = [{"id": 1, "name": "Item 1"}]

        response = MockResponseBuilder.search_response(items=items, total=100)

        assert response["data"] == items
        assert response["meta"]["total_count"] == 100

    def test_search_response_with_pagination(self):
        """Test building search response with pagination params."""
        items = [{"id": 1, "name": "Item 1"}]

        response = MockResponseBuilder.search_response(items=items, page=3, per_page=50)

        assert response["meta"]["page"] == 3
        assert response["meta"]["per_page"] == 50

    def test_search_response_empty(self):
        """Test building empty search response."""
        response = MockResponseBuilder.search_response()

        assert response["data"] == []
        assert response["meta"]["total_count"] == 0
