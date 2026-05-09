"""Resource for managing service keys."""

from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.service_keys.requests import ServiceKeyCreate, ServiceKeyUpdate
from nexla_sdk.models.service_keys.responses import ServiceKey
from nexla_sdk.resources.base_resource import BaseResource


class ServiceKeysResource(BaseResource):
    """Resource for managing service keys.

    Service keys are long-lived credentials for programmatic API access.
    Unlike session tokens, service keys don't expire but can be rotated
    and have lifecycle management (activate/pause).

    Examples:
        # List service keys
        keys = client.service_keys.list()

        # List all keys in org (admin only)
        all_keys = client.service_keys.list(all_keys=True)

        # Create a service key
        key = client.service_keys.create(ServiceKeyCreate(
            name="My Service Key",
            description="For automated pipelines"
        ))

        # Rotate a key
        rotated_key = client.service_keys.rotate(key.id)

        # Pause a key
        client.service_keys.pause(key.id)
    """

    def __init__(self, client):
        """Initialize the service keys resource.

        Args:
            client: Nexla client instance
        """
        super().__init__(client)
        self._path = "/service_keys"
        self._model_class = ServiceKey

    def list(
        self,
        access_role: Optional[str] = None,
        all_keys: bool = False,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs,
    ) -> List[ServiceKey]:
        """List service keys.

        Args:
            access_role: Filter by access role
            all_keys: If True and user has admin access, list all keys in org.
                      Super users can see all keys across orgs.
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            List of service keys
        """
        params = kwargs.copy()
        if access_role is not None:
            params["access_role"] = access_role
        if all_keys:
            params["all"] = True
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        response = self._make_request("GET", self._path, params=params)
        return self._parse_response(response)

    def get(self, key_id: Union[int, str]) -> ServiceKey:
        """Get service key by ID or key value.

        Args:
            key_id: Service key ID (int) or the api_key string itself

        Returns:
            ServiceKey instance
        """
        path = f"{self._path}/{key_id}"
        response = self._make_request("GET", path)
        return self._parse_response(response)

    def create(self, data: Union[ServiceKeyCreate, Dict[str, Any]]) -> ServiceKey:
        """Create a new service key.

        Args:
            data: Service key creation data (name and description required)

        Returns:
            Created service key with the api_key value
        """
        return super().create(data)

    def update(
        self, key_id: Union[int, str], data: Union[ServiceKeyUpdate, Dict[str, Any]]
    ) -> ServiceKey:
        """Update a service key.

        Args:
            key_id: Service key ID or api_key string
            data: Updated service key data

        Returns:
            Updated service key
        """
        path = f"{self._path}/{key_id}"
        serialized_data = self._serialize_data(data)
        response = self._make_request("PUT", path, json=serialized_data)
        return self._parse_response(response)

    def delete(self, key_id: Union[int, str]) -> Dict[str, Any]:
        """Delete a service key.

        Note: Cannot delete a service key that is associated with an active
        data source/flow. Returns 405 Method Not Allowed in that case.

        Args:
            key_id: Service key ID or api_key string

        Returns:
            Response with status
        """
        path = f"{self._path}/{key_id}"
        return self._make_request("DELETE", path)

    def rotate(self, key_id: Union[int, str]) -> ServiceKey:
        """Rotate a service key to generate a new key value.

        The old key becomes invalid immediately. The previous key value
        is stored in `last_rotated_key` for reference.

        Args:
            key_id: Service key ID or api_key string

        Returns:
            Service key with the new api_key value
        """
        path = f"{self._path}/{key_id}/rotate"
        response = self._make_request("PUT", path)
        return self._parse_response(response)

    def activate(self, key_id: Union[int, str]) -> ServiceKey:
        """Activate a paused service key.

        Args:
            key_id: Service key ID or api_key string

        Returns:
            Activated service key
        """
        path = f"{self._path}/{key_id}/activate"
        response = self._make_request("PUT", path)
        return self._parse_response(response)

    def pause(self, key_id: Union[int, str]) -> ServiceKey:
        """Pause a service key (temporarily disable).

        A paused key cannot be used for authentication until reactivated.

        Args:
            key_id: Service key ID or api_key string

        Returns:
            Paused service key
        """
        path = f"{self._path}/{key_id}/pause"
        response = self._make_request("PUT", path)
        return self._parse_response(response)
