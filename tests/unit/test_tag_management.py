"""Unit tests for tag management operations across resources.

Tests cover:
- get_tags: Retrieve tags for a resource
- set_tags: Replace all tags (POST)
- add_tags: Merge tags with existing (PUT)
- remove_tags: Delete specific tags (DELETE)
"""

import pytest

from nexla_sdk.exceptions import AuthorizationError, NotFoundError
from tests.utils import create_http_error


@pytest.mark.unit
class TestGetTags:
    """Tests for retrieving tags from resources."""

    def test_get_tags_returns_list(self, mock_client, mock_http_client):
        """Test that get_tags returns a list of tags."""
        # Arrange
        resource_id = 123
        expected_tags = ["production", "critical", "data-pipeline"]
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/tags", expected_tags
        )

        # Act
        result = mock_client.sources.get_tags(resource_id)

        # Assert
        assert result == expected_tags
        assert isinstance(result, list)
        assert len(result) == 3
        mock_http_client.assert_request_made("GET", f"/data_sources/{resource_id}/tags")

    def test_get_tags_empty_list(self, mock_client, mock_http_client):
        """Test get_tags returns empty list when no tags exist."""
        # Arrange
        resource_id = 123
        mock_http_client.add_response(f"/data_sources/{resource_id}/tags", [])

        # Act
        result = mock_client.sources.get_tags(resource_id)

        # Assert
        assert result == []
        assert isinstance(result, list)
        mock_http_client.assert_request_made("GET", f"/data_sources/{resource_id}/tags")

    def test_get_tags_single_tag(self, mock_client, mock_http_client):
        """Test get_tags with a single tag."""
        # Arrange
        resource_id = 456
        expected_tags = ["environment:staging"]
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/tags", expected_tags
        )

        # Act
        result = mock_client.sources.get_tags(resource_id)

        # Assert
        assert result == expected_tags
        assert len(result) == 1


@pytest.mark.unit
class TestSetTags:
    """Tests for replacing all tags on a resource."""

    def test_set_tags_success(self, mock_client, mock_http_client):
        """Test that set_tags replaces all tags."""
        # Arrange
        resource_id = 123
        new_tags = ["new-tag-1", "new-tag-2"]
        mock_http_client.add_response(f"/data_sources/{resource_id}/tags", new_tags)

        # Act
        result = mock_client.sources.set_tags(resource_id, new_tags)

        # Assert
        assert result == new_tags
        mock_http_client.assert_request_made(
            "POST", f"/data_sources/{resource_id}/tags"
        )
        # Verify the request body contains the tags
        last_request = mock_http_client.get_last_request()
        assert last_request is not None
        assert last_request.get("json") == new_tags

    def test_set_tags_with_empty_list_clears_all(self, mock_client, mock_http_client):
        """Test that set_tags with empty list clears all tags."""
        # Arrange
        resource_id = 123
        mock_http_client.add_response(f"/data_sources/{resource_id}/tags", [])

        # Act
        result = mock_client.sources.set_tags(resource_id, [])

        # Assert
        assert result == []
        mock_http_client.assert_request_made(
            "POST", f"/data_sources/{resource_id}/tags"
        )
        last_request = mock_http_client.get_last_request()
        assert last_request.get("json") == []

    def test_set_tags_replaces_existing(self, mock_client, mock_http_client):
        """Test that set_tags completely replaces existing tags."""
        # Arrange
        resource_id = 789
        # Simulate replacing ["old-tag"] with ["completely", "new", "tags"]
        new_tags = ["completely", "new", "tags"]
        mock_http_client.add_response(f"/data_sinks/{resource_id}/tags", new_tags)

        # Act
        result = mock_client.destinations.set_tags(resource_id, new_tags)

        # Assert
        assert result == new_tags
        assert "completely" in result
        mock_http_client.assert_request_made("POST", f"/data_sinks/{resource_id}/tags")


