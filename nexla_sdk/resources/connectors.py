"""Resource for managing connectors."""

from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.connectors.requests import ConnectorUpdate
from nexla_sdk.models.connectors.responses import Connector
from nexla_sdk.resources.base_resource import BaseResource


class ConnectorsResource(BaseResource):
    """Resource for managing connectors.

    Connectors define connection types for data sources and destinations.
    The backend only supports list, get, and update operations.

    Read access requires Nexla admin org membership.
    Update operations require super user access.

    Note:
        This resource only supports ``list()``, ``get()``, and ``update()``.
        Other write operations inherited from ``BaseResource`` (e.g.
        ``create``, ``delete``, ``copy``) are not supported by the backend
        and will raise ``NotImplementedError``.

    Examples:
        # List all connectors
        connectors = client.connectors.list()

        # Filter by API compatibility
        nexset_connectors = client.connectors.list(nexset_api_compatible=True)

        # Get a specific connector by ID
        connector = client.connectors.get(123)

        # Get a connector by type
        connector = client.connectors.get("s3")

        # Update a connector (super user only)
        connector = client.connectors.update(123, ConnectorUpdate(
            description="Updated description"
        ))
    """

    _NOT_SUPPORTED_MSG = (
        "Connectors only support list, get, and update operations. "
        "This method is not supported by the backend."
    )

    def __init__(self, client):
        """Initialize the connectors resource.

        Args:
            client: Nexla client instance
        """
        super().__init__(client)
        self._path = "/connectors"
        self._model_class = Connector

    def list(
        self,
        access_role: Optional[str] = None,
        nexset_api_compatible: Optional[bool] = None,
        sync_api_compatible: Optional[bool] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs,
    ) -> List[Connector]:
        """List connectors.

        Args:
            access_role: Filter by access role
            nexset_api_compatible: Filter by Nexset API compatibility
            sync_api_compatible: Filter by Sync API compatibility
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            List of connectors
        """
        params = kwargs.copy()
        if access_role is not None:
            params["access_role"] = access_role
        if nexset_api_compatible is not None:
            params["nexset_api_compatible"] = str(nexset_api_compatible).lower()
        if sync_api_compatible is not None:
            params["sync_api_compatible"] = str(sync_api_compatible).lower()
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        response = self._make_request("GET", self._path, params=params)
        return self._parse_response(response)

    def get(self, connector_id: Union[int, str]) -> Connector:
        """Get connector by ID or type.

        Args:
            connector_id: Connector ID (int) or type (string)

        Returns:
            Connector instance
        """
        path = f"{self._path}/{connector_id}"
        response = self._make_request("GET", path)
        return self._parse_response(response)

    def update(
        self,
        connector_id: Union[int, str],
        data: Union[ConnectorUpdate, Dict[str, Any]],
    ) -> Connector:
        """Update a connector (super user only).

        Args:
            connector_id: Connector ID or type
            data: Updated connector data

        Returns:
            Updated connector
        """
        path = f"{self._path}/{connector_id}"
        serialized_data = self._serialize_data(data)
        response = self._make_request("PUT", path, json=serialized_data)
        return self._parse_response(response)

    def create(self, data=None):
        raise NotImplementedError(self._NOT_SUPPORTED_MSG)

    def delete(self, resource_id=None):
        raise NotImplementedError(self._NOT_SUPPORTED_MSG)

    def copy(self, resource_id=None, options=None):
        raise NotImplementedError(self._NOT_SUPPORTED_MSG)

    def activate(self, resource_id=None):
        raise NotImplementedError(self._NOT_SUPPORTED_MSG)

    def pause(self, resource_id=None):
        raise NotImplementedError(self._NOT_SUPPORTED_MSG)
