"""Unit tests for audit log operations across resources.

Tests the get_audit_log functionality provided by BaseResource, which
retrieves audit history for resources via GET /{endpoint}/{id}/audit_log.
"""

import pytest

from nexla_sdk.exceptions import AuthorizationError, NotFoundError
from tests.utils import MockResponseBuilder, create_http_error


@pytest.mark.unit
class TestGetAuditLog:
    """Tests for get_audit_log operations."""

    def test_get_audit_log_returns_list(self, mock_client, mock_http_client):
        """Test that get_audit_log returns a list of audit log entries."""
        # Arrange
        resource_id = 123
        audit_entries = [
            MockResponseBuilder.audit_log_entry(event="create"),
            MockResponseBuilder.audit_log_entry(event="update"),
        ]
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", audit_entries
        )

        # Act
        result = mock_client.sources.get_audit_log(resource_id)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 2
        mock_http_client.assert_request_made(
            "GET", f"/data_sources/{resource_id}/audit_log"
        )

    def test_get_audit_log_empty_list(self, mock_client, mock_http_client):
        """Test getting audit log returns empty list when no entries exist."""
        # Arrange
        resource_id = 123
        mock_http_client.add_response(f"/data_sources/{resource_id}/audit_log", [])

        # Act
        result = mock_client.sources.get_audit_log(resource_id)

        # Assert
        assert result == []
        mock_http_client.assert_request_made(
            "GET", f"/data_sources/{resource_id}/audit_log"
        )

    def test_get_audit_log_single_entry(self, mock_client, mock_http_client):
        """Test getting audit log with a single entry."""
        # Arrange
        resource_id = 456
        audit_entry = MockResponseBuilder.audit_log_entry(
            item_type="DataSource",
            item_id=resource_id,
            event="create",
        )
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", [audit_entry]
        )

        # Act
        result = mock_client.sources.get_audit_log(resource_id)

        # Assert
        assert len(result) == 1
        assert result[0]["event"] == "create"
        assert result[0]["item_type"] == "DataSource"

    def test_get_audit_log_with_date_filters(self, mock_client, mock_http_client):
        """Test get_audit_log passes from_date and to_date as query params."""
        # Arrange
        resource_id = 123
        audit_entries = [
            MockResponseBuilder.audit_log_entry(event="create"),
        ]
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", audit_entries
        )

        # Act
        mock_client.sources.get_audit_log(
            resource_id, from_date="2024-01-01", to_date="2024-01-31"
        )

        # Assert
        params = mock_http_client.get_last_request()["params"]
        assert params == {"from": "2024-01-01", "to": "2024-01-31"}

    def test_get_audit_log_with_event_filter(self, mock_client, mock_http_client):
        """Test get_audit_log passes event_filter as query param."""
        # Arrange
        resource_id = 123
        audit_entries = [
            MockResponseBuilder.audit_log_entry(event="create"),
        ]
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", audit_entries
        )

        # Act
        mock_client.sources.get_audit_log(resource_id, event_filter="create")

        # Assert
        params = mock_http_client.get_last_request()["params"]
        assert params == {"event_filter": "create"}

    def test_get_audit_log_with_change_filter(self, mock_client, mock_http_client):
        """Test get_audit_log passes change_filter as query param."""
        # Arrange
        resource_id = 123
        audit_entries = [
            MockResponseBuilder.audit_log_entry(event="update"),
        ]
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", audit_entries
        )

        # Act
        mock_client.sources.get_audit_log(resource_id, change_filter="attribute")

        # Assert
        params = mock_http_client.get_last_request()["params"]
        assert params == {"change_filter": "attribute"}

    def test_get_audit_log_with_pagination(self, mock_client, mock_http_client):
        """Test get_audit_log passes page and per_page as query params."""
        # Arrange
        resource_id = 123
        audit_entries = [
            MockResponseBuilder.audit_log_entry(event="create"),
        ]
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", audit_entries
        )

        # Act
        mock_client.sources.get_audit_log(resource_id, page=2, per_page=25)

        # Assert
        params = mock_http_client.get_last_request()["params"]
        assert params == {"page": 2, "per_page": 25}

    def test_get_audit_log_with_all_params(self, mock_client, mock_http_client):
        """Test get_audit_log passes all optional params as query params."""
        # Arrange
        resource_id = 123
        audit_entries = [
            MockResponseBuilder.audit_log_entry(event="update"),
        ]
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", audit_entries
        )

        # Act
        mock_client.sources.get_audit_log(
            resource_id,
            from_date="2024-01-01",
            to_date="2024-01-31",
            event_filter="create",
            change_filter="attribute",
            page=2,
            per_page=25,
        )

        # Assert
        params = mock_http_client.get_last_request()["params"]
        assert params == {
            "from": "2024-01-01",
            "to": "2024-01-31",
            "event_filter": "create",
            "change_filter": "attribute",
            "page": 2,
            "per_page": 25,
        }

    def test_get_audit_log_with_no_optional_params(self, mock_client, mock_http_client):
        """Test get_audit_log sends no query params when none are provided."""
        # Arrange
        resource_id = 123
        audit_entries = [
            MockResponseBuilder.audit_log_entry(event="create"),
        ]
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", audit_entries
        )

        # Act
        mock_client.sources.get_audit_log(resource_id)

        # Assert
        params = mock_http_client.get_last_request()["params"]
        assert params == {}


