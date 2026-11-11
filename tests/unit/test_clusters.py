"""Unit tests for clusters resource."""

import pytest

from nexla_sdk.models.clusters.requests import (
    ClusterCreate,
    ClusterEndpointItem,
    ClusterUpdate,
)
from nexla_sdk.models.clusters.responses import Cluster
from tests.utils import assert_model_list_valid, assert_model_valid

# Sample response data
SAMPLE_CLUSTER = {
    "id": 123,
    "org_id": 1,
    "uid": "cluster-uid-123",
    "is_default": False,
    "is_private": False,
    "name": "Production Cluster",
    "description": "Main production cluster",
    "status": "ACTIVE",
    "region": "us-west-2",
    "provider": "aws",
    "org": {"id": 1, "name": "Test Org", "email_domain": "example.com"},
    "endpoints": [
        {
            "id": 1,
            "service": "data_ingestion",
            "protocol": "https",
            "host": "ingestion.example.com",
            "port": 443,
        }
    ],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
}

SAMPLE_CLUSTERS_LIST = [
    SAMPLE_CLUSTER,
    {**SAMPLE_CLUSTER, "id": 124, "name": "Staging Cluster"},
    {**SAMPLE_CLUSTER, "id": 125, "name": "Dev Cluster"},
]


@pytest.fixture
def sample_cluster_response():
    """Sample cluster response."""
    return SAMPLE_CLUSTER.copy()


@pytest.fixture
def sample_clusters_list():
    """Sample clusters list response."""
    return [c.copy() for c in SAMPLE_CLUSTERS_LIST]


@pytest.mark.unit
class TestClustersResource:
    """Unit tests for ClustersResource using mocks."""

    def test_list_clusters_success(
        self, mock_client, mock_http_client, sample_clusters_list
    ):
        """Test listing clusters with successful response."""
        mock_http_client.add_response("/clusters", sample_clusters_list)

        clusters = mock_client.clusters.list()

        assert len(clusters) == 3
        assert_model_list_valid(clusters, Cluster)
        mock_http_client.assert_request_made("GET", "/clusters")

    def test_list_clusters_with_pagination(
        self, mock_client, mock_http_client, sample_clusters_list
    ):
        """Test listing clusters with pagination."""
        mock_http_client.add_response("/clusters", sample_clusters_list)

        clusters = mock_client.clusters.list(page=1, per_page=10)

        assert len(clusters) == 3
        request = mock_http_client.get_request()
        assert "page" in str(request) or "per_page" in str(request)

    def test_get_cluster_success(
        self, mock_client, mock_http_client, sample_cluster_response
    ):
        """Test getting a single cluster."""
        cluster_id = 123
        mock_http_client.add_response(
            f"/clusters/{cluster_id}", sample_cluster_response
        )

        cluster = mock_client.clusters.get(cluster_id)

        assert_model_valid(cluster, {"id": cluster_id})
        mock_http_client.assert_request_made("GET", f"/clusters/{cluster_id}")

    def test_create_cluster_success(
        self, mock_client, mock_http_client, sample_cluster_response
    ):
        """Test creating a cluster."""
        mock_http_client.add_response("/clusters", sample_cluster_response)

        create_data = ClusterCreate(
            org_id=1,
            name="Production Cluster",
            region="us-west-2",
            provider="aws",
        )
        cluster = mock_client.clusters.create(create_data)

        assert_model_valid(cluster, {"name": "Production Cluster"})
        mock_http_client.assert_request_made("POST", "/clusters")

    def test_create_cluster_with_endpoints(
        self, mock_client, mock_http_client, sample_cluster_response
    ):
        """Test creating a cluster with endpoints."""
        mock_http_client.add_response("/clusters", sample_cluster_response)

        create_data = ClusterCreate(
            org_id=1,
            name="Production Cluster",
            region="us-west-2",
            endpoints=[
                ClusterEndpointItem(
                    service="data_ingestion",
                    protocol="https",
                    host="ingestion.example.com",
                    port=443,
                )
            ],
        )
        cluster = mock_client.clusters.create(create_data)

        assert cluster.endpoints is not None
        mock_http_client.assert_request_made("POST", "/clusters")

    def test_update_cluster_success(
        self, mock_client, mock_http_client, sample_cluster_response
    ):
        """Test updating a cluster."""
        cluster_id = 123
        updated_response = {**sample_cluster_response, "name": "Updated Cluster"}
        mock_http_client.add_response(f"/clusters/{cluster_id}", updated_response)

        update_data = ClusterUpdate(name="Updated Cluster")
        cluster = mock_client.clusters.update(cluster_id, update_data)

        assert cluster.name == "Updated Cluster"
        mock_http_client.assert_request_made("PUT", f"/clusters/{cluster_id}")

    def test_delete_cluster_success(self, mock_client, mock_http_client):
        """Test deleting a cluster."""
        cluster_id = 123
        mock_http_client.add_response(f"/clusters/{cluster_id}", {"success": True})

        result = mock_client.clusters.delete(cluster_id)

        assert result["success"] is True
        mock_http_client.assert_request_made("DELETE", f"/clusters/{cluster_id}")

    def test_activate_cluster_success(
        self, mock_client, mock_http_client, sample_cluster_response
    ):
        """Test activating a cluster."""
        cluster_id = 123
        active_response = {**sample_cluster_response, "status": "ACTIVE"}
        mock_http_client.add_response(
            f"/clusters/{cluster_id}/activate", active_response
        )

        cluster = mock_client.clusters.activate(cluster_id)

        assert cluster.status == "ACTIVE"
        mock_http_client.assert_request_made("PUT", f"/clusters/{cluster_id}/activate")

    def test_set_default_cluster_success(
        self, mock_client, mock_http_client, sample_cluster_response
    ):
        """Test setting a cluster as default."""
        cluster_id = 123
        default_response = {**sample_cluster_response, "is_default": True}
        mock_http_client.add_response(
            f"/clusters/default/{cluster_id}", default_response
        )

        cluster = mock_client.clusters.set_default(cluster_id)

        assert cluster.is_default is True
        mock_http_client.assert_request_made("PUT", f"/clusters/default/{cluster_id}")

    def test_delete_endpoint_success(self, mock_client, mock_http_client):
        """Test deleting a cluster endpoint."""
        cluster_id = 123
        endpoint_id = 456
        mock_http_client.add_response(
            f"/clusters/{cluster_id}/endpoints/{endpoint_id}", {"success": True}
        )

        result = mock_client.clusters.delete_endpoint(cluster_id, endpoint_id)

        assert result["success"] is True
        mock_http_client.assert_request_made(
            "DELETE", f"/clusters/{cluster_id}/endpoints/{endpoint_id}"
        )


