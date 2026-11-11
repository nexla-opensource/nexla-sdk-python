"""Unit tests for documentation operations across resources.

Tests for get_docs, set_docs, add_docs, and remove_docs operations
provided by BaseResource for managing resource documentation.
"""

import pytest

from nexla_sdk.exceptions import AuthorizationError, NotFoundError
from tests.utils import MockResponseBuilder, create_http_error


@pytest.mark.unit
class TestGetDocs:
    """Tests for get_docs operation."""

    def test_get_docs_returns_doc_entries(self, mock_client, mock_http_client):
        """Test that get_docs returns documentation entries for a resource."""
        # Arrange
        resource_id = 123
        docs_response = MockResponseBuilder.docs_response()
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/docs", docs_response
        )

        # Act
        result = mock_client.sources.get_docs(resource_id)

        # Assert
        assert result == docs_response
        assert "entries" in result
        assert len(result["entries"]) > 0
        mock_http_client.assert_request_made("GET", f"/data_sources/{resource_id}/docs")

    def test_get_docs_empty_by_default(self, mock_client, mock_http_client):
        """Test getting docs returns empty when no docs exist."""
        # Arrange
        resource_id = 123
        empty_docs = {"entries": []}
        mock_http_client.add_response(f"/data_sources/{resource_id}/docs", empty_docs)

        # Act
        result = mock_client.sources.get_docs(resource_id)

        # Assert
        assert result == empty_docs
        assert result["entries"] == []
        mock_http_client.assert_request_made("GET", f"/data_sources/{resource_id}/docs")


@pytest.mark.unit
class TestSetDocs:
    """Tests for set_docs operation (replaces all docs)."""

    def test_set_docs_replaces_all_docs(self, mock_client, mock_http_client):
        """Test that set_docs replaces all documentation entries."""
        # Arrange
        resource_id = 123
        new_docs = [
            {"key": "description", "value": "New description"},
            {"key": "usage", "value": "New usage instructions"},
        ]
        expected_response = {"entries": new_docs}
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/docs", expected_response
        )

        # Act
        result = mock_client.sources.set_docs(resource_id, new_docs)

        # Assert
        assert result == expected_response
        mock_http_client.assert_request_made(
            "POST", f"/data_sources/{resource_id}/docs"
        )
        # Verify the request body contains the new docs
        last_request = mock_http_client.get_last_request()
        assert last_request is not None
        assert last_request.get("json") == new_docs

    def test_set_docs_with_empty_list_clears_docs(self, mock_client, mock_http_client):
        """Test that set_docs with empty list clears all docs."""
        # Arrange
        resource_id = 123
        empty_docs = []
        expected_response = {"entries": []}
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/docs", expected_response
        )

        # Act
        result = mock_client.sources.set_docs(resource_id, empty_docs)

        # Assert
        assert result == expected_response
        mock_http_client.assert_request_made(
            "POST", f"/data_sources/{resource_id}/docs"
        )


@pytest.mark.unit
class TestAddDocs:
    """Tests for add_docs operation (merges docs)."""

    def test_add_docs_merges_entries(self, mock_client, mock_http_client):
        """Test that add_docs merges new documentation entries."""
        # Arrange
        resource_id = 123
        docs_to_add = [
            {"key": "new_section", "value": "New section content"},
        ]
        merged_response = {
            "entries": [
                {"key": "existing", "value": "Existing content"},
                {"key": "new_section", "value": "New section content"},
            ]
        }
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/docs", merged_response
        )

        # Act
        result = mock_client.sources.add_docs(resource_id, docs_to_add)

        # Assert
        assert result == merged_response
        mock_http_client.assert_request_made("PUT", f"/data_sources/{resource_id}/docs")
        # Verify the request body contains the docs to add
        last_request = mock_http_client.get_last_request()
        assert last_request is not None
        assert last_request.get("json") == docs_to_add

    def test_add_multiple_docs(self, mock_client, mock_http_client):
        """Test adding multiple documentation entries at once."""
        # Arrange
        resource_id = 123
        docs_to_add = [
            {"key": "overview", "value": "Overview content"},
            {"key": "setup", "value": "Setup instructions"},
            {"key": "examples", "value": "Example usage"},
        ]
        merged_response = {"entries": docs_to_add}
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/docs", merged_response
        )

        # Act
        result = mock_client.sources.add_docs(resource_id, docs_to_add)

        # Assert
        assert result == merged_response
        assert len(result["entries"]) == 3
        mock_http_client.assert_request_made("PUT", f"/data_sources/{resource_id}/docs")
        # Verify all docs were sent
        last_request = mock_http_client.get_last_request()
        assert len(last_request.get("json", [])) == 3


