"""Resource for managing clusters."""

from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.clusters.requests import ClusterCreate, ClusterUpdate
from nexla_sdk.models.clusters.responses import Cluster
from nexla_sdk.resources.base_resource import BaseResource


class ClustersResource(BaseResource):
    """Resource for managing clusters.

    Clusters define infrastructure endpoints for processing data flows.
    This resource requires super user access for most operations.

    Examples:
        # List clusters
        clusters = client.clusters.list()

        # Get a specific cluster
        cluster = client.clusters.get(123)

        # Create a cluster
        cluster = client.clusters.create(ClusterCreate(
            org_id=1,
            name="Production Cluster",
            region="us-west-2",
            provider="aws"
        ))

        # Activate a cluster
        client.clusters.activate(cluster.id)

        # Set as default cluster
        client.clusters.set_default(cluster.id)
    """

    def __init__(self, client):
        """Initialize the clusters resource.

        Args:
            client: Nexla client instance
        """
        super().__init__(client)
        self._path = "/clusters"
        self._model_class = Cluster

    def list(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        access_role: Optional[str] = None,
        **kwargs,
    ) -> List[Cluster]:
        """List clusters.

        Args:
            page: Page number (1-based)
            per_page: Items per page
            access_role: Filter by access role (owner, collaborator, operator, admin)

        Returns:
            List of clusters
        """
        return super().list(
            page=page, per_page=per_page, access_role=access_role, **kwargs
        )

    def get(self, cluster_id: int, expand: bool = False) -> Cluster:
        """Get cluster by ID.

        Args:
            cluster_id: Cluster ID
            expand: Include expanded references

        Returns:
            Cluster instance
        """
        return super().get(cluster_id, expand=expand)

    def create(self, data: Union[ClusterCreate, Dict[str, Any]]) -> Cluster:
        """Create a new cluster.

        Args:
            data: Cluster creation data (requires org_id, name, and region)

        Returns:
            Created cluster
        """
        return super().create(data)

    def update(
        self, cluster_id: int, data: Union[ClusterUpdate, Dict[str, Any]]
    ) -> Cluster:
        """Update a cluster.

        Args:
            cluster_id: Cluster ID
            data: Updated cluster data

        Returns:
            Updated cluster
        """
        return super().update(cluster_id, data)

    def delete(self, cluster_id: int) -> Dict[str, Any]:
        """Delete a cluster.

        Args:
            cluster_id: Cluster ID

        Returns:
            Response with status
        """
        return super().delete(cluster_id)

    def activate(self, cluster_id: int) -> Cluster:
        """Activate a cluster.

        Args:
            cluster_id: Cluster ID

        Returns:
            Activated cluster
        """
        return super().activate(cluster_id)

    def set_default(self, cluster_id: int) -> Cluster:
        """Set a cluster as the default.

        The cluster must be available (active, belongs to Nexla org,
        and is not private).

        Args:
            cluster_id: Cluster ID

        Returns:
            Updated cluster
        """
        path = f"{self._path}/default/{cluster_id}"
        response = self._make_request("PUT", path)
        return self._parse_response(response)

    def delete_endpoint(self, cluster_id: int, endpoint_id: int) -> Dict[str, Any]:
        """Delete an endpoint from a cluster.

        Args:
            cluster_id: Cluster ID
            endpoint_id: Endpoint ID

        Returns:
            Response with status
        """
        path = f"{self._path}/{cluster_id}/endpoints/{endpoint_id}"
        return self._make_request("DELETE", path)
