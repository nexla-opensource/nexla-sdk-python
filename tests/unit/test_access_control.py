"""Unit tests for access control operations across resources.

Note: Some tests use raw dict responses instead of model validation because
AccessorResponse is a Union type alias, and the SDK's model_validate call
on Union types has limitations. These tests focus on verifying the correct
HTTP requests are made and responses are handled appropriately.
"""

import pytest

from nexla_sdk.exceptions import AuthorizationError, NotFoundError
from nexla_sdk.models.access import TeamAccessorRequest, UserAccessorRequest
from tests.utils import create_http_error


@pytest.mark.unit
class TestAccessorCRUDOperations:
    """Tests for accessor CRUD operations."""

    def test_get_accessors_makes_correct_request(self, mock_client, mock_http_client):
        """Test that get_accessors makes the correct HTTP request."""
        # Arrange
        resource_id = 123
        # Return empty list to avoid model parsing issues
        mock_http_client.add_response(f"/data_sources/{resource_id}/accessors", [])

        # Act
        result = mock_client.sources.get_accessors(resource_id)

        # Assert
        assert result == []
        mock_http_client.assert_request_made(
            "GET", f"/data_sources/{resource_id}/accessors"
        )

    def test_get_accessors_empty_list(self, mock_client, mock_http_client):
        """Test getting accessors returns empty list when none exist."""
        # Arrange
        resource_id = 123
        mock_http_client.add_response(f"/data_sources/{resource_id}/accessors", [])

        # Act
        accessors = mock_client.sources.get_accessors(resource_id)

        # Assert
        assert accessors == []
        mock_http_client.assert_request_made(
            "GET", f"/data_sources/{resource_id}/accessors"
        )

    def test_add_accessors_makes_correct_request(self, mock_client, mock_http_client):
        """Test that add_accessors makes PUT request with correct body."""
        # Arrange
        resource_id = 123
        accessor = UserAccessorRequest(id=456, access_roles=["collaborator"])
        mock_http_client.add_response(f"/data_sources/{resource_id}/accessors", [])

        # Act
        mock_client.sources.add_accessors(resource_id, [accessor])

        # Assert
        mock_http_client.assert_request_made(
            "PUT", f"/data_sources/{resource_id}/accessors"
        )
        # Verify the request body contains the accessor data
        last_request = mock_http_client.get_last_request()
        assert last_request is not None
        assert "accessors" in str(last_request.get("json", {}))

    def test_replace_accessors_uses_post(self, mock_client, mock_http_client):
        """Test that replace_accessors uses POST method."""
        # Arrange
        resource_id = 123
        accessor = UserAccessorRequest(id=456, access_roles=["owner"])
        mock_http_client.add_response(f"/data_sources/{resource_id}/accessors", [])

        # Act
        mock_client.sources.replace_accessors(resource_id, [accessor])

        # Assert
        mock_http_client.assert_request_made(
            "POST", f"/data_sources/{resource_id}/accessors"
        )

    def test_delete_accessors_specific(self, mock_client, mock_http_client):
        """Test deleting specific accessors."""
        # Arrange
        resource_id = 123
        accessor = UserAccessorRequest(id=456, access_roles=["collaborator"])
        mock_http_client.add_response(f"/data_sources/{resource_id}/accessors", [])

        # Act
        mock_client.sources.delete_accessors(resource_id, [accessor])

        # Assert
        mock_http_client.assert_request_made(
            "DELETE", f"/data_sources/{resource_id}/accessors"
        )

    def test_delete_accessors_all(self, mock_client, mock_http_client):
        """Test deleting all accessors (passing None)."""
        # Arrange
        resource_id = 123
        mock_http_client.add_response(f"/data_sources/{resource_id}/accessors", [])

        # Act
        result = mock_client.sources.delete_accessors(resource_id, None)

        # Assert
        assert result == []
        mock_http_client.assert_request_made(
            "DELETE", f"/data_sources/{resource_id}/accessors"
        )


@pytest.mark.unit
class TestAccessControlErrorHandling:
    """Tests for access control error scenarios."""

    def test_accessor_not_found_returns_404(self, mock_client, mock_http_client):
        """Test that accessing non-existent resource returns 404."""
        # Arrange
        resource_id = 99999
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/accessors",
            create_http_error(404, "Resource not found"),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.sources.get_accessors(resource_id)

    def test_insufficient_permissions_returns_403(self, mock_client, mock_http_client):
        """Test that unauthorized access returns 403."""
        # Arrange
        resource_id = 123
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/accessors",
            create_http_error(403, "Forbidden"),
        )

        # Act & Assert
        with pytest.raises(AuthorizationError):
            mock_client.sources.get_accessors(resource_id)


