"""Unit tests for access insights operations across resources.

Tests cover:
- get_access_insights: Explain why the current user can access a resource
- get_users_access_insights: Get access insights for all users with access to a resource
- list_accessible: List resources accessible to the current user
"""

import pytest

from nexla_sdk.exceptions import AuthorizationError, NotFoundError
from tests.utils import MockResponseBuilder, create_http_error


@pytest.mark.unit
class TestGetAccessInsights:
    """Tests for get_access_insights operation."""

    def test_get_access_insights_returns_rules_list(
        self, mock_client, mock_http_client
    ):
        """Test that get_access_insights returns access insights payload."""
        # Arrange
        resource_id = 123
        access_insights_response = MockResponseBuilder.access_insights_response(
            resource_id=resource_id,
            access_granted=True,
            access_reason="owner",
            access_path=[{"type": "direct", "role": "owner"}],
        )
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/access", access_insights_response
        )

        # Act
        result = mock_client.sources.get_access_insights(resource_id)

        # Assert
        assert result["access_granted"] is True
        assert result["access_reason"] == "owner"
        assert result["resource_id"] == resource_id
        mock_http_client.assert_request_made(
            "GET", f"/data_sources/{resource_id}/access"
        )

    def test_get_access_insights_with_accessor_user_id_parameter(
        self, mock_client, mock_http_client
    ):
        """Test get_access_insights with accessor_user_id query parameter."""
        # Arrange
        resource_id = 123
        accessor_user_id = 456
        access_insights_response = MockResponseBuilder.access_insights_response(
            resource_id=resource_id,
            access_granted=True,
            access_reason="collaborator",
        )
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/access", access_insights_response
        )

        # Act
        result = mock_client.sources.get_access_insights(
            resource_id, accessor_user_id=accessor_user_id
        )

        # Assert
        assert result["access_granted"] is True
        mock_http_client.assert_request_made(
            "GET", f"/data_sources/{resource_id}/access"
        )
        # Verify the query parameter was passed
        last_request = mock_http_client.get_last_request()
        assert last_request is not None
        params = last_request.get("params", {})
        assert params.get("accessor_user_id") == accessor_user_id

    def test_get_access_insights_owner_rule_present(
        self, mock_client, mock_http_client
    ):
        """Test that access insights correctly identifies owner access."""
        # Arrange
        resource_id = 123
        access_insights_response = MockResponseBuilder.access_insights_response(
            resource_id=resource_id,
            access_granted=True,
            access_reason="owner",
            access_path=[
                {"type": "direct", "role": "owner"},
            ],
        )
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/access", access_insights_response
        )

        # Act
        result = mock_client.sources.get_access_insights(resource_id)

        # Assert
        assert result["access_granted"] is True
        assert result["access_reason"] == "owner"
        assert len(result["access_path"]) > 0
        assert result["access_path"][0]["role"] == "owner"
        assert result["access_path"][0]["type"] == "direct"

    def test_get_access_insights_team_member_access(
        self, mock_client, mock_http_client
    ):
        """Test access insights for team member access path."""
        # Arrange
        resource_id = 123
        access_insights_response = {
            "access_granted": True,
            "access_reason": "team_member",
            "access_path": [
                {
                    "type": "team",
                    "role": "collaborator",
                    "team_id": 789,
                    "team_name": "Engineering Team",
                }
            ],
            "resource_id": resource_id,
            "resource_type": "data_source",
        }
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/access", access_insights_response
        )

        # Act
        result = mock_client.sources.get_access_insights(resource_id)

        # Assert
        assert result["access_granted"] is True
        assert result["access_reason"] == "team_member"
        assert result["access_path"][0]["type"] == "team"
        assert result["access_path"][0]["team_id"] == 789


@pytest.mark.unit
class TestGetUsersAccessInsights:
    """Tests for get_users_access_insights operation."""

    def test_get_users_access_insights_returns_user_access_list(
        self, mock_client, mock_http_client
    ):
        """Test that get_users_access_insights returns user access list."""
        # Arrange
        resource_id = 123
        users_access_response = {
            "users": [
                {
                    "user_id": 1,
                    "email": "owner@example.com",
                    "full_name": "Owner User",
                    "access_roles": ["owner"],
                    "access_type": "direct",
                },
                {
                    "user_id": 2,
                    "email": "collab@example.com",
                    "full_name": "Collaborator User",
                    "access_roles": ["collaborator"],
                    "access_type": "direct",
                },
                {
                    "user_id": 3,
                    "email": "team@example.com",
                    "full_name": "Team Member",
                    "access_roles": ["collaborator"],
                    "access_type": "team",
                    "team_id": 789,
                },
            ],
            "resource_id": resource_id,
        }
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/users_access_insights", users_access_response
        )

        # Act
        result = mock_client.sources.get_users_access_insights(resource_id)

        # Assert
        assert "users" in result
        assert len(result["users"]) == 3
        assert result["resource_id"] == resource_id
        mock_http_client.assert_request_made(
            "GET", f"/data_sources/{resource_id}/users_access_insights"
        )

    def test_get_users_access_insights_empty_list(self, mock_client, mock_http_client):
        """Test get_users_access_insights when no users have access."""
        # Arrange
        resource_id = 123
        users_access_response = {
            "users": [],
            "resource_id": resource_id,
        }
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/users_access_insights", users_access_response
        )

        # Act
        result = mock_client.sources.get_users_access_insights(resource_id)

        # Assert
        assert result["users"] == []
        mock_http_client.assert_request_made(
            "GET", f"/data_sources/{resource_id}/users_access_insights"
        )


