"""Unit tests for API keys resource."""

import pytest

from nexla_sdk.models.api_keys.responses import ApiKey, ApiKeysIndex
from tests.utils import assert_model_list_valid, assert_model_valid

# Sample response data
SAMPLE_API_KEY = {
    "id": 123,
    "owner_id": 1,
    "org_id": 1,
    "data_set_id": 456,
    "name": "Dataset API Key",
    "description": "API key for dataset access",
    "status": "active",
    "scope": "read",
    "api_key": "ak_test_abc123",
    "url": "https://api.nexla.com/v1/data_sets/456",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
}

SAMPLE_API_KEYS_LIST = [
    SAMPLE_API_KEY,
    {**SAMPLE_API_KEY, "id": 124, "name": "Another API Key"},
    {**SAMPLE_API_KEY, "id": 125, "name": "Third API Key"},
]

SAMPLE_API_KEYS_GROUPED = {
    "data_sets": [SAMPLE_API_KEY],
    "data_sinks": [],
    "data_sources": [],
    "users": [],
}


@pytest.fixture
def sample_api_key_response():
    """Sample API key response."""
    return SAMPLE_API_KEY.copy()


@pytest.fixture
def sample_api_keys_list():
    """Sample API keys list response."""
    return [k.copy() for k in SAMPLE_API_KEYS_LIST]


@pytest.fixture
def sample_api_keys_grouped():
    """Sample grouped API keys response."""
    return SAMPLE_API_KEYS_GROUPED.copy()


@pytest.mark.unit
class TestApiKeysResource:
    """Unit tests for ApiKeysResource using mocks."""

    def test_list_api_keys_success(
        self, mock_client, mock_http_client, sample_api_keys_list
    ):
        """Test listing API keys with successful response."""
        mock_http_client.add_response("/api_keys", sample_api_keys_list)

        keys = mock_client.api_keys.list()

        assert len(keys) == 3
        assert_model_list_valid(keys, ApiKey)
        mock_http_client.assert_request_made("GET", "/api_keys")

    def test_list_grouped_api_keys_success(
        self, mock_client, mock_http_client, sample_api_keys_grouped
    ):
        """Test listing grouped API keys."""
        mock_http_client.add_response("/api_keys", sample_api_keys_grouped)

        result = mock_client.api_keys.list_grouped()

        assert isinstance(result, ApiKeysIndex)
        assert len(result.data_sets) == 1
        mock_http_client.assert_request_made("GET", "/api_keys")

    def test_get_api_key_success(
        self, mock_client, mock_http_client, sample_api_key_response
    ):
        """Test getting a single API key."""
        key_id = 123
        mock_http_client.add_response(f"/api_keys/{key_id}", sample_api_key_response)

        key = mock_client.api_keys.get(key_id)

        assert_model_valid(key, {"id": key_id})
        mock_http_client.assert_request_made("GET", f"/api_keys/{key_id}")

    def test_get_api_key_by_value(
        self, mock_client, mock_http_client, sample_api_key_response
    ):
        """Test getting an API key by its value."""
        key_value = "ak_test_abc123"
        mock_http_client.add_response(f"/api_keys/{key_value}", sample_api_key_response)

        key = mock_client.api_keys.get(key_value)

        assert key.api_key == key_value
        mock_http_client.assert_request_made("GET", f"/api_keys/{key_value}")

    def test_search_api_keys_success(
        self, mock_client, mock_http_client, sample_api_keys_list
    ):
        """Test searching API keys."""
        mock_http_client.add_response("/api_keys/search", sample_api_keys_list)

        filters = {"scope": "read"}
        keys = mock_client.api_keys.search(filters)

        assert len(keys) == 3
        mock_http_client.assert_request_made("POST", "/api_keys/search")


@pytest.mark.unit
class TestApiKeyModels:
    """Unit tests for API key models."""

    def test_api_key_model_validation(self, sample_api_key_response):
        """Test ApiKey model parses valid data correctly."""
        key = ApiKey.model_validate(sample_api_key_response)

        assert key.id == 123
        assert key.name == "Dataset API Key"
        assert key.scope == "read"
        assert key.api_key == "ak_test_abc123"

    def test_api_keys_index_model_validation(self, sample_api_keys_grouped):
        """Test ApiKeysIndex model parses valid data correctly."""
        index = ApiKeysIndex.model_validate(sample_api_keys_grouped)

        assert len(index.data_sets) == 1
        assert len(index.data_sinks) == 0

    def test_api_key_model_with_minimal_data(self):
        """Test ApiKey model with minimal required fields."""
        minimal_data = {
            "id": 1,
        }
        key = ApiKey.model_validate(minimal_data)

        assert key.id == 1
        assert key.name is None
        assert key.api_key is None


@pytest.mark.unit
class TestApiKeysUnsupportedOperations:
    """Test that unsupported write operations raise NotImplementedError."""

    def test_create_raises_not_implemented(self, mock_client):
        with pytest.raises(NotImplementedError, match="read-only"):
            mock_client.api_keys.create({"name": "test"})

    def test_update_raises_not_implemented(self, mock_client):
        with pytest.raises(NotImplementedError, match="read-only"):
            mock_client.api_keys.update(123, {"name": "test"})

    def test_delete_raises_not_implemented(self, mock_client):
        with pytest.raises(NotImplementedError, match="read-only"):
            mock_client.api_keys.delete(123)

    def test_copy_raises_not_implemented(self, mock_client):
        with pytest.raises(NotImplementedError, match="read-only"):
            mock_client.api_keys.copy(123)

    def test_activate_raises_not_implemented(self, mock_client):
        with pytest.raises(NotImplementedError, match="read-only"):
            mock_client.api_keys.activate(123)

    def test_pause_raises_not_implemented(self, mock_client):
        with pytest.raises(NotImplementedError, match="read-only"):
            mock_client.api_keys.pause(123)