@pytest.mark.unit
class TestClusterModels:
    """Unit tests for cluster models."""

    def test_cluster_model_validation(self, sample_cluster_response):
        """Test Cluster model parses valid data correctly."""
        cluster = Cluster.model_validate(sample_cluster_response)

        assert cluster.id == 123
        assert cluster.name == "Production Cluster"
        assert cluster.status == "ACTIVE"
        assert cluster.region == "us-west-2"
        assert cluster.provider == "aws"
        assert len(cluster.endpoints) == 1

    def test_cluster_model_with_minimal_data(self):
        """Test Cluster model with minimal required fields."""
        minimal_data = {
            "id": 1,
        }
        cluster = Cluster.model_validate(minimal_data)

        assert cluster.id == 1
        assert cluster.name is None
        assert cluster.endpoints == []

    def test_cluster_create_model_serialization(self):
        """Test ClusterCreate model serialization."""
        create_data = ClusterCreate(
            org_id=1,
            name="My Cluster",
            region="us-east-1",
            provider="aws",
            description="Test cluster",
        )

        data = create_data.model_dump(exclude_none=True)

        assert data["org_id"] == 1
        assert data["name"] == "My Cluster"
        assert data["region"] == "us-east-1"
        assert data["provider"] == "aws"

    def test_cluster_create_with_endpoints_serialization(self):
        """Test ClusterCreate with endpoints serialization."""
        create_data = ClusterCreate(
            org_id=1,
            name="My Cluster",
            region="us-east-1",
            endpoints=[
                ClusterEndpointItem(
                    service="data_ingestion",
                    protocol="https",
                    host="api.example.com",
                    port=443,
                )
            ],
        )

        data = create_data.model_dump(exclude_none=True)

        assert "endpoints" in data
        assert len(data["endpoints"]) == 1
        assert data["endpoints"][0]["service"] == "data_ingestion"

    def test_cluster_update_model_serialization(self):
        """Test ClusterUpdate model serialization."""
        update_data = ClusterUpdate(
            name="Updated Name",
            description="Updated description",
        )

        data = update_data.model_dump(exclude_none=True)

        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"
        assert "region" not in data
