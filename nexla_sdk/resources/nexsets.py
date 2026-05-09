from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.doc_containers import DocContainer, DocContainerInput
from nexla_sdk.models.nexsets.requests import (
    NexsetCopyOptions,
    NexsetCreate,
    NexsetUpdate,
)
from nexla_sdk.models.catalog_refs.responses import CatalogRef
from nexla_sdk.models.nexsets.responses import Nexset, NexsetSample
from nexla_sdk.resources.base_resource import BaseResource


class NexsetsResource(BaseResource):
    """Resource for managing nexsets (data sets)."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/data_sets"
        self._model_class = Nexset

    def list(self, **kwargs) -> List[Nexset]:
        """
        List nexsets with optional filters.

        Args:
            page: Page number (via kwargs)
            per_page: Items per page (via kwargs)
            access_role: Filter by access role (via kwargs)
            **kwargs: Additional query parameters

        Returns:
            List of nexsets

        Examples:
            client.nexsets.list(page=1, per_page=50)
        """
        return super().list(**kwargs)

    def list_all(self, **params) -> List[Nexset]:
        response = self._make_request("GET", f"{self._path}/all", params=params)
        return self._parse_response(response)

    def list_all_condensed(self, **params) -> List[Dict[str, Any]]:
        return self._make_request("GET", f"{self._path}/all/condensed", params=params)

    def list_all_ids(self, **params) -> List[int]:
        return self._make_request("GET", f"{self._path}/all/ids", params=params)

    def list_available(self, **params) -> List[Nexset]:
        response = self._make_request("GET", f"{self._path}/available", params=params)
        return self._parse_response(response)

    def search_available(self, filters: Dict[str, Any], **params) -> List[Nexset]:
        path = f"{self._path}/available/search"
        response = self._make_request("POST", path, json=filters, params=params)
        return self._parse_response(response)

    def list_shared(self, **params) -> List[Nexset]:
        response = self._make_request("GET", f"{self._path}/shared", params=params)
        return self._parse_response(response)

    def list_public(self, **params) -> List[Nexset]:
        response = self._make_request("GET", f"{self._path}/public", params=params)
        return self._parse_response(response)

    def search_public_tags(self, tags: List[str], **params) -> List[Nexset]:
        path = f"{self._path}/public/search_tags"
        response = self._make_request("POST", path, json=tags, params=params)
        return self._parse_response(response)

    def list_characteristics_search(self, **params) -> Dict[str, Any]:
        return self._make_request(
            "GET", f"{self._path}/characteristics/search", params=params
        )

    def list_summary(self, **params) -> Dict[str, Any]:
        return self._make_request("GET", f"{self._path}/summary", params=params)

    def list_nexset_api_compatible(self, **params) -> List[Nexset]:
        response = self._make_request(
            "GET", f"{self._path}/nexset_api_compatible", params=params
        )
        return self._parse_response(response)

    def update_runtime_status(self, set_id: int, status: str) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/runtime_status/{status}"
        return self._make_request("PUT", path)

    def get(self, set_id: int, expand: bool = False) -> Nexset:
        """
        Get single nexset by ID.

        Args:
            set_id: Nexset ID
            expand: Include expanded references

        Returns:
            Nexset instance

        Examples:
            client.nexsets.get(789)
        """
        return super().get(set_id, expand)

    def create(self, data: NexsetCreate) -> Nexset:
        """
        Create new nexset.

        Args:
            data: Nexset creation data

        Returns:
            Created nexset

        Examples:
            new_set = client.nexsets.create(NexsetCreate(name="My Dataset", ...))
        """
        return super().create(data)

    def update(self, set_id: int, data: NexsetUpdate) -> Nexset:
        """
        Update nexset.

        Args:
            set_id: Nexset ID
            data: Updated nexset data

        Returns:
            Updated nexset
        """
        return super().update(set_id, data)

    def delete(self, set_id: int) -> Dict[str, Any]:
        """
        Delete nexset.

        Args:
            set_id: Nexset ID

        Returns:
            Response with status
        """
        return super().delete(set_id)

    def activate(self, set_id: int) -> Nexset:
        """
        Activate nexset.

        Args:
            set_id: Nexset ID

        Returns:
            Activated nexset
        """
        return super().activate(set_id)

    def pause(self, set_id: int) -> Nexset:
        """
        Pause nexset.

        Args:
            set_id: Nexset ID

        Returns:
            Paused nexset
        """
        return super().pause(set_id)

    def get_samples(
        self,
        set_id: int,
        count: int = 10,
        include_metadata: bool = False,
        live: bool = False,
    ) -> List[NexsetSample]:
        """
        Get sample records from a nexset.

        Args:
            set_id: Nexset ID
            count: Maximum number of samples
            include_metadata: Include Nexla metadata
            live: Fetch live samples from topic

        Returns:
            List of sample records
        """
        path = f"{self._path}/{set_id}/samples"
        params = {"count": count, "include_metadata": include_metadata, "live": live}

        response = self._make_request("GET", path, params=params)

        # Handle both response formats
        if isinstance(response, list):
            return [NexsetSample(**item) for item in response]
        return response

    def update_samples(
        self, set_id: int, samples: Any, replace: bool = False
    ) -> List[NexsetSample]:
        path = f"{self._path}/{set_id}/samples"
        params = {"replace": replace}
        response = self._make_request("PUT", path, json=samples, params=params)
        if isinstance(response, list):
            return [NexsetSample(**item) for item in response]
        return response

    def add_samples(self, set_id: int, samples: Any) -> List[NexsetSample]:
        path = f"{self._path}/{set_id}/samples"
        response = self._make_request("POST", path, json=samples)
        if isinstance(response, list):
            return [NexsetSample(**item) for item in response]
        return response

    def copy(self, set_id: int, options: Optional[NexsetCopyOptions] = None) -> Nexset:
        """
        Copy a nexset.

        Args:
            set_id: Nexset ID
            options: Copy options

        Returns:
            Copied nexset
        """
        data = options.to_dict() if options else {}
        return super().copy(set_id, data)

    def sync_with_catalog(self, set_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/sync_with_catalog"
        return self._make_request("POST", path)

    def get_flow(self, set_id: int) -> Dict[str, Any]:
        return self._make_request("GET", f"{self._path}/{set_id}/flow")

    def get_flow_dashboard(self, set_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/flow/dashboard"
        return self._make_request("GET", path, params=params)

    def get_flow_status_metrics(self, set_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/flow/status_metrics"
        return self._make_request("GET", path, params=params)

    def get_flow_metrics(self, set_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/flow/metrics"
        return self._make_request("GET", path, params=params)

    def get_flow_logs(self, set_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/flow/logs"
        return self._make_request("GET", path, params=params)

    def get_metrics(
        self, set_id: int, metrics_name: Optional[str] = None, **params
    ) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/metrics"
        if metrics_name:
            path = f"{path}/{metrics_name}"
        return self._make_request("GET", path, params=params)

    def catalog_add(self, set_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/catalog"
        return self._make_request("POST", path, json=payload)

    def semantic_schemas(self, set_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/semantic_schemas"
        return self._make_request("GET", path, params=params)

    def transform(self, set_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/transform"
        return self._make_request("POST", path, json=payload)

    def get_quarantine_settings(self, set_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/quarantine_settings"
        return self._make_request("GET", path)

    def create_quarantine_settings(self, set_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/quarantine_settings"
        return self._make_request("POST", path, json=payload)

    def update_quarantine_settings(self, set_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/quarantine_settings"
        return self._make_request("PUT", path, json=payload)

    def delete_quarantine_settings(self, set_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/quarantine_settings"
        return self._make_request("DELETE", path)

    def get_dashboard_transforms(self, set_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/dashboard_transforms"
        return self._make_request("GET", path)

    def create_dashboard_transforms(self, set_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/dashboard_transforms"
        return self._make_request("POST", path, json=payload)

    def update_dashboard_transforms(self, set_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/dashboard_transforms"
        return self._make_request("PUT", path, json=payload)

    def delete_dashboard_transforms(self, set_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/dashboard_transforms"
        return self._make_request("DELETE", path)

    def list_sharers(self, set_id: int) -> List[Dict[str, Any]]:
        path = f"{self._path}/{set_id}/sharers"
        return self._make_request("GET", path) or []

    def set_sharers(self, set_id: int, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        path = f"{self._path}/{set_id}/sharers"
        return self._make_request("POST", path, json=payload) or []

    def add_sharers(self, set_id: int, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        path = f"{self._path}/{set_id}/sharers"
        return self._make_request("PUT", path, json=payload) or []

    def remove_sharers(self, set_id: int, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        path = f"{self._path}/{set_id}/sharers"
        return self._make_request("DELETE", path, json=payload) or []

    def mark_shared(self, set_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/sharers/shared"
        return self._make_request("PUT", path)

    def probe_quarantine_sample(self, set_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/probe/quarantine/sample"
        return self._make_request("POST", path, json=payload)

    def get_quarantine_offset(self, set_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/quarantine/offset"
        return self._make_request("GET", path)

    def get_offset(self, set_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/offset"
        return self._make_request("GET", path)

    def get_data_update_time(self, set_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/data_update_time"
        return self._make_request("GET", path)

    def get_characteristics(self, set_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/characteristics"
        return self._make_request("GET", path)

    def summary(self, set_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/summary"
        return self._make_request("GET", path)

    def search(self, filters: Dict[str, Any], **params) -> List[Nexset]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params) -> List[Nexset]:
        return super().search_tags(tags, **params)

    def vote(self, set_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/vote"
        return self._make_request("POST", path, json=payload)

    def unvote(self, set_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/unvote"
        return self._make_request("DELETE", path)

    def list_catalog_refs(self, **params) -> List[CatalogRef]:
        path = f"{self._path}/catalog_refs"
        response = self._make_request("GET", path, params=params)
        return [CatalogRef.model_validate(item) for item in (response or [])]

    def get_catalog_ref(self, ref_id: int) -> CatalogRef:
        path = f"{self._path}/catalog_refs/{ref_id}"
        response = self._make_request("GET", path)
        return CatalogRef.model_validate(response)

    def create_catalog_ref(self, payload: Dict[str, Any]) -> CatalogRef:
        path = f"{self._path}/catalog_refs"
        response = self._make_request("POST", path, json=payload)
        return CatalogRef.model_validate(response)

    def update_catalog_ref(self, ref_id: int, payload: Dict[str, Any]) -> CatalogRef:
        path = f"{self._path}/catalog_refs/{ref_id}"
        response = self._make_request("PUT", path, json=payload)
        return CatalogRef.model_validate(response)

    def delete_catalog_ref(self, ref_id: int) -> Dict[str, Any]:
        path = f"{self._path}/catalog_refs/{ref_id}"
        return self._make_request("DELETE", path)

    def bulk_update_catalog_refs(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PUT", "/catalog_refs/bulk_update_refs", json=payload)

    def list_api_keys(self, set_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/api_keys"
        return self._make_request("GET", path, params=params)

    def search_api_keys(self, set_id: int, filters: Dict[str, Any], **params) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/api_keys/search"
        return self._make_request("POST", path, json=filters, params=params)

    def get_api_key(self, set_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/api_keys/{api_key_id}"
        return self._make_request("GET", path)

    def create_api_key(self, set_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/api_keys"
        return self._make_request("POST", path, json=payload)

    def update_api_key(self, set_id: int, api_key_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/api_keys/{api_key_id}"
        return self._make_request("PUT", path, json=payload)

    def rotate_api_key(self, set_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/api_keys/{api_key_id}/rotate"
        return self._make_request("PUT", path)

    def activate_api_key(self, set_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/api_keys/{api_key_id}/activate"
        return self._make_request("PUT", path)

    def pause_api_key(self, set_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/api_keys/{api_key_id}/pause"
        return self._make_request("PUT", path)

    def pause_all_api_keys(self, set_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/api_keys/pause"
        return self._make_request("PUT", path)

    def delete_api_key(self, set_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/api_keys/{api_key_id}"
        return self._make_request("DELETE", path)

    def trigger_quarantine_aggregation(
        self, set_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/trigger_quarantine_aggregation"
        return self._make_request("POST", path, json=payload)

    def get_quarantine_aggregation(self, set_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{set_id}/quarantine_aggregation"
        return self._make_request("GET", path)

    def docs_recommendation(self, set_id: int) -> Dict[str, Any]:
        """Generate AI suggestion for Nexset documentation."""
        path = f"{self._path}/{set_id}/docs/recommendation"
        return self._make_request("POST", path)

    def list_docs(self, set_id: int, expand: bool = True) -> List[DocContainer]:
        """List documentation entries attached to a nexset.

        Each entry is a ``DocContainer`` carrying the rich documentation body
        in its ``text`` field (typically markdown), along with metadata such
        as owner, org, doc type, and timestamps.

        Args:
            set_id: Nexset ID.
            expand: When ``True`` (default), pass ``expand=1`` to the API to
                include nested ``owner`` and ``org`` details in each entry.

        Returns:
            List of ``DocContainer`` instances.  Empty list if the nexset has
            no documentation.

        Examples:
            Read the markdown body of the first doc on a nexset::

                docs = client.nexsets.list_docs(419706)
                if docs:
                    print(docs[0].text)
        """
        path = f"{self._path}/{set_id}/docs"
        params = {"expand": 1} if expand else {}
        response = self._make_request("GET", path, params=params)
        if isinstance(response, list):
            return [DocContainer.model_validate(item) for item in response]
        return []

    def update_docs(
        self,
        set_id: int,
        docs: List[Union[DocContainerInput, Dict[str, Any]]],
    ) -> List[DocContainer]:
        """Replace all documentation entries on a nexset.

        This call uses **replace-all** semantics: the provided list becomes
        the entire set of docs for the nexset.  Any existing entries that are
        not in the list are removed.

        Args:
            set_id: Nexset ID.
            docs: New documentation entries.  Each item may be a
                ``DocContainerInput`` instance or a plain dict with the same
                shape (``name``, ``text``, ``doc_type``, optional
                ``description``).  Plain dicts are accepted to support
                generic pass-through callers (e.g. the MCP server, raw
                scripts).

            Returns:
                The new list of ``DocContainer`` entries as parsed from the
                server response.

        Examples:
            Replace a nexset's docs with a single markdown entry::

                from nexla_sdk.models import DocContainerInput

                client.nexsets.update_docs(
                    419706,
                    [DocContainerInput(
                        name="Overview",
                        description="High-level description",
                        text="# Overview\\n\\n...",
                    )],
                )
        """
        path = f"{self._path}/{set_id}/docs"
        serialized = [self._serialize_data(d) for d in docs]
        response = self._make_request(
            "POST", path, json={"docs": serialized}
        )
        if isinstance(response, list):
            return [DocContainer.model_validate(item) for item in response]
        return []

    def copy_docs(self, src_id: int, dst_id: int) -> List[DocContainer]:
        """Copy all documentation entries from one nexset to another.

        Reads the source's docs, strips server-owned fields (id, owner, org,
        access_roles, copied_from_id, created_at, updated_at), and writes
        them to the destination using ``update_docs`` (replace-all
        semantics).  Existing docs on the destination are overwritten.

        If the source has no docs, this is a no-op: the destination is left
        unchanged and an empty list is returned.

        Note: only fields present on ``DocContainerInput`` are carried over.
        Any new server-side doc fields will be ignored until
        ``DocContainerInput`` is extended.

        Args:
            src_id: Source nexset ID (docs are read from here).
            dst_id: Destination nexset ID (docs are written here).

        Returns:
            The destination's new list of ``DocContainer`` entries, or an
            empty list if the source had no docs.

        Examples:
            Copy docs from one nexset to another::

                client.nexsets.copy_docs(src_id=419706, dst_id=419800)
        """
        source_docs = self.list_docs(src_id)
        if not source_docs:
            return []
        payload = [
            DocContainerInput.model_validate(
                doc.model_dump(exclude_none=True)
            )
            for doc in source_docs
        ]
        return self.update_docs(dst_id, payload)
