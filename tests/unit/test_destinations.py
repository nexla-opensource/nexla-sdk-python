"""Unit tests for destinations resource."""

import pytest

from nexla_sdk.exceptions import NotFoundError, ServerError
from nexla_sdk.http_client import HttpClientError
from nexla_sdk.models.destinations.requests import (
    DestinationCopyOptions,
    DestinationCreate,
    DestinationUpdate,
)
from nexla_sdk.models.destinations.responses import DataMapInfo, Destination
from tests.utils.assertions import assert_model_list_valid
from tests.utils.mock_builders import MockResponseBuilder


@pytest.mark.unit
class TestDestinationsResource:
    """Test destinations resource methods."""

    def test_list_destinations(self, mock_client):
        """Test listing destinations."""
        # Arrange
        mock_destinations = [
            MockResponseBuilder.destination({"id": 1, "name": "Dest 1"}),
            MockResponseBuilder.destination({"id": 2, "name": "Dest 2"}),
        ]
        mock_client.http_client.add_response("/data_sinks", mock_destinations)

        # Act
        destinations = mock_client.destinations.list()

        # Assert
        assert len(destinations) == 2
        assert_model_list_valid(destinations, Destination)
        mock_client.http_client.assert_request_made("GET", "/data_sinks")

    def test_list_destinations_with_parameters(self, mock_client):
        """Test listing destinations with query parameters."""
        # Arrange
        mock_destinations = [MockResponseBuilder.destination()]
        mock_client.http_client.add_response("/data_sinks", mock_destinations)

        # Act
        destinations = mock_client.destinations.list(
            page=2, per_page=50, access_role="owner"
        )

        # Assert
        assert len(destinations) == 1
        mock_client.http_client.assert_request_made("GET", "/data_sinks")

        # Verify parameters were sent
        request = mock_client.http_client.get_last_request()
        assert request["params"].get("page") == 2
        assert request["params"].get("per_page") == 50
        assert request["params"].get("access_role") == "owner"

    def test_get_destination(self, mock_client):
        """Test getting single destination."""
        # Arrange
        destination_id = 12345
        mock_response = MockResponseBuilder.destination(
            {"id": destination_id, "name": "Test Destination"}
        )
        mock_client.http_client.add_response(
            f"/data_sinks/{destination_id}", mock_response
        )

        # Act
        destination = mock_client.destinations.get(destination_id)

        # Assert
        assert isinstance(destination, Destination)
        assert destination.id == destination_id
        assert destination.name == "Test Destination"
        mock_client.http_client.assert_request_made(
            "GET", f"/data_sinks/{destination_id}"
        )

    def test_get_destination_with_expand(self, mock_client):
        """Test getting destination with expand parameter."""
        # Arrange
        destination_id = 12345
        mock_response = MockResponseBuilder.destination(
            {
                "id": destination_id,
                "name": "Test Destination",
                "data_set": MockResponseBuilder.data_set_info(),
            }
        )
        mock_client.http_client.add_response(
            f"/data_sinks/{destination_id}", mock_response
        )

        # Act
        destination = mock_client.destinations.get(destination_id, expand=True)

        # Assert
        assert isinstance(destination, Destination)
        assert destination.id == destination_id
        mock_client.http_client.assert_request_made(
            "GET", f"/data_sinks/{destination_id}"
        )

        # Verify expand parameter was sent
        request = mock_client.http_client.get_last_request()
        assert request["params"].get("expand") == 1

    def test_create_destination(self, mock_client):
        """Test creating destination."""
        # Arrange
        create_data = DestinationCreate(
            name="Test Destination",
            sink_type="s3",
            data_credentials_id=100,
            data_set_id=200,
            description="Test description",
        )
        mock_response = MockResponseBuilder.destination(
            {"id": 12345, "name": "Test Destination", "sink_type": "s3"}
        )
        mock_client.http_client.add_response("/data_sinks", mock_response)

        # Act
        destination = mock_client.destinations.create(create_data)

        # Assert
        assert isinstance(destination, Destination)
        assert destination.id == 12345
        assert destination.name == "Test Destination"
        mock_client.http_client.assert_request_made("POST", "/data_sinks")

        # Verify request body
        request = mock_client.http_client.get_last_request()
        assert request["json"]["name"] == "Test Destination"
        assert request["json"]["sink_type"] == "s3"

    def test_update_destination(self, mock_client):
        """Test updating destination."""
        # Arrange
        destination_id = 12345
        update_data = DestinationUpdate(
            name="Updated Destination", description="Updated description"
        )
        mock_response = MockResponseBuilder.destination(
            {"id": destination_id, "name": "Updated Destination"}
        )
        mock_client.http_client.add_response(
            f"/data_sinks/{destination_id}", mock_response
        )

        # Act
        destination = mock_client.destinations.update(destination_id, update_data)

        # Assert
        assert isinstance(destination, Destination)
        assert destination.name == "Updated Destination"
        mock_client.http_client.assert_request_made(
            "PUT", f"/data_sinks/{destination_id}"
        )

    def test_delete_destination(self, mock_client):
        """Test deleting destination."""
        # Arrange
        destination_id = 12345
        mock_client.http_client.add_response(
            f"/data_sinks/{destination_id}", {"status": "deleted"}
        )

        # Act
        result = mock_client.destinations.delete(destination_id)

        # Assert
        assert result == {"status": "deleted"}
        mock_client.http_client.assert_request_made(
            "DELETE", f"/data_sinks/{destination_id}"
        )

    def test_activate_destination(self, mock_client):
        """Test activating destination."""
        # Arrange
        destination_id = 12345
        mock_response = MockResponseBuilder.destination(
            {"id": destination_id, "status": "ACTIVE"}
        )
        mock_client.http_client.add_response(
            f"/data_sinks/{destination_id}/activate", mock_response
        )

        # Act
        destination = mock_client.destinations.activate(destination_id)

        # Assert
        assert isinstance(destination, Destination)
        assert destination.status == "ACTIVE"
        mock_client.http_client.assert_request_made(
            "PUT", f"/data_sinks/{destination_id}/activate"
        )

    def test_pause_destination(self, mock_client):
        """Test pausing destination."""
        # Arrange
        destination_id = 12345
        mock_response = MockResponseBuilder.destination(
            {"id": destination_id, "status": "PAUSED"}
        )
        mock_client.http_client.add_response(
            f"/data_sinks/{destination_id}/pause", mock_response
        )

        # Act
        destination = mock_client.destinations.pause(destination_id)

        # Assert
        assert isinstance(destination, Destination)
        assert destination.status == "PAUSED"
        mock_client.http_client.assert_request_made(
            "PUT", f"/data_sinks/{destination_id}/pause"
        )

    def test_copy_destination(self, mock_client):
        """Test copying destination."""
        # Arrange
        destination_id = 12345
        copy_options = DestinationCopyOptions(
            reuse_data_credentials=True, copy_access_controls=False
        )
        mock_response = MockResponseBuilder.destination(
            {"id": 54321, "name": "Copied Destination"}
        )
        mock_client.http_client.add_response(
            f"/data_sinks/{destination_id}/copy", mock_response
        )

        # Act
        destination = mock_client.destinations.copy(destination_id, copy_options)

        # Assert
        assert isinstance(destination, Destination)
        assert destination.id == 54321
        mock_client.http_client.assert_request_made(
            "POST", f"/data_sinks/{destination_id}/copy"
        )

    def test_http_error_handling(self, mock_client):
        """Test HTTP error handling."""
        # Arrange
        mock_client.http_client.add_error(
            "/data_sinks",
            HttpClientError(
                "Server Error",
                status_code=500,
                response={"message": "Internal server error"},
            ),
        )

        # Act & Assert
        with pytest.raises(ServerError) as exc_info:
            mock_client.destinations.list()

        assert exc_info.value.status_code == 500

    def test_not_found_error(self, mock_client):
        """Test not found error handling."""
        # Arrange
        destination_id = 99999
        mock_client.http_client.add_error(
            f"/data_sinks/{destination_id}",
            HttpClientError(
                "Not found",
                status_code=404,
                response={"message": "Destination not found"},
            ),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.destinations.get(destination_id)

    def test_validation_error_handling(self):
        """Test validation error handling."""
        # Arrange
        invalid_data = {"invalid": "data"}  # Missing required fields

        # Act & Assert - Will raise validation error during model creation
        with pytest.raises(Exception):
            DestinationCreate(**invalid_data)

    def test_empty_list_response(self, mock_client):
        """Test handling empty list response."""
        # Arrange
        mock_client.http_client.add_response("/data_sinks", [])

        # Act
        destinations = mock_client.destinations.list()

        # Assert
        assert destinations == []
        assert len(destinations) == 0

    def test_destination_with_null_data_map_description(self, mock_client):
        """Test that destinations with None data_map.description validate correctly."""
        mock_response = MockResponseBuilder.destination(
            {
                "id": 100,
                "name": "Dest with null map desc",
                "data_map": {
                    "id": 1,
                    "owner_id": 10,
                    "org_id": 5,
                    "name": "Test Map",
                    "description": None,
                    "public": False,
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                },
            }
        )
        mock_client.http_client.add_response("/data_sinks/100", mock_response)

        destination = mock_client.destinations.get(100)

        assert isinstance(destination, Destination)
        assert destination.data_map is not None
        assert isinstance(destination.data_map, DataMapInfo)
        assert destination.data_map.description is None

    def test_data_map_info_with_null_description(self):
        """Test DataMapInfo model validates with description=None."""
        data = {
            "id": 1,
            "owner_id": 10,
            "org_id": 5,
            "name": "Map",
            "description": None,
            "public": False,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
        }
        model = DataMapInfo.model_validate(data)
        assert model.description is None
