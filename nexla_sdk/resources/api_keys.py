"""Resource for managing API keys (read-only)."""

from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.api_keys.responses import ApiKey, ApiKeysIndex
from nexla_sdk.resources.base_resource import BaseResource


class ApiKeysResource(BaseResource):
    """Resource for API keys (read-only access).

    API keys provide programmatic access to specific resources like
    datasets, data sources, data sinks, and users.

    Note:
        This resource only supports ``list()``, ``list_grouped()``,
        ``get()``, and ``search()``. Write operations inherited from
        ``BaseResource`` (e.g. ``create``, ``update``, ``delete``) are
        not supported by the backend and will raise ``NotImplementedError``.

    Examples:
        # List all API keys (grouped by type)
        all_keys = client.api_keys.list_grouped()

        # Get a specific API key
        key = client.api_keys.get(123)

        # Search API keys
        keys = client.api_keys.search({"scope": "read"})
    """

    _NOT_SUPPORTED_MSG = (
        "API keys are read-only. Create, update, and delete operations "
        "are not supported. Manage API keys through their parent resources."
    )

    def __init__(self, client):
        """Initialize the API keys resource.

        Args:
            client: Nexla client instance
        """
        super().__init__(client)
        self._path = "/api_keys"
        self._model_class = ApiKey

    def list(
        self,
        access_role: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs,
    ) -> List[ApiKey]:
        """List API keys.

        Args:
            access_role: Filter by access role
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            List of API keys
        """
        params = kwargs.copy()
        if access_role is not None:
            params["access_role"] = access_role
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        response = self._make_request("GET", self._path, params=params)
        return self._parse_response(response)

    def list_grouped(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> ApiKeysIndex:
        """List API keys grouped by resource type.

        Returns API keys organized by their resource type:
        data_sets, data_sinks, data_sources, and users.

        Args:
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            ApiKeysIndex with grouped API keys
        """
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        response = self._make_request("GET", self._path, params=params)
        return ApiKeysIndex.model_validate(response)

    def get(self, api_key_id: Union[int, str]) -> ApiKey:
        """Get API key by ID or key value.

        Args:
            api_key_id: API key ID (int) or api_key value (string)

        Returns:
            ApiKey instance
        """
        path = f"{self._path}/{api_key_id}"
        response = self._make_request("GET", path)
        return self._parse_response(response)

    def search(
        self,
        filters: Dict[str, Any],
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[ApiKey]:
        """Search API keys with filters.

        Args:
            filters: Search filters
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            List of matching API keys
        """
        path = f"{self._path}/search"
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        response = self._make_request("POST", path, json=filters, params=params)
        return [ApiKey.model_validate(k) for k in response]

    def create(self, data=None):
        raise NotImplementedError(self._NOT_SUPPORTED_MSG)

    def update(self, resource_id=None, data=None):
        raise NotImplementedError(self._NOT_SUPPORTED_MSG)

    def delete(self, resource_id=None):
        raise NotImplementedError(self._NOT_SUPPORTED_MSG)

    def copy(self, resource_id=None, options=None):
        raise NotImplementedError(self._NOT_SUPPORTED_MSG)

    def activate(self, resource_id=None):
        raise NotImplementedError(self._NOT_SUPPORTED_MSG)

    def pause(self, resource_id=None):
        raise NotImplementedError(self._NOT_SUPPORTED_MSG)
