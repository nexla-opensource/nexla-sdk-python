"""Unit tests for lifecycle operations (activate, pause, copy)."""

import pytest

from nexla_sdk.exceptions import NotFoundError
from nexla_sdk.models.sources.responses import Source
from tests.utils import MockResponseBuilder, create_http_error


@pytest.mark.unit
class TestActivateOperation:
    """Tests for resource activation."""

    def test_activate_source_success(self, mock_client, mock_http_client):
        """Test activating a source."""
        # Arrange
        resource_id = 123
        response = MockResponseBuilder.source(source_id=resource_id, status="ACTIVE")
        mock_http_client.add_response(f"/data_sources/{resource_id}/activate", response)

        # Act
        result = mock_client.sources.activate(resource_id)

        # Assert
        assert isinstance(result, Source)
        assert result.status == "ACTIVE"
        mock_http_client.assert_request_made(
            "PUT", f"/data_sources/{resource_id}/activate"
        )

    def test_activate_destination_success(self, mock_client, mock_http_client):
        """Test activating a destination."""
        # Arrange
        resource_id = 456
        response = MockResponseBuilder.destination(
            {"id": resource_id, "status": "ACTIVE"}
        )
        mock_http_client.add_response(f"/data_sinks/{resource_id}/activate", response)

        # Act
        result = mock_client.destinations.activate(resource_id)

        # Assert
        assert result.status == "ACTIVE"
        mock_http_client.assert_request_made(
            "PUT", f"/data_sinks/{resource_id}/activate"
        )

    def test_activate_nexset_success(self, mock_client, mock_http_client):
        """Test activating a nexset."""
        # Arrange
        resource_id = 789
        response = MockResponseBuilder.nexset({"id": resource_id, "status": "ACTIVE"})
        mock_http_client.add_response(f"/data_sets/{resource_id}/activate", response)

        # Act
        result = mock_client.nexsets.activate(resource_id)

        # Assert
        assert result.status == "ACTIVE"
        mock_http_client.assert_request_made(
            "PUT", f"/data_sets/{resource_id}/activate"
        )

    def test_activate_returns_updated_status(self, mock_client, mock_http_client):
        """Test that activate returns resource with updated status."""
        # Arrange
        resource_id = 123
        # Simulate a source that was PAUSED and is now ACTIVE
        response = MockResponseBuilder.source(source_id=resource_id, status="ACTIVE")
        mock_http_client.add_response(f"/data_sources/{resource_id}/activate", response)

        # Act
        result = mock_client.sources.activate(resource_id)

        # Assert
        assert result.id == resource_id
        assert result.status == "ACTIVE"

    def test_activate_not_found(self, mock_client, mock_http_client):
        """Test activate on non-existent resource raises NotFoundError."""
        # Arrange
        resource_id = 99999
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/activate",
            create_http_error(404, "Resource not found"),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.sources.activate(resource_id)


@pytest.mark.unit
class TestPauseOperation:
    """Tests for resource pausing."""

    def test_pause_source_success(self, mock_client, mock_http_client):
        """Test pausing a source."""
        # Arrange
        resource_id = 123
        response = MockResponseBuilder.source(source_id=resource_id, status="PAUSED")
        mock_http_client.add_response(f"/data_sources/{resource_id}/pause", response)

        # Act
        result = mock_client.sources.pause(resource_id)

        # Assert
        assert isinstance(result, Source)
        assert result.status == "PAUSED"
        mock_http_client.assert_request_made(
            "PUT", f"/data_sources/{resource_id}/pause"
        )

    def test_pause_destination_success(self, mock_client, mock_http_client):
        """Test pausing a destination."""
        # Arrange
        resource_id = 456
        response = MockResponseBuilder.destination(
            {"id": resource_id, "status": "PAUSED"}
        )
        mock_http_client.add_response(f"/data_sinks/{resource_id}/pause", response)

        # Act
        result = mock_client.destinations.pause(resource_id)

        # Assert
        assert result.status == "PAUSED"
        mock_http_client.assert_request_made("PUT", f"/data_sinks/{resource_id}/pause")

    def test_pause_nexset_success(self, mock_client, mock_http_client):
        """Test pausing a nexset."""
        # Arrange
        resource_id = 789
        response = MockResponseBuilder.nexset({"id": resource_id, "status": "PAUSED"})
        mock_http_client.add_response(f"/data_sets/{resource_id}/pause", response)

        # Act
        result = mock_client.nexsets.pause(resource_id)

        # Assert
        assert result.status == "PAUSED"
        mock_http_client.assert_request_made("PUT", f"/data_sets/{resource_id}/pause")

    def test_pause_returns_updated_status(self, mock_client, mock_http_client):
        """Test that pause returns resource with updated status."""
        # Arrange
        resource_id = 123
        response = MockResponseBuilder.source(source_id=resource_id, status="PAUSED")
        mock_http_client.add_response(f"/data_sources/{resource_id}/pause", response)

        # Act
        result = mock_client.sources.pause(resource_id)

        # Assert
        assert result.id == resource_id
        assert result.status == "PAUSED"

    def test_pause_not_found(self, mock_client, mock_http_client):
        """Test pause on non-existent resource raises NotFoundError."""
        # Arrange
        resource_id = 99999
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/pause",
            create_http_error(404, "Resource not found"),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.sources.pause(resource_id)


