"""Unit tests for cluster endpoints resource."""

import pytest

from nexla_sdk.models.clusters.requests import (
    ClusterEndpointCreate,
    ClusterEndpointUpdate,
)
from nexla_sdk.models.clusters.responses import ClusterEndpoint
from tests.utils import assert_model_list_valid, assert_model_valid

# Sample response data
SAMPLE_CLUSTER_ENDPOINT = {
    "id": 456,
    "cluster_id": 123,
    "org_id": 1,
    "service": "data_ingestion",
    "protocol": "https",
    "host": "ingestion.example.com",
    "port": 443,
    "context": "/api/v1",
    "org": {"id": 1, "name": "Test Org", "email_domain": "example.com"},
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
}

SAMPLE_ENDPOINTS_LIST = [
    SAMPLE_CLUSTER_ENDPOINT,
    {**SAMPLE_CLUSTER_ENDPOINT, "id": 457, "service": "metrics"},
    {**SAMPLE_CLUSTER_ENDPOINT, "id": 458, "service": "transform"},
]


@pytest.fixture
def sample_endpoint_response():
    """Sample cluster endpoint response."""
    return SAMPLE_CLUSTER_ENDPOINT.copy()


@pytest.fixture
def sample_endpoints_list():
    """Sample cluster endpoints list response."""
    return [e.copy() for e in SAMPLE_ENDPOINTS_LIST]


@pytest.mark.unit
class TestClusterEndpointsResource:
    """Unit tests for ClusterEndpointsResource using mocks."""

    def test_list_endpoints_success(
        self, mock_client, mock_http_client, sample_endpoints_list
    ):
        """Test listing cluster endpoints with successful response."""
        mock_http_client.add_response("/cluster_endpoints", sample_endpoints_list)

        endpoints = mock_client.cluster_endpoints.list()

        assert len(endpoints) == 3
        assert_model_list_valid(endpoints, ClusterEndpoint)
        mock_http_client.assert_request_made("GET", "/cluster_endpoints")

    def test_list_endpoints_with_pagination(
        self, mock_client, mock_http_client, sample_endpoints_list
    ):
        """Test listing endpoints with pagination."""
        mock_http_client.add_response("/cluster_endpoints", sample_endpoints_list)

        endpoints = mock_client.cluster_endpoints.list(page=1, per_page=10)

        assert len(endpoints) == 3
        request = mock_http_client.get_request()
        assert "page" in str(request) or "per_page" in str(request)

    def test_get_endpoint_success(
        self, mock_client, mock_http_client, sample_endpoint_response
    ):
        """Test getting a single cluster endpoint."""
        endpoint_id = 456
        mock_http_client.add_response(
            f"/cluster_endpoints/{endpoint_id}", sample_endpoint_response
        )

        endpoint = mock_client.cluster_endpoints.get(endpoint_id)

        assert_model_valid(endpoint, {"id": endpoint_id})
        mock_http_client.assert_request_made("GET", f"/cluster_endpoints/{endpoint_id}")

    def test_create_endpoint_success(
        self, mock_client, mock_http_client, sample_endpoint_response
    ):
        """Test creating a cluster endpoint."""
        mock_http_client.add_response("/cluster_endpoints", sample_endpoint_response)

        create_data = ClusterEndpointCreate(
            cluster_id=123,
            service="data_ingestion",
            protocol="https",
            host="ingestion.example.com",
            port=443,
        )
        endpoint = mock_client.cluster_endpoints.create(create_data)

        assert_model_valid(endpoint, {"service": "data_ingestion"})
        mock_http_client.assert_request_made("POST", "/cluster_endpoints")

    def test_update_endpoint_success(
        self, mock_client, mock_http_client, sample_endpoint_response
    ):
        """Test updating a cluster endpoint."""
        endpoint_id = 456
        updated_response = {**sample_endpoint_response, "host": "new-host.example.com"}
        mock_http_client.add_response(
            f"/cluster_endpoints/{endpoint_id}", updated_response
        )

        update_data = ClusterEndpointUpdate(host="new-host.example.com")
        endpoint = mock_client.cluster_endpoints.update(endpoint_id, update_data)

        assert endpoint.host == "new-host.example.com"
        mock_http_client.assert_request_made("PUT", f"/cluster_endpoints/{endpoint_id}")

    def test_get_audit_log_success(self, mock_client, mock_http_client):
        """Test getting audit log for an endpoint."""
        endpoint_id = 456
        audit_log = [
            {"action": "create", "timestamp": "2025-01-01T00:00:00Z"},
            {"action": "update", "timestamp": "2025-01-02T00:00:00Z"},
        ]
        mock_http_client.add_response(
            f"/cluster_endpoints/{endpoint_id}/audit_log", audit_log
        )

        result = mock_client.cluster_endpoints.get_audit_log(endpoint_id)

        assert len(result) == 2
        mock_http_client.assert_request_made(
            "GET", f"/cluster_endpoints/{endpoint_id}/audit_log"
        )

    def test_get_audit_log_with_pagination(self, mock_client, mock_http_client):
        """Test getting audit log with pagination."""
        endpoint_id = 456
        audit_log = [{"action": "create", "timestamp": "2025-01-01T00:00:00Z"}]
        mock_http_client.add_response(
            f"/cluster_endpoints/{endpoint_id}/audit_log", audit_log
        )

        result = mock_client.cluster_endpoints.get_audit_log(
            endpoint_id, page=1, per_page=10
        )

        assert len(result) == 1
        request = mock_http_client.get_request()
        assert "page" in str(request) or "per_page" in str(request)


@pytest.mark.unit
class TestClusterEndpointModels:
    """Unit tests for cluster endpoint models."""

    def test_endpoint_model_validation(self, sample_endpoint_response):
        """Test ClusterEndpoint model parses valid data correctly."""
        endpoint = ClusterEndpoint.model_validate(sample_endpoint_response)

        assert endpoint.id == 456
        assert endpoint.cluster_id == 123
        assert endpoint.service == "data_ingestion"
        assert endpoint.protocol == "https"
        assert endpoint.host == "ingestion.example.com"
        assert endpoint.port == 443

    def test_endpoint_model_with_minimal_data(self):
        """Test ClusterEndpoint model with minimal required fields."""
        minimal_data = {
            "id": 1,
        }
        endpoint = ClusterEndpoint.model_validate(minimal_data)

        assert endpoint.id == 1
        assert endpoint.service is None
        assert endpoint.host is None

    def test_endpoint_create_model_serialization(self):
        """Test ClusterEndpointCreate model serialization."""
        create_data = ClusterEndpointCreate(
            cluster_id=123,
            service="data_ingestion",
            protocol="https",
            host="api.example.com",
            port=443,
        )

        data = create_data.model_dump(exclude_none=True)

        assert data["cluster_id"] == 123
        assert data["service"] == "data_ingestion"
        assert data["protocol"] == "https"
        assert data["host"] == "api.example.com"
        assert data["port"] == 443

    def test_endpoint_update_model_serialization(self):
        """Test ClusterEndpointUpdate model serialization."""
        update_data = ClusterEndpointUpdate(
            host="new-host.example.com",
            port=8443,
        )

        data = update_data.model_dump(exclude_none=True)

        assert data["host"] == "new-host.example.com"
        assert data["port"] == 8443
        assert "cluster_id" not in data
        assert "service" not in data