@pytest.mark.unit
class TestAddTags:
    """Tests for adding/merging tags to a resource."""

    def test_add_tags_success(self, mock_client, mock_http_client):
        """Test that add_tags merges with existing tags."""
        # Arrange
        resource_id = 123
        tags_to_add = ["new-tag"]
        # Simulated merged response (existing + new)
        merged_tags = ["existing-tag", "new-tag"]
        mock_http_client.add_response(f"/data_sources/{resource_id}/tags", merged_tags)

        # Act
        result = mock_client.sources.add_tags(resource_id, tags_to_add)

        # Assert
        assert result == merged_tags
        mock_http_client.assert_request_made("PUT", f"/data_sources/{resource_id}/tags")
        last_request = mock_http_client.get_last_request()
        assert last_request.get("json") == tags_to_add

    def test_add_tags_with_duplicate_tags_idempotent(
        self, mock_client, mock_http_client
    ):
        """Test that add_tags with duplicate tags is idempotent."""
        # Arrange
        resource_id = 123
        # Adding a tag that already exists
        tags_to_add = ["existing-tag"]
        # Response shows same tags (no duplicates created)
        existing_tags = ["existing-tag", "another-tag"]
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/tags", existing_tags
        )

        # Act
        result = mock_client.sources.add_tags(resource_id, tags_to_add)

        # Assert
        assert result == existing_tags
        # Verify no duplicate "existing-tag" in result
        assert result.count("existing-tag") == 1
        mock_http_client.assert_request_made("PUT", f"/data_sources/{resource_id}/tags")

    def test_add_multiple_tags(self, mock_client, mock_http_client):
        """Test adding multiple tags at once."""
        # Arrange
        resource_id = 456
        tags_to_add = ["tag-1", "tag-2", "tag-3"]
        merged_tags = ["original", "tag-1", "tag-2", "tag-3"]
        mock_http_client.add_response(f"/data_sets/{resource_id}/tags", merged_tags)

        # Act
        result = mock_client.nexsets.add_tags(resource_id, tags_to_add)

        # Assert
        assert result == merged_tags
        assert all(tag in result for tag in tags_to_add)
        mock_http_client.assert_request_made("PUT", f"/data_sets/{resource_id}/tags")


@pytest.mark.unit
class TestRemoveTags:
    """Tests for removing tags from a resource."""

    def test_remove_tags_success(self, mock_client, mock_http_client):
        """Test that remove_tags deletes specific tags."""
        # Arrange
        resource_id = 123
        tags_to_remove = ["tag-to-remove"]
        # Remaining tags after removal
        remaining_tags = ["kept-tag-1", "kept-tag-2"]
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/tags", remaining_tags
        )

        # Act
        result = mock_client.sources.remove_tags(resource_id, tags_to_remove)

        # Assert
        assert result == remaining_tags
        assert "tag-to-remove" not in result
        mock_http_client.assert_request_made(
            "DELETE", f"/data_sources/{resource_id}/tags"
        )
        last_request = mock_http_client.get_last_request()
        assert last_request.get("json") == tags_to_remove

    def test_remove_multiple_tags(self, mock_client, mock_http_client):
        """Test removing multiple tags at once."""
        # Arrange
        resource_id = 789
        tags_to_remove = ["remove-1", "remove-2"]
        remaining_tags = ["keeper"]
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/tags", remaining_tags
        )

        # Act
        result = mock_client.sources.remove_tags(resource_id, tags_to_remove)

        # Assert
        assert result == remaining_tags
        mock_http_client.assert_request_made(
            "DELETE", f"/data_sources/{resource_id}/tags"
        )

    def test_remove_all_tags_leaves_empty(self, mock_client, mock_http_client):
        """Test removing all tags leaves empty list."""
        # Arrange
        resource_id = 123
        tags_to_remove = ["only-tag"]
        mock_http_client.add_response(f"/data_sources/{resource_id}/tags", [])

        # Act
        result = mock_client.sources.remove_tags(resource_id, tags_to_remove)

        # Assert
        assert result == []
        mock_http_client.assert_request_made(
            "DELETE", f"/data_sources/{resource_id}/tags"
        )

    def test_remove_nonexistent_tags_no_error(self, mock_client, mock_http_client):
        """Test that removing non-existent tags does not raise an error."""
        # Arrange
        resource_id = 123
        tags_to_remove = ["nonexistent-tag"]
        existing_tags = ["existing-tag"]
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/tags", existing_tags
        )

        # Act
        result = mock_client.sources.remove_tags(resource_id, tags_to_remove)

        # Assert
        assert result == existing_tags
        mock_http_client.assert_request_made(
            "DELETE", f"/data_sources/{resource_id}/tags"
        )