@pytest.mark.unit
class TestAuditLogEntryFields:
    """Tests for verifying audit log entry structure and fields."""

    def test_entry_has_required_fields(self, mock_client, mock_http_client):
        """Test that audit log entry has required fields."""
        # Arrange
        resource_id = 123
        audit_entry = MockResponseBuilder.audit_log_entry(
            item_type="DataSource",
            item_id=resource_id,
            event="update",
            object_changes={"name": ["Old Name", "New Name"]},
        )
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", [audit_entry]
        )

        # Act
        result = mock_client.sources.get_audit_log(resource_id)

        # Assert
        assert len(result) == 1
        entry = result[0]
        # Verify required fields are present
        assert "item_type" in entry
        assert "item_id" in entry
        assert "event" in entry
        assert "object_changes" in entry
        assert "created_at" in entry

    def test_entry_has_user_information(self, mock_client, mock_http_client):
        """Test that audit log entry contains user information."""
        # Arrange
        resource_id = 123
        audit_entry = MockResponseBuilder.audit_log_entry(
            owner_id=456,
            owner_email="user@example.com",
            user={"id": 456, "email": "user@example.com"},
        )
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", [audit_entry]
        )

        # Act
        result = mock_client.sources.get_audit_log(resource_id)

        # Assert
        entry = result[0]
        assert "owner_id" in entry
        assert "owner_email" in entry
        assert "user" in entry
        assert entry["user"]["email"] == "user@example.com"

    def test_entry_has_request_metadata(self, mock_client, mock_http_client):
        """Test that audit log entry contains request metadata."""
        # Arrange
        resource_id = 123
        audit_entry = MockResponseBuilder.audit_log_entry(
            request_ip="192.168.1.1",
            request_user_agent="Mozilla/5.0 Test",
            request_url="/api/v1/data_sources/123",
        )
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", [audit_entry]
        )

        # Act
        result = mock_client.sources.get_audit_log(resource_id)

        # Assert
        entry = result[0]
        assert "request_ip" in entry
        assert "request_user_agent" in entry
        assert "request_url" in entry


@pytest.mark.unit
class TestAuditLogEventTypes:
    """Tests for different audit log event types."""

    def test_create_event(self, mock_client, mock_http_client):
        """Test audit log entry with create event."""
        # Arrange
        resource_id = 123
        audit_entry = MockResponseBuilder.audit_log_entry(
            item_type="DataSource",
            item_id=resource_id,
            event="create",
            object_changes={},
        )
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", [audit_entry]
        )

        # Act
        result = mock_client.sources.get_audit_log(resource_id)

        # Assert
        assert len(result) == 1
        assert result[0]["event"] == "create"

    def test_update_event_includes_object_changes(self, mock_client, mock_http_client):
        """Test audit log entry with update event includes object_changes."""
        # Arrange
        resource_id = 123
        object_changes = {
            "name": ["Original Name", "Updated Name"],
            "status": ["DRAFT", "ACTIVE"],
        }
        audit_entry = MockResponseBuilder.audit_log_entry(
            item_type="DataSource",
            item_id=resource_id,
            event="update",
            object_changes=object_changes,
            change_summary=["name", "status"],
        )
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", [audit_entry]
        )

        # Act
        result = mock_client.sources.get_audit_log(resource_id)

        # Assert
        assert len(result) == 1
        entry = result[0]
        assert entry["event"] == "update"
        assert "object_changes" in entry
        assert entry["object_changes"]["name"] == ["Original Name", "Updated Name"]
        assert entry["object_changes"]["status"] == ["DRAFT", "ACTIVE"]

    def test_destroy_event(self, mock_client, mock_http_client):
        """Test audit log entry with destroy event."""
        # Arrange
        resource_id = 123
        audit_entry = MockResponseBuilder.audit_log_entry(
            item_type="DataSource",
            item_id=resource_id,
            event="destroy",
            object_changes={},
        )
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", [audit_entry]
        )

        # Act
        result = mock_client.sources.get_audit_log(resource_id)

        # Assert
        assert len(result) == 1
        assert result[0]["event"] == "destroy"

    def test_association_event(self, mock_client, mock_http_client):
        """Test audit log entry with association events (e.g., add_accessor)."""
        # Arrange
        resource_id = 123
        audit_entry = MockResponseBuilder.audit_log_entry(
            item_type="DataSource",
            item_id=resource_id,
            event="add_accessor",
            object_changes={
                "accessor_type": [None, "USER"],
                "accessor_id": [None, 456],
            },
        )
        mock_http_client.add_response(
            f"/data_sources/{resource_id}/audit_log", [audit_entry]
        )

        # Act
        result = mock_client.sources.get_audit_log(resource_id)

        # Assert
        assert len(result) == 1
        assert result[0]["event"] == "add_accessor"
        assert result[0]["object_changes"]["accessor_type"] == [None, "USER"]


