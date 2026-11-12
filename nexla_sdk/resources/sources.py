from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from nexla_sdk.models.sources.requests import (
    SourceCopyOptions,
    SourceCreate,
    SourceUpdate,
)
from nexla_sdk.models.sources.responses import Source
from nexla_sdk.resources.base_resource import BaseResource
from nexla_sdk.utils.deprecation import missing_route

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class SourcesResource(BaseResource):
    """Resource for managing data sources."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/data_sources"
        self._model_class = Source

    def list(self, **kwargs) -> List[Source]:
        """
        List sources with optional filters.

        Args:
            page: Page number (via kwargs)
            per_page: Items per page (via kwargs)
            access_role: Filter by access role (via kwargs)
            **kwargs: Additional query parameters

        Returns:
            List of sources

        Examples:
            # All sources
            client.sources.list()

            # With pagination and role
            client.sources.list(page=1, per_page=20, access_role="owner")
        """
        return super().list(**kwargs)

    def search(self, filters: Dict[str, Any], **params) -> List[Source]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params) -> List[Source]:
        return super().search_tags(tags, **params)

    def list_all(self, **params) -> List[Source]:
        response = self._make_request("GET", f"{self._path}/all", params=params)
        return self._parse_response(response)

    def list_all_condensed(self, **params) -> List[Dict[str, Any]]:
        return self._make_request("GET", f"{self._path}/all/condensed", params=params)

    def list_all_ids(self, **params) -> List[int]:
        return self._make_request("GET", f"{self._path}/all/ids", params=params)

    def list_accessible(self, **params) -> List[Source]:
        return super().list_accessible(**params)

    def script_source_config(self) -> Dict[str, Any]:
        return self._make_request("GET", f"{self._path}/script_source_config")

    def update_runtime_status(self, source_id: int, status: str) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/runtime_status/{status}"
        return self._make_request("PUT", path)

    def get(self, source_id: int, expand: bool = False) -> Source:
        """
        Get single source by ID.

        Args:
            source_id: Source ID
            expand: Include expanded references

        Returns:
            Source instance

        Examples:
            client.sources.get(123)
        """
        return super().get(source_id, expand)

    def create(self, data: SourceCreate) -> Source:
        """
        Create new source.

        Args:
            data: Source creation data

        Returns:
            Created source

        Examples:
            new_source = client.sources.create(SourceCreate(name="My Source", connector=...))
        """
        return super().create(data)

    def update(self, source_id: int, data: SourceUpdate) -> Source:
        """
        Update source.

        Args:
            source_id: Source ID
            data: Updated source data

        Returns:
            Updated source
        """
        return super().update(source_id, data)

    def delete(self, source_id: int) -> Dict[str, Any]:
        """
        Delete source.

        Args:
            source_id: Source ID

        Returns:
            Response with status
        """
        return super().delete(source_id)

    def get_flow(self, source_id: int) -> Dict[str, Any]:
        return self._make_request("GET", f"{self._path}/{source_id}/flow")

    def get_flow_dashboard(self, source_id: int, **params) -> Dict[str, Any]:
        return self._make_request(
            "GET", f"{self._path}/{source_id}/flow/dashboard", params=params
        )

    def get_flow_status_metrics(self, source_id: int, **params) -> Dict[str, Any]:
        return self._make_request(
            "GET", f"{self._path}/{source_id}/flow/status_metrics", params=params
        )

    def get_flow_metrics(self, source_id: int, **params) -> Dict[str, Any]:
        return self._make_request(
            "GET", f"{self._path}/{source_id}/flow/metrics", params=params
        )

    def get_flow_logs(self, source_id: int, **params) -> Dict[str, Any]:
        return self._make_request(
            "GET", f"{self._path}/{source_id}/flow/logs", params=params
        )

    def get_metrics(
        self, source_id: int, metrics_name: Optional[str] = None, **params
    ) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/metrics"
        if metrics_name:
            path = f"{path}/{metrics_name}"
        return self._make_request("GET", path, params=params)

    def get_quarantine_offset(
        self, source_id: int, data_set_id: Optional[int] = None
    ) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/quarantine/offset"
        if data_set_id:
            path = f"{path}/{data_set_id}"
        return self._make_request("GET", path)

    def get_offset(
        self, source_id: int, data_set_id: Optional[int] = None
    ) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/offset"
        if data_set_id:
            path = f"{path}/{data_set_id}"
        return self._make_request("GET", path)

    def activate(self, source_id: int) -> Source:
        """
        Activate source.

        Args:
            source_id: Source ID

        Returns:
            Activated source
        """
        return super().activate(source_id)

    def pause(self, source_id: int) -> Source:
        """
        Pause source.

        Args:
            source_id: Source ID

        Returns:
            Paused source
        """
        return super().pause(source_id)

    def copy(
        self, source_id: int, options: Optional[SourceCopyOptions] = None
    ) -> Source:
        """
        Copy a source.

        Args:
            source_id: Source ID
            options: Copy options

        Returns:
            Copied source
        """
        data = options.to_dict() if options else {}
        return super().copy(source_id, data)

    def probe_list_buckets(self, source_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/probe"
        return self._make_request("GET", path)

    def probe_summary(self, source_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/probe/summary"
        return self._make_request("GET", path)

    def probe_authenticate(self, source_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/probe/authenticate"
        return self._make_request("GET", path)

    def probe_list_files(
        self, source_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/probe/buckets"
        return self._make_request("POST", path, json=payload)

    def probe_tree(self, source_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/probe/tree"
        return self._make_request("POST", path, json=payload)

    def probe_read_file(
        self, source_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/probe/files"
        return self._make_request("POST", path, json=payload)

    def probe_detect_schemas(
        self, source_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/probe/schemas"
        return self._make_request("POST", path, json=payload)

    def probe_quarantine_sample(
        self, source_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/probe/quarantine/sample"
        return self._make_request("POST", path, json=payload)

    def probe_sample(self, source_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/probe/sample"
        return self._make_request("POST", path, json=payload)

    def get_reingested_files(self, source_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/file/ingest"
        return self._make_request("GET", path, params=params)

    def reingest_files(self, source_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/file/ingest"
        return self._make_request("POST", path, json=payload)

    def get_quarantine_settings(self, source_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/quarantine_settings"
        return self._make_request("GET", path)

    def create_quarantine_settings(
        self, source_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/quarantine_settings"
        return self._make_request("POST", path, json=payload)

    def update_quarantine_settings(
        self, source_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/quarantine_settings"
        return self._make_request("PUT", path, json=payload)

    def delete_quarantine_settings(self, source_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/quarantine_settings"
        return self._make_request("DELETE", path)

    def get_dashboard_transforms(self, source_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/dashboard_transforms"
        return self._make_request("GET", path)

    def create_dashboard_transforms(
        self, source_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/dashboard_transforms"
        return self._make_request("POST", path, json=payload)

    def update_dashboard_transforms(
        self, source_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/dashboard_transforms"
        return self._make_request("PUT", path, json=payload)

    def delete_dashboard_transforms(self, source_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/dashboard_transforms"
        return self._make_request("DELETE", path)

    @missing_route("POST", "/data_sources/config/validate")
    def validate_config(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", f"{self._path}/config/validate", json=payload)

    def test_config(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", f"{self._path}/test_config", json=payload)

    def list_data_sinks(self, source_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/data_sinks"
        return self._make_request("GET", path, params=params)

    def run_now(self, source_id: int, method: str = "POST") -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/run_now"
        return self._make_request(method.upper(), path)

    def ready(self, source_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/ready"
        return self._make_request("POST", path)

    def list_runs(self, source_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/runs"
        return self._make_request("GET", path, params=params)

    def list_flow_triggers(self, source_id: int) -> List[Dict[str, Any]]:
        path = f"{self._path}/{source_id}/flow_triggers"
        return self._make_request("GET", path) or []

    def edit_flow_triggers(
        self,
        source_id: int,
        payload: Dict[str, Any],
        mode: str,
        all_triggers: bool = False,
    ) -> List[Dict[str, Any]]:
        path = f"{self._path}/{source_id}/flow_triggers"
        if mode in {"pause", "activate"}:
            path = f"{path}/{mode}"
        if all_triggers:
            path = f"{path}/all"
        method = "PUT" if mode in {"add", "pause", "activate"} else "POST"
        if mode == "remove":
            method = "DELETE"
        return self._make_request(method, path, json=payload) or []

    def list_api_keys(self, source_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/api_keys"
        return self._make_request("GET", path, params=params)

    def search_api_keys(
        self, source_id: int, filters: Dict[str, Any], **params
    ) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/api_keys/search"
        return self._make_request("POST", path, json=filters, params=params)

    def get_api_key(self, source_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/api_keys/{api_key_id}"
        return self._make_request("GET", path)

    def create_api_key(self, source_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/api_keys"
        return self._make_request("POST", path, json=payload)

    def update_api_key(
        self, source_id: int, api_key_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/api_keys/{api_key_id}"
        return self._make_request("PUT", path, json=payload)

    def rotate_api_key(self, source_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/api_keys/{api_key_id}/rotate"
        return self._make_request("PUT", path)

    def activate_api_key(self, source_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/api_keys/{api_key_id}/activate"
        return self._make_request("PUT", path)

    def pause_api_key(self, source_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/api_keys/{api_key_id}/pause"
        return self._make_request("PUT", path)

    def pause_all_api_keys(self, source_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/api_keys/pause"
        return self._make_request("PUT", path)

    def delete_api_key(self, source_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/api_keys/{api_key_id}"
        return self._make_request("DELETE", path)

    def trigger_quarantine_aggregation(
        self, source_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/trigger_quarantine_aggregation"
        return self._make_request("POST", path, json=payload)

    def get_quarantine_aggregation(self, source_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{source_id}/quarantine_aggregation"
        return self._make_request("GET", path)

    def data_sources_update_data_source(
        self,
        data_source_id: int,
        data: Dict[str, Any],
        force: Optional[bool] = None,
        run_now: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Partially update a data source (PATCH).

        Args:
            data_source_id: Data source ID
            data: Fields to update
            force: Force the update
            run_now: Run the data source after the update

        Returns:
            Updated data source
        """
        params = {"force": force, "run_now": run_now}
        path = f"{self._path}/{data_source_id}"
        return self._make_request(
            "PATCH",
            path,
            params={k: v for k, v in params.items() if v is not None},
            json=data,
        )

    def validate_data_source_config(
        self, data_source_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate the configuration of a data source.

        Args:
            data_source_id: Data source ID
            data: Configuration to validate

        Returns:
            Validation result
        """
        path = f"{self._path}/{data_source_id}/config/validate"
        return self._make_request("POST", path, json=data)

    def get_external_file_status_alias(
        self,
        data_source_id: int,
        source: Optional[str] = None,
        status: Optional[str] = None,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sortBy: Optional[str] = None,
        sortOrder: Optional[str] = None,
        fileId: Optional[str] = None,
        filePath: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get external file ingestion status (alias of get_external_file_status).

        Args:
            data_source_id: Data source ID
            source: Source filter (EXTERNAL, CLOUD, REINGEST, all)
            status: Status filter (NEW, STARTED, DONE, and others)
            page: Page number
            size: Page size
            sortBy: Sort field
            sortOrder: Sort order
            fileId: File ID filter
            filePath: File path filter

        Returns:
            External file status payload
        """
        params = {
            "source": source,
            "status": status,
            "page": page,
            "size": size,
            "sortBy": sortBy,
            "sortOrder": sortOrder,
            "fileId": fileId,
            "filePath": filePath,
        }
        path = f"{self._path}/{data_source_id}/file/external/status"
        return self._make_request(
            "GET", path, params={k: v for k, v in params.items() if v is not None}
        )

    def get_external_file_status(
        self,
        data_source_id: int,
        source: Optional[str] = None,
        status: Optional[str] = None,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sortBy: Optional[str] = None,
        sortOrder: Optional[str] = None,
        fileId: Optional[str] = None,
        filePath: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get external file ingestion status.

        Args:
            data_source_id: Data source ID
            source: Source filter (EXTERNAL, CLOUD, REINGEST, all)
            status: Status filter (NEW, STARTED, DONE, and others)
            page: Page number
            size: Page size
            sortBy: Sort field
            sortOrder: Sort order
            fileId: File ID filter
            filePath: File path filter

        Returns:
            External file status payload
        """
        params = {
            "source": source,
            "status": status,
            "page": page,
            "size": size,
            "sortBy": sortBy,
            "sortOrder": sortOrder,
            "fileId": fileId,
            "filePath": filePath,
        }
        path = f"{self._path}/{data_source_id}/file/status"
        return self._make_request(
            "GET", path, params={k: v for k, v in params.items() if v is not None}
        )

    def dequeue_external_file(
        self,
        data_source_id: int,
        file_id: str,
        filePath: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Remove an external file from the ingestion queue.

        Args:
            data_source_id: Data source ID
            file_id: File ID
            filePath: File path (camelCase query name)
            file_path: File path (snake_case query name)

        Returns:
            Dequeue result
        """
        params = {"filePath": filePath, "file_path": file_path}
        path = f"{self._path}/{data_source_id}/file/external/{file_id}"
        return self._make_request(
            "DELETE", path, params={k: v for k, v in params.items() if v is not None}
        )

    def data_sources_flow_audit_log(
        self,
        resource_id: int,
        interval: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        event_filter: Optional[str] = None,
        change_filter: Optional[str] = None,
        page: Optional[str] = None,
        per_page: Optional[str] = None,
        expand: Optional[str] = None,
        access_role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get the audit log for the flow of a data source.

        Args:
            resource_id: Data source ID
            interval: Time interval filter
            from_date: Start date (wire name from)
            to_date: End date (wire name to)
            event_filter: Event type filter
            change_filter: Change type filter
            page: Page number
            per_page: Items per page
            expand: Expand references
            access_role: Access role filter

        Returns:
            Flow audit log entries
        """
        params = {
            "interval": interval,
            "from": from_date,
            "to": to_date,
            "event_filter": event_filter,
            "change_filter": change_filter,
            "page": page,
            "per_page": per_page,
            "expand": expand,
            "access_role": access_role,
        }
        path = f"{self._path}/{resource_id}/flow/audit_log"
        return self._make_request(
            "GET", path, params={k: v for k, v in params.items() if v is not None}
        )

    def activate_flow_via_data_source(
        self,
        resource_id: int,
        all: Optional[bool] = None,
        full_tree: Optional[bool] = None,
        run_now: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Activate the flow of a data source.

        Args:
            resource_id: Data source ID
            all: Activate the entire flow tree
            full_tree: Include the full tree in the response
            run_now: Run value passed to the backend

        Returns:
            Flow response
        """
        params = {"all": all, "full_tree": full_tree, "run_now": run_now}
        path = f"{self._path}/{resource_id}/flow/activate"
        return self._make_request(
            "PUT", path, params={k: v for k, v in params.items() if v is not None}
        )

    def pause_flow_via_data_source(
        self,
        resource_id: int,
        all: Optional[bool] = None,
        full_tree: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Pause the flow of a data source.

        Args:
            resource_id: Data source ID
            all: Pause the entire flow tree
            full_tree: Include the full tree in the response

        Returns:
            Flow response
        """
        params = {"all": all, "full_tree": full_tree}
        path = f"{self._path}/{resource_id}/flow/pause"
        return self._make_request(
            "PUT", path, params={k: v for k, v in params.items() if v is not None}
        )

    def auto_create_nexset(
        self,
        data_source_id: int,
        include_samples: Optional[bool] = None,
        include_nexset_api_config: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Probe a data source and create its first nexset.

        Args:
            data_source_id: Data source ID
            include_samples: Include data samples in the response
            include_nexset_api_config: Include the nexset API config

        Returns:
            Created nexset payload
        """
        params = {
            "include_samples": include_samples,
            "include_nexset_api_config": include_nexset_api_config,
        }
        path = f"{self._path}/{data_source_id}/nexset"
        return self._make_request(
            "POST", path, params={k: v for k, v in params.items() if v is not None}
        )

    def data_sources_get_data_source_offset(
        self, data_source_id: int, data_set_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get the offset of a data source, optionally for one nexset.

        Args:
            data_source_id: Data source ID
            data_set_id: Nexset ID filter

        Returns:
            Offset payload
        """
        params = {}
        if data_set_id is not None:
            params["data_set_id"] = data_set_id
        path = f"{self._path}/{data_source_id}/offset"
        return self._make_request("GET", path, params=params)

    def data_sources_get_data_source_quarantine_offset(
        self, data_source_id: int, data_set_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get the quarantine offset of a data source, optionally for one nexset.

        Args:
            data_source_id: Data source ID
            data_set_id: Nexset ID filter

        Returns:
            Quarantine offset payload
        """
        params = {}
        if data_set_id is not None:
            params["data_set_id"] = data_set_id
        path = f"{self._path}/{data_source_id}/quarantine/offset"
        return self._make_request("GET", path, params=params)

    def data_sources_probe_list_files_data_source(
        self, data_source_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List files in a bucket or path (PUT).

        Args:
            data_source_id: Data source ID
            data: Probe input

        Returns:
            Probe result
        """
        path = f"{self._path}/{data_source_id}/probe/buckets"
        return self._make_request("PUT", path, json=data)

    def data_sources_probe_read_file_data_source(
        self, data_source_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Read a file from the data source (PUT).

        Args:
            data_source_id: Data source ID
            data: Probe input

        Returns:
            Probe result
        """
        path = f"{self._path}/{data_source_id}/probe/files"
        return self._make_request("PUT", path, json=data)

    def data_sources_probe_read_quarantine_data_source(
        self, data_source_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Read a quarantine sample from the data source (PUT).

        Args:
            data_source_id: Data source ID
            data: Probe input

        Returns:
            Probe result
        """
        path = f"{self._path}/{data_source_id}/probe/quarantine/sample"
        return self._make_request("PUT", path, json=data)

    def data_sources_probe_read_sample_data_source(
        self,
        data_source_id: int,
        data: Optional[Dict[str, Any]] = None,
        return_original_response_status: Optional[bool] = None,
        page: Optional[Union[str, int]] = None,
        per_page: Optional[Union[str, int]] = None,
    ) -> Dict[str, Any]:
        """
        Read a data sample from the data source (PUT).

        Args:
            data_source_id: Data source ID
            data: Probe input
            return_original_response_status: Return the original response status
            page: Page number
            per_page: Items per page

        Returns:
            Probe result
        """
        params = {
            "return_original_response_status": return_original_response_status,
            "page": page,
            "per_page": per_page,
        }
        path = f"{self._path}/{data_source_id}/probe/sample"
        return self._make_request(
            "PUT",
            path,
            params={k: v for k, v in params.items() if v is not None},
            json=data,
        )

    def data_sources_probe_detect_schemas_data_source(
        self, data_source_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect schemas of the data source (PUT).

        Args:
            data_source_id: Data source ID
            data: Probe input

        Returns:
            Probe result
        """
        path = f"{self._path}/{data_source_id}/probe/schemas"
        return self._make_request("PUT", path, json=data)

    def data_sources_probe_list_tree_data_source(
        self, data_source_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List the tree of the data source (PUT).

        Args:
            data_source_id: Data source ID
            data: Probe input

        Returns:
            Probe result
        """
        path = f"{self._path}/{data_source_id}/probe/tree"
        return self._make_request("PUT", path, json=data)

    def register_external_files(
        self, data_source_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register external files for a data source and activate it on success.

        The backend forwards the body to the dataplane unchanged.

        Args:
            data_source_id: Data source ID
            payload: External file listing to register

        Returns:
            Dataplane result with status and output
        """
        path = f"{self._path}/{data_source_id}/file/external"
        return self._make_request("POST", path, json=payload)
