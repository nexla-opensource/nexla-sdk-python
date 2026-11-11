"""Resource for managing cluster endpoints."""

from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.clusters.requests import (
    ClusterEndpointCreate,
    ClusterEndpointUpdate,
)
from nexla_sdk.models.clusters.responses import ClusterEndpoint
from nexla_sdk.resources.base_resource import BaseResource


class ClusterEndpointsResource(BaseResource):
    """Resource for managing cluster endpoints.

    Cluster endpoints define individual service connections within a cluster.
    Most operations require super user access.

    Examples:
        # List cluster endpoints
        endpoints = client.cluster_endpoints.list()

        # Get a specific endpoint
        endpoint = client.cluster_endpoints.get(123)

        # Create an endpoint
        endpoint = client.cluster_endpoints.create(ClusterEndpointCreate(
            cluster_id=456,
            service="data_ingestion",
            protocol="https",
            host="ingestion.example.com",
            port=443
        ))

        # Update an endpoint
        endpoint = client.cluster_endpoints.update(123, ClusterEndpointUpdate(
            host="new-ingestion.example.com"
        ))

        # Get audit log
        audit_log = client.cluster_endpoints.get_audit_log(123)
    """

    def __init__(self, client):
        """Initialize the cluster endpoints resource.

        Args:
            client: Nexla client instance
        """
        super().__init__(client)
        self._path = "/cluster_endpoints"
        self._model_class = ClusterEndpoint

    def list(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs,
    ) -> List[ClusterEndpoint]:
        """List cluster endpoints.

        Args:
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            List of cluster endpoints
        """
        return super().list(page=page, per_page=per_page, **kwargs)

    def get(self, endpoint_id: int) -> ClusterEndpoint:
        """Get cluster endpoint by ID.

        Args:
            endpoint_id: Endpoint ID

        Returns:
            ClusterEndpoint instance
        """
        path = f"{self._path}/{endpoint_id}"
        response = self._make_request("GET", path)
        return self._parse_response(response)

    def create(
        self, data: Union[ClusterEndpointCreate, Dict[str, Any]]
    ) -> ClusterEndpoint:
        """Create a new cluster endpoint.

        Args:
            data: Endpoint creation data (requires cluster_id and service)

        Returns:
            Created cluster endpoint
        """
        serialized_data = self._serialize_data(data)
        response = self._make_request("POST", self._path, json=serialized_data)
        return self._parse_response(response)

    def update(
        self, endpoint_id: int, data: Union[ClusterEndpointUpdate, Dict[str, Any]]
    ) -> ClusterEndpoint:
        """Update a cluster endpoint.

        Args:
            endpoint_id: Endpoint ID
            data: Updated endpoint data

        Returns:
            Updated cluster endpoint
        """
        path = f"{self._path}/{endpoint_id}"
        serialized_data = self._serialize_data(data)
        response = self._make_request("PUT", path, json=serialized_data)
        return self._parse_response(response)

    def get_audit_log(
        self,
        endpoint_id: int,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get audit log for a cluster endpoint.

        Args:
            endpoint_id: Endpoint ID
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            List of audit log entries
        """
        path = f"{self._path}/{endpoint_id}/audit_log"
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        return self._make_request("GET", path, params=params)