@pytest.mark.unit
class TestAuditLogErrorHandling:
    """Tests for audit log error scenarios."""

    def test_audit_log_not_found_returns_404(self, mock_client, mock_http_client):
        """Test that accessing audit log of non-existent resource returns 404."""
        # Arrange
        resource_id = 99999
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/audit_log",
            create_http_error(404, "Resource not found"),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.sources.get_audit_log(resource_id)

    def test_audit_log_permission_denied_returns_403(
        self, mock_client, mock_http_client
    ):
        """Test that unauthorized access to audit log returns 403."""
        # Arrange
        resource_id = 123
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/audit_log",
            create_http_error(403, "Forbidden"),
        )

        # Act & Assert
        with pytest.raises(AuthorizationError):
            mock_client.sources.get_audit_log(resource_id)


@pytest.mark.unit
class TestAuditLogAcrossResources:
    """Tests verifying audit log operations work across resource types.

    Note: TeamsResource has its own get_audit_log implementation that returns
    LogEntry model objects instead of raw dicts. It is tested separately.
    """

    @pytest.mark.parametrize(
        "resource_name,endpoint,item_type",
        [
            ("sources", "/data_sources", "DataSource"),
            ("destinations", "/data_sinks", "DataSink"),
            ("nexsets", "/data_sets", "DataSet"),
            ("credentials", "/data_credentials", "DataCredential"),
            ("lookups", "/data_maps", "DataMap"),
            ("projects", "/projects", "Project"),
        ],
    )
    def test_get_audit_log_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint, item_type
    ):
        """Test get_audit_log works for different resource types."""
        # Arrange
        resource_id = 123
        audit_entries = [
            MockResponseBuilder.audit_log_entry(
                item_type=item_type,
                item_id=resource_id,
                event="create",
            ),
            MockResponseBuilder.audit_log_entry(
                item_type=item_type,
                item_id=resource_id,
                event="update",
            ),
        ]
        mock_http_client.add_response(
            f"{endpoint}/{resource_id}/audit_log", audit_entries
        )

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.get_audit_log(resource_id)

        # Assert
        assert len(result) == 2
        assert result[0]["item_type"] == item_type
        mock_http_client.assert_request_made(
            "GET", f"{endpoint}/{resource_id}/audit_log"
        )

    def test_teams_get_audit_log_returns_model_objects(
        self, mock_client, mock_http_client
    ):
        """Test teams.get_audit_log returns LogEntry model objects.

        Note: TeamsResource has its own get_audit_log that parses responses
        into LogEntry model objects rather than returning raw dicts.
        """
        # Arrange
        team_id = 123
        audit_entries = [
            MockResponseBuilder.audit_log_entry(
                item_type="Team",
                item_id=team_id,
                event="create",
            ),
            MockResponseBuilder.audit_log_entry(
                item_type="Team",
                item_id=team_id,
                event="update",
            ),
        ]
        mock_http_client.add_response(f"/teams/{team_id}/audit_log", audit_entries)

        # Act
        result = mock_client.teams.get_audit_log(team_id)

        # Assert
        assert len(result) == 2
        # LogEntry is a model object, so access via attributes
        assert result[0].item_type == "Team"
        assert result[0].event == "create"
        assert result[1].event == "update"
        mock_http_client.assert_request_made("GET", f"/teams/{team_id}/audit_log")

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
            ("credentials", "/data_credentials"),
        ],
    )
    def test_audit_log_empty_for_resource_type(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test get_audit_log returns empty list for resource types with no history."""
        # Arrange
        resource_id = 789
        mock_http_client.add_response(f"{endpoint}/{resource_id}/audit_log", [])

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.get_audit_log(resource_id)

        # Assert
        assert result == []
        mock_http_client.assert_request_made(
            "GET", f"{endpoint}/{resource_id}/audit_log"
        )