@pytest.mark.unit
class TestCopyOperation:
    """Tests for resource copying."""

    def test_copy_source_default_options(self, mock_client, mock_http_client):
        """Test copying a source with default options."""
        # Arrange
        resource_id = 123
        copied_id = 456
        response = MockResponseBuilder.source(
            source_id=copied_id, name="Copy of Source"
        )
        mock_http_client.add_response(f"/data_sources/{resource_id}/copy", response)

        # Act
        result = mock_client.sources.copy(resource_id)

        # Assert
        assert isinstance(result, Source)
        assert result.id == copied_id
        mock_http_client.assert_request_made(
            "POST", f"/data_sources/{resource_id}/copy"
        )

    def test_copy_destination_default_options(self, mock_client, mock_http_client):
        """Test copying a destination with default options."""
        # Arrange
        resource_id = 123
        copied_id = 456
        response = MockResponseBuilder.destination(
            {"id": copied_id, "name": "Copy of Destination"}
        )
        mock_http_client.add_response(f"/data_sinks/{resource_id}/copy", response)

        # Act
        result = mock_client.destinations.copy(resource_id)

        # Assert
        assert result.id == copied_id

    def test_copy_nexset_default_options(self, mock_client, mock_http_client):
        """Test copying a nexset with default options."""
        # Arrange
        resource_id = 123
        copied_id = 456
        response = MockResponseBuilder.nexset(
            {"id": copied_id, "name": "Copy of Nexset"}
        )
        mock_http_client.add_response(f"/data_sets/{resource_id}/copy", response)

        # Act
        result = mock_client.nexsets.copy(resource_id)

        # Assert
        assert result.id == copied_id

    def test_copy_project_default_options(self, mock_client, mock_http_client):
        """Test copying a project with default options."""
        # Arrange
        resource_id = 123
        copied_id = 456
        response = MockResponseBuilder.project(
            project_id=copied_id, name="Copy of Project"
        )
        mock_http_client.add_response(f"/projects/{resource_id}/copy", response)

        # Act
        result = mock_client.projects.copy(resource_id)

        # Assert
        assert result.id == copied_id

    def test_copy_returns_new_resource(self, mock_client, mock_http_client):
        """Test that copy returns a new resource with different ID."""
        # Arrange
        original_id = 123
        copied_id = 456
        response = MockResponseBuilder.source(source_id=copied_id, name="Copied Source")
        mock_http_client.add_response(f"/data_sources/{original_id}/copy", response)

        # Act
        result = mock_client.sources.copy(original_id)

        # Assert
        assert result.id == copied_id
        assert result.id != original_id
        mock_http_client.assert_request_made(
            "POST", f"/data_sources/{original_id}/copy"
        )

    def test_copy_not_found(self, mock_client, mock_http_client):
        """Test copy on non-existent resource raises NotFoundError."""
        # Arrange
        resource_id = 99999
        mock_http_client.add_error(
            f"/data_sources/{resource_id}/copy",
            create_http_error(404, "Resource not found"),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.sources.copy(resource_id)


@pytest.mark.unit
class TestLifecycleOperationsAcrossResources:
    """Tests for lifecycle operations across different resource types."""

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
        ],
    )
    def test_activate_across_resources(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test activate works across different resource types."""
        # Arrange
        resource_id = 123
        if resource_name == "sources":
            response = MockResponseBuilder.source(
                source_id=resource_id, status="ACTIVE"
            )
        elif resource_name == "destinations":
            response = MockResponseBuilder.destination(
                {"id": resource_id, "status": "ACTIVE"}
            )
        else:
            response = MockResponseBuilder.nexset(
                {"id": resource_id, "status": "ACTIVE"}
            )

        mock_http_client.add_response(f"{endpoint}/{resource_id}/activate", response)

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.activate(resource_id)

        # Assert
        assert result.status == "ACTIVE"
        mock_http_client.assert_request_made(
            "PUT", f"{endpoint}/{resource_id}/activate"
        )

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
        ],
    )
    def test_pause_across_resources(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test pause works across different resource types."""
        # Arrange
        resource_id = 123
        if resource_name == "sources":
            response = MockResponseBuilder.source(
                source_id=resource_id, status="PAUSED"
            )
        elif resource_name == "destinations":
            response = MockResponseBuilder.destination(
                {"id": resource_id, "status": "PAUSED"}
            )
        else:
            response = MockResponseBuilder.nexset(
                {"id": resource_id, "status": "PAUSED"}
            )

        mock_http_client.add_response(f"{endpoint}/{resource_id}/pause", response)

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.pause(resource_id)

        # Assert
        assert result.status == "PAUSED"
        mock_http_client.assert_request_made("PUT", f"{endpoint}/{resource_id}/pause")

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
            ("projects", "/projects"),
        ],
    )
    def test_copy_across_resources(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test copy works across different resource types."""
        # Arrange
        resource_id = 123
        copied_id = 456
        if resource_name == "sources":
            response = MockResponseBuilder.source(source_id=copied_id)
        elif resource_name == "destinations":
            response = MockResponseBuilder.destination({"id": copied_id})
        elif resource_name == "nexsets":
            response = MockResponseBuilder.nexset({"id": copied_id})
        else:
            response = MockResponseBuilder.project(project_id=copied_id)

        mock_http_client.add_response(f"{endpoint}/{resource_id}/copy", response)

        # Act
        resource = getattr(mock_client, resource_name)
        result = resource.copy(resource_id)

        # Assert
        assert result.id == copied_id
        mock_http_client.assert_request_made("POST", f"{endpoint}/{resource_id}/copy")
