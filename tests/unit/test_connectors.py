"""Unit tests for connectors resource."""

import pytest

from nexla_sdk.models.connectors.requests import ConnectorUpdate
from nexla_sdk.models.connectors.responses import Connector
from tests.utils import assert_model_list_valid, assert_model_valid

# Sample response data
SAMPLE_CONNECTOR = {
    "id": 123,
    "type": "s3",
    "connection_type": "file",
    "name": "Amazon S3",
    "description": "Amazon Simple Storage Service connector",
    "nexset_api_compatible": True,
    "sync_api_compatible": True,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
}

SAMPLE_CONNECTORS_LIST = [
    SAMPLE_CONNECTOR,
    {**SAMPLE_CONNECTOR, "id": 124, "type": "gcs", "name": "Google Cloud Storage"},
    {**SAMPLE_CONNECTOR, "id": 125, "type": "azure_blob", "name": "Azure Blob Storage"},
]


@pytest.fixture
def sample_connector_response():
    """Sample connector response."""
    return SAMPLE_CONNECTOR.copy()


@pytest.fixture
def sample_connectors_list():
    """Sample connectors list response."""
    return [c.copy() for c in SAMPLE_CONNECTORS_LIST]


@pytest.mark.unit
class TestConnectorsResource:
    """Unit tests for ConnectorsResource using mocks."""

    def test_list_connectors_success(
        self, mock_client, mock_http_client, sample_connectors_list
    ):
        """Test listing connectors with successful response."""
        mock_http_client.add_response("/connectors", sample_connectors_list)

        connectors = mock_client.connectors.list()

        assert len(connectors) == 3
        assert_model_list_valid(connectors, Connector)
        mock_http_client.assert_request_made("GET", "/connectors")

    def test_list_connectors_with_filter(
        self, mock_client, mock_http_client, sample_connectors_list
    ):
        """Test listing connectors with API compatibility filter."""
        mock_http_client.add_response("/connectors", sample_connectors_list)

        connectors = mock_client.connectors.list(nexset_api_compatible=True)

        assert len(connectors) == 3
        mock_http_client.assert_request_made("GET", "/connectors")

    def test_get_connector_by_id(
        self, mock_client, mock_http_client, sample_connector_response
    ):
        """Test getting a connector by ID."""
        connector_id = 123
        mock_http_client.add_response(
            f"/connectors/{connector_id}", sample_connector_response
        )

        connector = mock_client.connectors.get(connector_id)

        assert_model_valid(connector, {"id": connector_id})
        mock_http_client.assert_request_made("GET", f"/connectors/{connector_id}")

    def test_get_connector_by_type(
        self, mock_client, mock_http_client, sample_connector_response
    ):
        """Test getting a connector by type."""
        connector_type = "s3"
        mock_http_client.add_response(
            f"/connectors/{connector_type}", sample_connector_response
        )

        connector = mock_client.connectors.get(connector_type)

        assert connector.type == connector_type
        mock_http_client.assert_request_made("GET", f"/connectors/{connector_type}")

    def test_update_connector_success(
        self, mock_client, mock_http_client, sample_connector_response
    ):
        """Test updating a connector."""
        connector_id = 123
        updated_response = {**sample_connector_response, "description": "Updated desc"}
        mock_http_client.add_response(f"/connectors/{connector_id}", updated_response)

        update_data = ConnectorUpdate(description="Updated desc")
        connector = mock_client.connectors.update(connector_id, update_data)

        assert connector.description == "Updated desc"
        mock_http_client.assert_request_made("PUT", f"/connectors/{connector_id}")


@pytest.mark.unit
class TestConnectorModels:
    """Unit tests for connector models."""

    def test_connector_model_validation(self, sample_connector_response):
        """Test Connector model parses valid data correctly."""
        connector = Connector.model_validate(sample_connector_response)

        assert connector.id == 123
        assert connector.type == "s3"
        assert connector.name == "Amazon S3"
        assert connector.nexset_api_compatible is True

    def test_connector_model_with_minimal_data(self):
        """Test Connector model with minimal required fields."""
        minimal_data = {
            "id": 1,
        }
        connector = Connector.model_validate(minimal_data)

        assert connector.id == 1
        assert connector.type is None
        assert connector.name is None

    def test_connector_update_model_serialization(self):
        """Test ConnectorUpdate model serialization."""
        update_data = ConnectorUpdate(
            name="Updated Name",
            description="Updated description",
            nexset_api_compatible=True,
        )

        data = update_data.model_dump(exclude_none=True)

        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"
        assert data["nexset_api_compatible"] is True


@pytest.mark.unit
class TestConnectorsUnsupportedOperations:
    """Test that unsupported operations raise NotImplementedError."""

    def test_create_raises_not_implemented(self, mock_client):
        with pytest.raises(NotImplementedError, match="not supported"):
            mock_client.connectors.create({"name": "test"})

    def test_delete_raises_not_implemented(self, mock_client):
        with pytest.raises(NotImplementedError, match="not supported"):
            mock_client.connectors.delete(123)

    def test_copy_raises_not_implemented(self, mock_client):
        with pytest.raises(NotImplementedError, match="not supported"):
            mock_client.connectors.copy(123)

    def test_activate_raises_not_implemented(self, mock_client):
        with pytest.raises(NotImplementedError, match="not supported"):
            mock_client.connectors.activate(123)

    def test_pause_raises_not_implemented(self, mock_client):
        with pytest.raises(NotImplementedError, match="not supported"):
            mock_client.connectors.pause(123)