@pytest.mark.unit
class TestTagErrorHandling:
    """Tests for tag operation error scenarios."""

    def test_tags_not_found_returns_404(self, mock_client, mock_http_client):
        """Test that accessing tags on non-existent resource returns 404."""
        # Arrange
        resource_id = 99999
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/tags",
            create_http_error(404, "Resource not found"),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.sources.get_tags(resource_id)

    def test_tags_permission_denied_returns_403(self, mock_client, mock_http_client):
        """Test that unauthorized access to tags returns 403."""
        # Arrange
        resource_id = 123
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/tags",
            create_http_error(403, "Forbidden"),
        )

        # Act & Assert
        with pytest.raises(AuthorizationError):
            mock_client.sources.get_tags(resource_id)

    def test_set_tags_not_found(self, mock_client, mock_http_client):
        """Test set_tags on non-existent resource raises NotFoundError."""
        # Arrange
        resource_id = 99999
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/tags",
            create_http_error(404, "Resource not found"),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.sources.set_tags(resource_id, ["tag"])

    def test_add_tags_permission_denied(self, mock_client, mock_http_client):
        """Test add_tags with insufficient permissions raises AuthorizationError."""
        # Arrange
        resource_id = 123
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/tags",
            create_http_error(403, "Insufficient permissions to modify tags"),
        )

        # Act & Assert
        with pytest.raises(AuthorizationError):
            mock_client.sources.add_tags(resource_id, ["new-tag"])

    def test_remove_tags_not_found(self, mock_client, mock_http_client):
        """Test remove_tags on non-existent resource raises NotFoundError."""
        # Arrange
        resource_id = 99999
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/tags",
            create_http_error(404, "Resource not found"),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.sources.remove_tags(resource_id, ["tag"])


@pytest.mark.unit
class TestTagsAcrossResources:
    """Tests verifying tag operations work across different resource types."""

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
            ("credentials", "/data_credentials"),
        ],
    )
    def test_get_tags_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test get_tags works across different resource types."""
        # Arrange
        resource_id = 123
        expected_tags = ["resource-tag", "type-specific"]
        mock_http_client.add_response(f"{endpoint}/{resource_id}/tags", expected_tags)

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.get_tags(resource_id)

        # Assert
        assert result == expected_tags
        mock_http_client.assert_request_made("GET", f"{endpoint}/{resource_id}/tags")

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
            ("credentials", "/data_credentials"),
        ],
    )
    def test_set_tags_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test set_tags works across different resource types."""
        # Arrange
        resource_id = 456
        new_tags = ["replaced-tag"]
        mock_http_client.add_response(f"{endpoint}/{resource_id}/tags", new_tags)

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.set_tags(resource_id, new_tags)

        # Assert
        assert result == new_tags
        mock_http_client.assert_request_made("POST", f"{endpoint}/{resource_id}/tags")

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
            ("credentials", "/data_credentials"),
        ],
    )
    def test_add_tags_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test add_tags works across different resource types."""
        # Arrange
        resource_id = 789
        tags_to_add = ["added-tag"]
        merged_tags = ["existing", "added-tag"]
        mock_http_client.add_response(f"{endpoint}/{resource_id}/tags", merged_tags)

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.add_tags(resource_id, tags_to_add)

        # Assert
        assert result == merged_tags
        mock_http_client.assert_request_made("PUT", f"{endpoint}/{resource_id}/tags")

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
            ("credentials", "/data_credentials"),
        ],
    )
    def test_remove_tags_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test remove_tags works across different resource types."""
        # Arrange
        resource_id = 321
        tags_to_remove = ["to-remove"]
        remaining_tags = ["remaining"]
        mock_http_client.add_response(f"{endpoint}/{resource_id}/tags", remaining_tags)

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.remove_tags(resource_id, tags_to_remove)

        # Assert
        assert result == remaining_tags
        mock_http_client.assert_request_made("DELETE", f"{endpoint}/{resource_id}/tags")


@pytest.mark.unit
class TestTagFormats:
    """Tests for various tag format scenarios."""

    def test_tags_with_special_characters(self, mock_client, mock_http_client):
        """Test tags containing special characters."""
        # Arrange
        resource_id = 123
        special_tags = ["env:production", "team/data-eng", "version_2.0"]
        mock_http_client.add_response(f"/data_sources/{resource_id}/tags", special_tags)

        # Act
        result = mock_client.sources.get_tags(resource_id)

        # Assert
        assert result == special_tags
        assert "env:production" in result

    def test_tags_with_unicode(self, mock_client, mock_http_client):
        """Test tags containing unicode characters."""
        # Arrange
        resource_id = 123
        unicode_tags = ["categoria-datos", "equipo-analisis"]
        mock_http_client.add_response(f"/data_sources/{resource_id}/tags", unicode_tags)

        # Act
        result = mock_client.sources.get_tags(resource_id)

        # Assert
        assert result == unicode_tags

    def test_tags_case_sensitivity(self, mock_client, mock_http_client):
        """Test that tags preserve case sensitivity."""
        # Arrange
        resource_id = 123
        case_sensitive_tags = ["Production", "CRITICAL", "lowercased"]
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/tags", case_sensitive_tags
        )

        # Act
        result = mock_client.sources.get_tags(resource_id)

        # Assert
        assert result == case_sensitive_tags
        assert "Production" in result
        assert "CRITICAL" in result
        assert "lowercased" in result
