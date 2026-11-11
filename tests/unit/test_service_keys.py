"""Unit tests for service keys resource."""

import pytest

from nexla_sdk.models.service_keys.requests import ServiceKeyCreate, ServiceKeyUpdate
from nexla_sdk.models.service_keys.responses import ServiceKey
from tests.utils import assert_model_list_valid, assert_model_valid

# Sample response data
SAMPLE_SERVICE_KEY = {
    "id": 123,
    "owner_id": 1,
    "org_id": 1,
    "name": "Test Service Key",
    "description": "A test service key",
    "status": "ACTIVE",
    "api_key": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "last_rotated_key": None,
    "last_rotated_at": None,
    "data_source_id": None,
    "updated_at": "2025-01-01T00:00:00Z",
    "created_at": "2025-01-01T00:00:00Z",
}

SAMPLE_SERVICE_KEYS_LIST = [
    SAMPLE_SERVICE_KEY,
    {**SAMPLE_SERVICE_KEY, "id": 124, "name": "Another Key", "status": "PAUSED"},
    {**SAMPLE_SERVICE_KEY, "id": 125, "name": "Third Key"},
]


@pytest.fixture
def sample_service_key_response():
    """Sample service key response."""
    return SAMPLE_SERVICE_KEY.copy()


@pytest.fixture
def sample_service_keys_list():
    """Sample service keys list response."""
    return [k.copy() for k in SAMPLE_SERVICE_KEYS_LIST]


@pytest.mark.unit
class TestServiceKeysResource:
    """Unit tests for ServiceKeysResource using mocks."""

    def test_list_service_keys_success(
        self, mock_client, mock_http_client, sample_service_keys_list
    ):
        """Test listing service keys with successful response."""
        mock_http_client.add_response("/service_keys", sample_service_keys_list)

        keys = mock_client.service_keys.list()

        assert len(keys) == 3
        assert_model_list_valid(keys, ServiceKey)
        mock_http_client.assert_request_made("GET", "/service_keys")

    def test_list_service_keys_all(
        self, mock_client, mock_http_client, sample_service_keys_list
    ):
        """Test listing all service keys in org."""
        mock_http_client.add_response("/service_keys", sample_service_keys_list)

        keys = mock_client.service_keys.list(all_keys=True)

        assert len(keys) == 3
        request = mock_http_client.get_request()
        assert "all" in str(request)

    def test_list_service_keys_with_pagination(
        self, mock_client, mock_http_client, sample_service_keys_list
    ):
        """Test listing service keys with pagination."""
        mock_http_client.add_response("/service_keys", sample_service_keys_list)

        keys = mock_client.service_keys.list(page=1, per_page=10)

        assert len(keys) == 3

    def test_get_service_key_by_id(
        self, mock_client, mock_http_client, sample_service_key_response
    ):
        """Test getting a service key by ID."""
        key_id = 123
        mock_http_client.add_response(
            f"/service_keys/{key_id}", sample_service_key_response
        )

        key = mock_client.service_keys.get(key_id)

        assert_model_valid(key, {"id": key_id})
        mock_http_client.assert_request_made("GET", f"/service_keys/{key_id}")

    def test_get_service_key_by_key_value(
        self, mock_client, mock_http_client, sample_service_key_response
    ):
        """Test getting a service key by its api_key value."""
        api_key = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        mock_http_client.add_response(
            f"/service_keys/{api_key}", sample_service_key_response
        )

        key = mock_client.service_keys.get(api_key)

        assert_model_valid(key, {"api_key": api_key})

    def test_create_service_key_success(
        self, mock_client, mock_http_client, sample_service_key_response
    ):
        """Test creating a service key."""
        mock_http_client.add_response("/service_keys", sample_service_key_response)

        create_data = ServiceKeyCreate(
            name="Test Service Key",
            description="A test service key",
        )
        key = mock_client.service_keys.create(create_data)

        assert_model_valid(key, {"name": "Test Service Key"})
        mock_http_client.assert_request_made("POST", "/service_keys")

    def test_update_service_key_success(
        self, mock_client, mock_http_client, sample_service_key_response
    ):
        """Test updating a service key."""
        key_id = 123
        updated_response = {**sample_service_key_response, "name": "Updated Key"}
        mock_http_client.add_response(f"/service_keys/{key_id}", updated_response)

        update_data = ServiceKeyUpdate(name="Updated Key")
        key = mock_client.service_keys.update(key_id, update_data)

        assert key.name == "Updated Key"
        mock_http_client.assert_request_made("PUT", f"/service_keys/{key_id}")

    def test_delete_service_key_success(self, mock_client, mock_http_client):
        """Test deleting a service key."""
        key_id = 123
        mock_http_client.add_response(f"/service_keys/{key_id}", {"success": True})

        result = mock_client.service_keys.delete(key_id)

        assert result["success"] is True
        mock_http_client.assert_request_made("DELETE", f"/service_keys/{key_id}")

    def test_rotate_service_key_success(
        self, mock_client, mock_http_client, sample_service_key_response
    ):
        """Test rotating a service key."""
        key_id = 123
        rotated_response = {
            **sample_service_key_response,
            "api_key": "new_rotated_key_12345678901234567",
            "last_rotated_key": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            "last_rotated_at": "2025-01-02T00:00:00Z",
        }
        mock_http_client.add_response(
            f"/service_keys/{key_id}/rotate", rotated_response
        )

        key = mock_client.service_keys.rotate(key_id)

        assert key.api_key == "new_rotated_key_12345678901234567"
        assert key.last_rotated_key == "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        mock_http_client.assert_request_made("PUT", f"/service_keys/{key_id}/rotate")

    def test_activate_service_key_success(
        self, mock_client, mock_http_client, sample_service_key_response
    ):
        """Test activating a service key."""
        key_id = 123
        activated_response = {**sample_service_key_response, "status": "ACTIVE"}
        mock_http_client.add_response(
            f"/service_keys/{key_id}/activate", activated_response
        )

        key = mock_client.service_keys.activate(key_id)

        assert key.status == "ACTIVE"
        mock_http_client.assert_request_made("PUT", f"/service_keys/{key_id}/activate")

    def test_pause_service_key_success(
        self, mock_client, mock_http_client, sample_service_key_response
    ):
        """Test pausing a service key."""
        key_id = 123
        paused_response = {**sample_service_key_response, "status": "PAUSED"}
        mock_http_client.add_response(f"/service_keys/{key_id}/pause", paused_response)

        key = mock_client.service_keys.pause(key_id)

        assert key.status == "PAUSED"
        mock_http_client.assert_request_made("PUT", f"/service_keys/{key_id}/pause")


