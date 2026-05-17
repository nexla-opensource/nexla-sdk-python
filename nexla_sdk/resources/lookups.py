"""Lookups resource implementation."""

from typing import Any, Dict, List, Union

from nexla_sdk.models.lookups.requests import (
    LookupCreate,
    LookupEntriesUpsert,
    LookupUpdate,
)
from nexla_sdk.models.lookups.responses import Lookup
from nexla_sdk.resources.base_resource import BaseResource


class LookupsResource(BaseResource):
    """Resource for managing lookups (data maps)."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/data_maps"
        self._model_class = Lookup

    def list(self, **kwargs) -> List[Lookup]:
        """
        List lookups with optional filters.

        Args:
            page: Page number (via kwargs)
            per_page: Items per page (via kwargs)
            access_role: Filter by access role (via kwargs)
            **kwargs: Additional query parameters

        Returns:
            List of lookups

        Examples:
            client.lookups.list(page=1, per_page=50)
        """
        return super().list(**kwargs)

    def list_public(self, **params) -> List[Lookup]:
        response = self._make_request("GET", f"{self._path}/public", params=params)
        return self._parse_response(response)

    def list_accessible(self, **params) -> List[Lookup]:
        return super().list_accessible(**params)

    def get(self, data_map_id: int, expand: bool = False) -> Lookup:
        """
        Get single lookup by ID.

        Args:
            data_map_id: Lookup ID
            expand: Include expanded references

        Returns:
            Lookup instance

        Examples:
            client.lookups.get(55)
        """
        return super().get(data_map_id, expand)

    def create(self, data: LookupCreate) -> Lookup:
        """
        Create new lookup.

        Args:
            data: Lookup creation data

        Returns:
            Created lookup

        Examples:
            client.lookups.create(LookupCreate(name="status-map", ...))
        """
        return super().create(data)

    def update(self, data_map_id: int, data: LookupUpdate) -> Lookup:
        """
        Update lookup.

        Args:
            data_map_id: Lookup ID
            data: Updated lookup data

        Returns:
            Updated lookup
        """
        return super().update(data_map_id, data)

    def delete(self, data_map_id: int) -> Dict[str, Any]:
        """
        Delete lookup.

        Args:
            data_map_id: Lookup ID

        Returns:
            Response with status
        """
        return super().delete(data_map_id)

    def search(self, filters: Dict[str, Any], **params) -> List[Lookup]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params) -> List[Lookup]:
        return super().search_tags(tags, **params)

    def validate(self, data_map_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{data_map_id}/validate"
        return self._make_request("GET", path)

    def download_map(self, data_map_id: int) -> str:
        path = f"{self._path}/{data_map_id}/download_map"
        response = self._make_request("GET", path)
        return response  # plain text response

    def upsert_entries(
        self, data_map_id: int, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Upsert entries in a lookup.

        Args:
            data_map_id: Lookup ID
            entries: List of entries to upsert

        Returns:
            Response with entry results
        """
        path = f"{self._path}/{data_map_id}/entries"

        # Create request model
        request = LookupEntriesUpsert(entries=entries)

        return self._make_request("PUT", path, json=request.to_dict())

    def get_entries(
        self, data_map_id: int, entry_keys: Union[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Get specific entries from a lookup.

        Args:
            data_map_id: Lookup ID
            entry_keys: Single key or list of keys to retrieve

        Returns:
            List of matching entries
        """
        if isinstance(entry_keys, list):
            keys_str = ",".join(str(key) for key in entry_keys)
        else:
            keys_str = str(entry_keys)

        path = f"/data_maps/{data_map_id}/entries/{keys_str}"
        return self._make_request("GET", path)

    def get_entries_by_body(
        self, data_map_id: int, payload: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        path = f"{self._path}/{data_map_id}/get_entries"
        return self._make_request("POST", path, json=payload)

    def delete_entries(
        self, data_map_id: int, entry_keys: Union[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Delete specific entries from a lookup.

        Args:
            data_map_id: Lookup ID
            entry_keys: Single key or list of keys to delete

        Returns:
            Response with deletion results
        """
        if isinstance(entry_keys, list):
            keys_str = ",".join(str(key) for key in entry_keys)
        else:
            keys_str = str(entry_keys)

        path = f"/data_maps/{data_map_id}/entries/{keys_str}"
        return self._make_request("DELETE", path)

    def delete_entries_by_body(
        self, data_map_id: int, entry_keys: List[str]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{data_map_id}/entries"
        return self._make_request("DELETE", path, json=entry_keys)

    def probe_sample(self, data_map_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{data_map_id}/probe/sample"
        return self._make_request("POST", path, json=payload)