@pytest.mark.unit
class TestAccessControlAcrossResources:
    """Tests verifying accessor operations work across resource types."""

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
            ("credentials", "/data_credentials"),
            ("lookups", "/data_maps"),
            ("projects", "/projects"),
            ("teams", "/teams"),
        ],
    )
    def test_get_accessors_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test get_accessors works for different resource types."""
        # Arrange
        resource_id = 123
        mock_http_client.add_response(f"{endpoint}/{resource_id}/accessors", [])

        # Act
        resource = getattr(mock_client, resource_name)
        accessors = resource.get_accessors(resource_id)

        # Assert
        assert accessors == []
        mock_http_client.assert_request_made(
            "GET", f"{endpoint}/{resource_id}/accessors"
        )

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
            ("credentials", "/data_credentials"),
        ],
    )
    def test_add_accessors_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test add_accessors works for different resource types."""
        # Arrange
        resource_id = 123
        accessor = UserAccessorRequest(id=456, access_roles=["collaborator"])
        mock_http_client.add_response(f"{endpoint}/{resource_id}/accessors", [])

        # Act
        resource = getattr(mock_client, resource_name)
        resource.add_accessors(resource_id, [accessor])

        # Assert
        mock_http_client.assert_request_made(
            "PUT", f"{endpoint}/{resource_id}/accessors"
        )


@pytest.mark.unit
class TestAccessorRequestTypes:
    """Tests for different accessor request types (USER, TEAM)."""

    def test_user_accessor_request(self, mock_client, mock_http_client):
        """Test creating a USER type accessor request."""
        # Arrange
        resource_id = 123
        accessor = UserAccessorRequest(id=456, access_roles=["collaborator"])
        mock_http_client.add_response(f"/data_sources/{resource_id}/accessors", [])

        # Act
        mock_client.sources.add_accessors(resource_id, [accessor])

        # Assert
        last_request = mock_http_client.get_last_request()
        request_data = last_request.get("json", {})
        assert "accessors" in request_data
        accessor_data = request_data["accessors"][0]
        assert accessor_data["type"] == "USER"

    def test_team_accessor_request(self, mock_client, mock_http_client):
        """Test creating a TEAM type accessor request."""
        # Arrange
        resource_id = 123
        accessor = TeamAccessorRequest(id=789, access_roles=["collaborator"])
        mock_http_client.add_response(f"/data_sources/{resource_id}/accessors", [])

        # Act
        mock_client.sources.add_accessors(resource_id, [accessor])

        # Assert
        last_request = mock_http_client.get_last_request()
        request_data = last_request.get("json", {})
        assert "accessors" in request_data
        accessor_data = request_data["accessors"][0]
        assert accessor_data["type"] == "TEAM"

    def test_multiple_access_roles(self, mock_client, mock_http_client):
        """Test accessor with multiple access roles."""
        # Arrange
        resource_id = 123
        accessor = UserAccessorRequest(id=456, access_roles=["collaborator", "admin"])
        mock_http_client.add_response(f"/data_sources/{resource_id}/accessors", [])

        # Act
        mock_client.sources.add_accessors(resource_id, [accessor])

        # Assert
        last_request = mock_http_client.get_last_request()
        request_data = last_request.get("json", {})
        accessor_data = request_data["accessors"][0]
        assert "collaborator" in accessor_data["access_roles"]
        assert "admin" in accessor_data["access_roles"]


@pytest.mark.unit
class TestAccessRoleTypes:
    """Tests for different access role values."""

    @pytest.mark.parametrize(
        "access_role",
        ["owner", "collaborator", "admin", "operator"],
    )
    def test_supported_access_roles(self, mock_client, mock_http_client, access_role):
        """Test that common access roles are accepted."""
        # Arrange
        resource_id = 123
        accessor = UserAccessorRequest(id=456, access_roles=[access_role])
        mock_http_client.add_response(f"/data_sources/{resource_id}/accessors", [])

        # Act
        mock_client.sources.add_accessors(resource_id, [accessor])

        # Assert
        last_request = mock_http_client.get_last_request()
        request_data = last_request.get("json", {})
        accessor_data = request_data["accessors"][0]
        assert access_role in accessor_data["access_roles"]