@pytest.mark.unit
class TestRemoveDocs:
    """Tests for remove_docs operation."""

    def test_remove_docs_deletes_specific_entries(self, mock_client, mock_http_client):
        """Test that remove_docs removes specific documentation entries."""
        # Arrange
        resource_id = 123
        docs_to_remove = [
            {"key": "obsolete_section", "value": "To be removed"},
        ]
        remaining_response = {
            "entries": [
                {"key": "remaining", "value": "Still here"},
            ]
        }
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/docs", remaining_response
        )

        # Act
        result = mock_client.sources.remove_docs(resource_id, docs_to_remove)

        # Assert
        assert result == remaining_response
        mock_http_client.assert_request_made(
            "DELETE", f"/data_sources/{resource_id}/docs"
        )
        # Verify the request body contains the docs to remove
        last_request = mock_http_client.get_last_request()
        assert last_request is not None
        assert last_request.get("json") == docs_to_remove

    def test_remove_docs_with_none_sends_empty_list(
        self, mock_client, mock_http_client
    ):
        """Test that remove_docs with None sends empty list."""
        # Arrange
        resource_id = 123
        empty_response = {"entries": []}
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/docs", empty_response
        )

        # Act
        result = mock_client.sources.remove_docs(resource_id, None)

        # Assert
        assert result == empty_response
        mock_http_client.assert_request_made(
            "DELETE", f"/data_sources/{resource_id}/docs"
        )
        # Verify empty list was sent
        last_request = mock_http_client.get_last_request()
        assert last_request.get("json") == []


@pytest.mark.unit
class TestDocsErrorHandling:
    """Tests for error handling in docs operations."""

    def test_docs_not_found_returns_404(self, mock_client, mock_http_client):
        """Test that accessing docs for non-existent resource returns 404."""
        # Arrange
        resource_id = 99999
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/docs",
            create_http_error(404, "Resource not found"),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.sources.get_docs(resource_id)

    def test_docs_permission_denied_returns_403(self, mock_client, mock_http_client):
        """Test that unauthorized docs access returns 403."""
        # Arrange
        resource_id = 123
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/docs",
            create_http_error(403, "Forbidden"),
        )

        # Act & Assert
        with pytest.raises(AuthorizationError):
            mock_client.sources.get_docs(resource_id)

    def test_set_docs_permission_denied(self, mock_client, mock_http_client):
        """Test that unauthorized set_docs access returns 403."""
        # Arrange
        resource_id = 123
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/docs",
            create_http_error(403, "Forbidden"),
        )

        # Act & Assert
        with pytest.raises(AuthorizationError):
            mock_client.sources.set_docs(
                resource_id, [{"key": "test", "value": "data"}]
            )


@pytest.mark.unit
class TestDocsAcrossResources:
    """Tests verifying docs operations work across resource types."""

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
        ],
    )
    def test_get_docs_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test get_docs works for different resource types."""
        # Arrange
        resource_id = 123
        docs_response = MockResponseBuilder.docs_response()
        mock_http_client.add_response(f"{endpoint}/{resource_id}/docs", docs_response)

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.get_docs(resource_id)

        # Assert
        assert result == docs_response
        mock_http_client.assert_request_made("GET", f"{endpoint}/{resource_id}/docs")

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
        ],
    )
    def test_set_docs_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test set_docs works for different resource types."""
        # Arrange
        resource_id = 123
        new_docs = [{"key": "test", "value": "Test documentation"}]
        expected_response = {"entries": new_docs}
        mock_http_client.add_response(
            f"{endpoint}/{resource_id}/docs", expected_response
        )

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.set_docs(resource_id, new_docs)

        # Assert
        assert result == expected_response
        mock_http_client.assert_request_made("POST", f"{endpoint}/{resource_id}/docs")

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
        ],
    )
    def test_add_docs_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test add_docs works for different resource types."""
        # Arrange
        resource_id = 123
        docs_to_add = [{"key": "additional", "value": "Additional documentation"}]
        expected_response = {"entries": docs_to_add}
        mock_http_client.add_response(
            f"{endpoint}/{resource_id}/docs", expected_response
        )

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.add_docs(resource_id, docs_to_add)

        # Assert
        assert result == expected_response
        mock_http_client.assert_request_made("PUT", f"{endpoint}/{resource_id}/docs")

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
        ],
    )
    def test_remove_docs_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test remove_docs works for different resource types."""
        # Arrange
        resource_id = 123
        docs_to_remove = [{"key": "obsolete", "value": "Obsolete documentation"}]
        expected_response = {"entries": []}
        mock_http_client.add_response(
            f"{endpoint}/{resource_id}/docs", expected_response
        )

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.remove_docs(resource_id, docs_to_remove)

        # Assert
        assert result == expected_response
        mock_http_client.assert_request_made("DELETE", f"{endpoint}/{resource_id}/docs")