@pytest.mark.unit
class TestServiceKeyModels:
    """Unit tests for service key models."""

    def test_service_key_model_validation(self, sample_service_key_response):
        """Test ServiceKey model parses valid data correctly."""
        key = ServiceKey.model_validate(sample_service_key_response)

        assert key.id == 123
        assert key.name == "Test Service Key"
        assert key.status == "ACTIVE"
        assert key.api_key == "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        assert key.owner_id == 1
        assert key.org_id == 1

    def test_service_key_with_rotated_key(self):
        """Test ServiceKey model with rotated key data."""
        data = {
            **SAMPLE_SERVICE_KEY,
            "last_rotated_key": "old_key_value",
            "last_rotated_at": "2025-01-02T00:00:00Z",
        }
        key = ServiceKey.model_validate(data)

        assert key.last_rotated_key == "old_key_value"
        assert key.last_rotated_at is not None

    def test_service_key_create_model_serialization(self):
        """Test ServiceKeyCreate model serialization."""
        create_data = ServiceKeyCreate(
            name="My Key",
            description="My description",
        )

        data = create_data.model_dump(exclude_none=True)

        assert data["name"] == "My Key"
        assert data["description"] == "My description"

    def test_service_key_create_with_data_source(self):
        """Test ServiceKeyCreate model with data_source_id."""
        create_data = ServiceKeyCreate(
            name="Flow Key",
            description="Key for flow",
            data_source_id=456,
        )

        data = create_data.model_dump(exclude_none=True)

        assert data["data_source_id"] == 456

    def test_service_key_update_model_serialization(self):
        """Test ServiceKeyUpdate model serialization."""
        update_data = ServiceKeyUpdate(name="Updated Name")

        data = update_data.model_dump(exclude_none=True)

        assert data["name"] == "Updated Name"
        assert "description" not in data
