from typing import Any, Dict, List, Optional

from nexla_sdk.models.sources.requests import (
    SourceCopyOptions,
    SourceCreate,
    SourceUpdate,
)
from nexla_sdk.models.sources.responses import Source
from nexla_sdk.resources.base_resource import BaseResource


class SourcesResource(BaseResource):
    """Resource for managing data sources."""

    def __init__(self, client):
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
