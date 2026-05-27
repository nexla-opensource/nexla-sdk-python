"""Unit tests for UsersResource."""

import pytest

from nexla_sdk.exceptions import NotFoundError, ServerError, ValidationError
from nexla_sdk.http_client import HttpClientError
from nexla_sdk.models.users.requests import UserCreate, UserUpdate
from nexla_sdk.models.users.responses import User, UserExpanded, UserSettings
from tests.utils.assertions import NexlaAssertions
from tests.utils.mock_builders import MockResponseBuilder


class TestUsersUnitTests:
    """Unit tests for UsersResource."""

    def test_list_users_success(self, mock_client):
        """Test successful listing of users."""
        client = mock_client
        user_data = MockResponseBuilder.user()
        user_data["id"] = 123
        client.http_client.add_response("/users", [user_data])

        users = client.users.list()

        assert len(users) == 1
        assert isinstance(users[0], User)
        NexlaAssertions.assert_user_response(users[0], user_data)
        client.http_client.assert_request_made("GET", "/users")

    def test_list_users_with_access_role_all(self, mock_client):
        """Test listing all users with access_role=all parameter."""
        client = mock_client
        user_data1 = MockResponseBuilder.user()
        user_data1["id"] = 123
        user_data2 = MockResponseBuilder.user()
        user_data2["id"] = 124
        user_data = [user_data1, user_data2]
        client.http_client.add_response("/users", user_data)

        users = client.users.list(access_role="all")

        assert len(users) == 2
        client.http_client.assert_request_made(
            "GET", "/users", params={"access_role": "all"}
        )

    def test_list_users_with_expand(self, mock_client):
        """Test listing users with expand parameter."""
        client = mock_client
        user_data = MockResponseBuilder.user()
        user_data["id"] = 123
        client.http_client.add_response("/users?expand=1", [user_data])

        users = client.users.list(expand=True)

        assert len(users) == 1
        assert isinstance(users[0], UserExpanded)

    def test_list_users_with_pagination(self, mock_client):
        """Test listing users with pagination parameters."""
        client = mock_client
        user_data = MockResponseBuilder.user()
        user_data["id"] = 123
        client.http_client.add_response("/users", [user_data])

        client.users.list(page=2, per_page=50)

        client.http_client.assert_request_made(
            "GET", "/users", params={"page": 2, "per_page": 50}
        )

    def test_get_user_success(self, mock_client):
        """Test successful getting of a user."""
        client = mock_client
        user_data = MockResponseBuilder.user()
        user_data["id"] = 123
        client.http_client.add_response("/users/123", user_data)

        user = client.users.get(123)

        assert isinstance(user, User)
        NexlaAssertions.assert_user_response(user, user_data)
        client.http_client.assert_request_made("GET", "/users/123")

    def test_get_user_with_expand(self, mock_client):
        """Test getting a user with expand parameter."""
        client = mock_client
        user_data = MockResponseBuilder.user()
        user_data["id"] = 123
        client.http_client.add_response("/users/123?expand=1", user_data)

        user = client.users.get(123, expand=True)

        assert isinstance(user, UserExpanded)

    def test_get_user_not_found(self, mock_client):
        """Test getting a non-existent user."""
        client = mock_client
        client.http_client.add_error(
            "/users/999",
            HttpClientError(
                "Not found", status_code=404, response={"message": "User not found"}
            ),
        )

        with pytest.raises(NotFoundError):
            client.users.get(999)

    def test_create_user_success(self, mock_client):
        """Test successful creation of a user."""
        client = mock_client
        request_data = UserCreate(full_name="Test User", email="test@example.com")
        response_data = MockResponseBuilder.user()
        response_data.update(
            {"id": 123, "full_name": "Test User", "email": "test@example.com"}
        )
        client.http_client.add_response("/users", response_data)

        user = client.users.create(request_data)

        assert isinstance(user, User)
        assert user.full_name == "Test User"
        assert user.email == "test@example.com"
        client.http_client.assert_request_made("POST", "/users")

    def test_create_user_validation_error(self, mock_client):
        """Test user creation with validation error."""
        client = mock_client
        request_data = UserCreate(full_name="Test User", email="invalid-email")
        client.http_client.add_error(
            "/users",
            HttpClientError(
                "Validation failed",
                status_code=400,
                response={"message": "Invalid email format"},
            ),
        )

        with pytest.raises(ValidationError):
            client.users.create(request_data)

    def test_update_user_success(self, mock_client):
        """Test successful updating of a user."""
        client = mock_client
        request_data = UserUpdate(name="Updated User")
        response_data = MockResponseBuilder.user()
        response_data.update({"id": 123, "full_name": "Updated User"})
        client.http_client.add_response("/users/123", response_data)

        user = client.users.update(123, request_data)

        assert isinstance(user, User)
        client.http_client.assert_request_made("PUT", "/users/123")

    def test_delete_user_success(self, mock_client):
        """Test successful deletion of a user."""
        client = mock_client
        client.http_client.add_response("/users/123", {"status": "deleted"})

        result = client.users.delete(123)

        assert result["status"] == "deleted"
        client.http_client.assert_request_made("DELETE", "/users/123")

    def test_get_settings_success(self, mock_client):
        """Test successful getting of user settings."""
        client = mock_client
        settings_data = [
            {
                "id": "setting1",
                "owner": {"id": 123, "name": "Test User"},
                "org": {"id": 1, "name": "Test Org"},
                "user_settings_type": "general",
                "settings": {"theme": "dark"},
            }
        ]
        client.http_client.add_response("/user_settings", settings_data)

        settings = client.users.get_settings()

        assert len(settings) == 1
        assert isinstance(settings[0], UserSettings)
        client.http_client.assert_request_made("GET", "/user_settings")

    def test_get_quarantine_settings_success(self, mock_client):
        """Test successful getting of quarantine settings."""
        client = mock_client
        settings_data = {"enabled": True, "path": "/quarantine"}
        client.http_client.add_response("/users/123/quarantine_settings", settings_data)

        settings = client.users.get_quarantine_settings(123)

        assert settings["enabled"]
        client.http_client.assert_request_made("GET", "/users/123/quarantine_settings")

    def test_http_error_handling(self, mock_client):
        """Test proper HTTP error handling."""
        client = mock_client
        client.http_client.add_error(
            "/users",
            HttpClientError(
                "Server Error", status_code=500, response={"message": "Internal error"}
            ),
        )

        with pytest.raises(ServerError) as exc_info:
            client.users.list()

        assert exc_info.value.status_code == 500

    def test_empty_list_response(self, mock_client):
        """Test handling of empty list response."""
        client = mock_client
        client.http_client.add_response("/users", [])

        users = client.users.list()

        assert users == []

    def test_user_with_org_memberships(self, mock_client):
        """Test user response with org memberships."""
        client = mock_client
        user_data = MockResponseBuilder.user()
        org_membership1 = MockResponseBuilder.org_membership()
        org_membership1["id"] = 1
        org_membership2 = MockResponseBuilder.org_membership()
        org_membership2["id"] = 2
        user_data.update(
            {"id": 123, "org_memberships": [org_membership1, org_membership2]}
        )
        client.http_client.add_response("/users/123", user_data)

        user = client.users.get(123)

        assert len(user.org_memberships) == 2
        assert user.org_memberships[0].api_key is not None

    def test_get_flow_status_metrics_defaults(self, mock_client):
        """Defaults send no query params and hit /users/<id>/flows/status_metrics."""
        client = mock_client
        user_id = 123
        client.http_client.add_response(
            f"/users/{user_id}/flows/status_metrics", {"total": 0}
        )

        result = client.users.get_flow_status_metrics(user_id)

        assert result == {"total": 0}
        last_request = client.http_client.get_last_request()
        assert last_request["method"] == "GET"
        assert f"/users/{user_id}/flows/status_metrics" in last_request["url"]
        assert last_request["params"] == {}

    def test_get_flow_status_metrics_with_access_role_and_kwargs(self, mock_client):
        """access_role and **kwargs are forwarded as query params."""
        client = mock_client
        user_id = 123
        client.http_client.add_response(
            f"/users/{user_id}/flows/status_metrics", {"total": 5}
        )

        result = client.users.get_flow_status_metrics(
            user_id,
            from_date="2026-01-01",
            page=1,
            per_page=20,
            access_role="collaborator",
            org_id=42,
        )

        assert result == {"total": 5}
        last_request = client.http_client.get_last_request()
        assert last_request["params"] == {
            "from": "2026-01-01",
            "page": 1,
            "per_page": 20,
            "access_role": "collaborator",
            "org_id": 42,
        }