@pytest.mark.unit
class TestListAccessible:
    """Tests for list_accessible operation."""

    def test_list_accessible_returns_accessible_resources(
        self, mock_client, mock_http_client
    ):
        """Test that list_accessible returns list of accessible resources."""
        # Arrange
        accessible_sources = [
            MockResponseBuilder.source(source_id=1, name="Source 1"),
            MockResponseBuilder.source(source_id=2, name="Source 2"),
            MockResponseBuilder.source(source_id=3, name="Source 3"),
        ]
        mock_http_client.add_response("/data_sources/accessible", accessible_sources)

        # Act
        result = mock_client.sources.list_accessible()

        # Assert
        assert len(result) == 3
        mock_http_client.assert_request_made("GET", "/data_sources/accessible")

    def test_list_accessible_returns_empty_when_no_access(
        self, mock_client, mock_http_client
    ):
        """Test list_accessible returns empty list when user has no access."""
        # Arrange
        mock_http_client.add_response("/data_sources/accessible", [])

        # Act
        result = mock_client.sources.list_accessible()

        # Assert
        assert result == []
        mock_http_client.assert_request_made("GET", "/data_sources/accessible")

    def test_list_accessible_with_query_params(self, mock_client, mock_http_client):
        """Test list_accessible passes additional query parameters."""
        # Arrange
        accessible_sources = [MockResponseBuilder.source(source_id=1)]
        mock_http_client.add_response("/data_sources/accessible", accessible_sources)

        # Act
        result = mock_client.sources.list_accessible(include_metrics=True)

        # Assert
        assert len(result) == 1
        mock_http_client.assert_request_made("GET", "/data_sources/accessible")
        last_request = mock_http_client.get_last_request()
        params = last_request.get("params", {})
        assert params.get("include_metrics") is True


@pytest.mark.unit
class TestAccessInsightsErrorHandling:
    """Tests for access insights error scenarios."""

    def test_access_insights_not_found_returns_404(self, mock_client, mock_http_client):
        """Test that accessing non-existent resource returns 404."""
        # Arrange
        resource_id = 99999
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/access",
            create_http_error(404, "Resource not found"),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.sources.get_access_insights(resource_id)

    def test_access_insights_permission_denied_returns_403(
        self, mock_client, mock_http_client
    ):
        """Test that unauthorized access returns 403."""
        # Arrange
        resource_id = 123
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/access",
            create_http_error(403, "Forbidden - insufficient permissions"),
        )

        # Act & Assert
        with pytest.raises(AuthorizationError):
            mock_client.sources.get_access_insights(resource_id)

    def test_users_access_insights_not_found(self, mock_client, mock_http_client):
        """Test users_access_insights for non-existent resource."""
        # Arrange
        resource_id = 99999
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/users_access_insights",
            create_http_error(404, "Resource not found"),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.sources.get_users_access_insights(resource_id)

    def test_users_access_insights_permission_denied(
        self, mock_client, mock_http_client
    ):
        """Test users_access_insights returns 403 for unauthorized access."""
        # Arrange
        resource_id = 123
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/users_access_insights",
            create_http_error(403, "Forbidden - owner access required"),
        )

        # Act & Assert
        with pytest.raises(AuthorizationError):
            mock_client.sources.get_users_access_insights(resource_id)


@pytest.mark.unit
class TestAccessInsightsAcrossResources:
    """Tests verifying access insights operations work across resource types."""

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
            ("credentials", "/data_credentials"),
            ("lookups", "/data_maps"),
            ("projects", "/projects"),
        ],
    )
    def test_get_access_insights_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test get_access_insights works for different resource types."""
        # Arrange
        resource_id = 123
        access_insights_response = MockResponseBuilder.access_insights_response(
            resource_id=resource_id
        )
        mock_http_client.add_response(
            f"{endpoint}/{resource_id}/access", access_insights_response
        )

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.get_access_insights(resource_id)

        # Assert
        assert result["access_granted"] is True
        mock_http_client.assert_request_made("GET", f"{endpoint}/{resource_id}/access")

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
        ],
    )
    def test_get_users_access_insights_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test get_users_access_insights works for different resource types."""
        # Arrange
        resource_id = 123
        users_access_response = {
            "users": [
                {
                    "user_id": 1,
                    "email": "user@example.com",
                    "access_roles": ["owner"],
                }
            ],
            "resource_id": resource_id,
        }
        mock_http_client.add_response(
            f"{endpoint}/{resource_id}/users_access_insights", users_access_response
        )

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.get_users_access_insights(resource_id)

        # Assert
        assert "users" in result
        mock_http_client.assert_request_made(
            "GET", f"{endpoint}/{resource_id}/users_access_insights"
        )

    @pytest.mark.parametrize(
        "resource_name,endpoint,builder_method",
        [
            ("sources", "/data_sources", "source"),
            ("destinations", "/data_sinks", "destination"),
            ("nexsets", "/data_sets", "nexset"),
        ],
    )
    def test_list_accessible_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint, builder_method
    ):
        """Test list_accessible works for different resource types."""
        # Arrange
        builder_func = getattr(MockResponseBuilder, builder_method)
        accessible_resources = [builder_func() for _ in range(2)]
        mock_http_client.add_response(f"{endpoint}/accessible", accessible_resources)

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.list_accessible()

        # Assert
        assert len(result) == 2
        mock_http_client.assert_request_made("GET", f"{endpoint}/accessible")
