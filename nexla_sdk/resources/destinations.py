from typing import Any, Dict, List, Optional

from nexla_sdk.models.destinations.requests import (
    DestinationCopyOptions,
    DestinationCreate,
    DestinationUpdate,
)
from nexla_sdk.models.destinations.responses import Destination
from nexla_sdk.resources.base_resource import BaseResource


class DestinationsResource(BaseResource):
    """Resource for managing destinations (data sinks)."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/data_sinks"
        self._model_class = Destination

    def list(self, **kwargs) -> List[Destination]:
        """
        List destinations with optional filters.

        Args:
            page: Page number (via kwargs)
            per_page: Items per page (via kwargs)
            access_role: Filter by access role (via kwargs)
            **kwargs: Additional query parameters

        Returns:
            List of destinations

        Examples:
            client.destinations.list(page=1, per_page=20, access_role="owner")
        """
        return super().list(**kwargs)

    def search(self, filters: Dict[str, Any], **params) -> List[Destination]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params) -> List[Destination]:
        return super().search_tags(tags, **params)

    def list_all(self, **params) -> List[Destination]:
        response = self._make_request("GET", f"{self._path}/all", params=params)
        return self._parse_response(response)

    def list_all_condensed(self, **params) -> List[Dict[str, Any]]:
        return self._make_request("GET", f"{self._path}/all/condensed", params=params)

    def list_all_ids(self, **params) -> List[int]:
        return self._make_request("GET", f"{self._path}/all/ids", params=params)

    def list_all_by_data_set(self, **params) -> List[Destination]:
        response = self._make_request(
            "GET", f"{self._path}/all/data_set", params=params
        )
        return self._parse_response(response)

    def list_accessible(self, **params) -> List[Destination]:
        return super().list_accessible(**params)

    def script_sink_config(self) -> Dict[str, Any]:
        return self._make_request("GET", f"{self._path}/script_sink_config")

    def update_runtime_status(self, sink_id: int, status: str) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/runtime_status/{status}"
        return self._make_request("PUT", path)

    def get(self, sink_id: int, expand: bool = False) -> Destination:
        """
        Get single destination by ID.

        Args:
            sink_id: Destination ID
            expand: Include expanded references

        Returns:
            Destination instance

        Examples:
            client.destinations.get(321)
        """
        return super().get(sink_id, expand)

    def create(self, data: DestinationCreate) -> Destination:
        """
        Create new destination.

        Args:
            data: Destination creation data

        Returns:
            Created destination

        Examples:
            new_sink = client.destinations.create(DestinationCreate(name="My Sink", connector=...))
        """
        return super().create(data)

    def update(self, sink_id: int, data: DestinationUpdate) -> Destination:
        """
        Update destination.

        Args:
            sink_id: Destination ID
            data: Updated destination data

        Returns:
            Updated destination
        """
        return super().update(sink_id, data)

    def delete(self, sink_id: int) -> Dict[str, Any]:
        """
        Delete destination.

        Args:
            sink_id: Destination ID

        Returns:
            Response with status
        """
        return super().delete(sink_id)

    def get_flow(self, sink_id: int) -> Dict[str, Any]:
        return self._make_request("GET", f"{self._path}/{sink_id}/flow")

    def get_flow_dashboard(self, sink_id: int, **params) -> Dict[str, Any]:
        return self._make_request(
            "GET", f"{self._path}/{sink_id}/flow/dashboard", params=params
        )

    def get_flow_status_metrics(self, sink_id: int, **params) -> Dict[str, Any]:
        return self._make_request(
            "GET", f"{self._path}/{sink_id}/flow/status_metrics", params=params
        )

    def get_flow_metrics(self, sink_id: int, **params) -> Dict[str, Any]:
        return self._make_request(
            "GET", f"{self._path}/{sink_id}/flow/metrics", params=params
        )

    def get_flow_logs(self, sink_id: int, **params) -> Dict[str, Any]:
        return self._make_request(
            "GET", f"{self._path}/{sink_id}/flow/logs", params=params
        )

    def get_metrics(
        self, sink_id: int, metrics_name: Optional[str] = None, **params
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/metrics"
        if metrics_name:
            path = f"{path}/{metrics_name}"
        return self._make_request("GET", path, params=params)

    def get_quarantine_offset(
        self, sink_id: int, data_set_id: Optional[int] = None
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/quarantine/offset"
        if data_set_id:
            path = f"{path}/{data_set_id}"
        return self._make_request("GET", path)

    def get_offset(
        self, sink_id: int, data_set_id: Optional[int] = None
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/offset"
        if data_set_id:
            path = f"{path}/{data_set_id}"
        return self._make_request("GET", path)

    def activate(self, sink_id: int) -> Destination:
        """
        Activate destination.

        Args:
            sink_id: Destination ID

        Returns:
            Activated destination
        """
        return super().activate(sink_id)

    def pause(self, sink_id: int) -> Destination:
        """
        Pause destination.

        Args:
            sink_id: Destination ID

        Returns:
            Paused destination
        """
        return super().pause(sink_id)

    def copy(
        self, sink_id: int, options: Optional[DestinationCopyOptions] = None
    ) -> Destination:
        """
        Copy a destination.

        Args:
            sink_id: Destination ID
            options: Copy options

        Returns:
            Copied destination
        """
        data = options.to_dict() if options else {}
        return super().copy(sink_id, data)

    def probe_list_buckets(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe"
        return self._make_request("GET", path)

    def probe_summary(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe/summary"
        return self._make_request("GET", path)

    def probe_authenticate(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe/authenticate"
        return self._make_request("GET", path)

    def probe_list_files(self, sink_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe/buckets"
        return self._make_request("POST", path, json=payload)

    def probe_tree(self, sink_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe/tree"
        return self._make_request("POST", path, json=payload)

    def probe_read_file(self, sink_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe/files"
        return self._make_request("POST", path, json=payload)

    def probe_detect_schemas(
        self, sink_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe/schemas"
        return self._make_request("POST", path, json=payload)

    def probe_quarantine_sample(
        self, sink_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe/quarantine/sample"
        return self._make_request("POST", path, json=payload)

    def get_quarantine_settings(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/quarantine_settings"
        return self._make_request("GET", path)

    def create_quarantine_settings(
        self, sink_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/quarantine_settings"
        return self._make_request("POST", path, json=payload)

    def update_quarantine_settings(
        self, sink_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/quarantine_settings"
        return self._make_request("PUT", path, json=payload)

    def delete_quarantine_settings(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/quarantine_settings"
        return self._make_request("DELETE", path)

    def get_dashboard_transforms(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/dashboard_transforms"
        return self._make_request("GET", path)

    def create_dashboard_transforms(
        self, sink_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/dashboard_transforms"
        return self._make_request("POST", path, json=payload)

    def update_dashboard_transforms(
        self, sink_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/dashboard_transforms"
        return self._make_request("PUT", path, json=payload)

    def delete_dashboard_transforms(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/dashboard_transforms"
        return self._make_request("DELETE", path)

    def validate_config(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", f"{self._path}/config/validate", json=payload)

    def test_config(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", f"{self._path}/test_config", json=payload)

    def run_status(self, sink_id: int, run_id: Optional[int] = None) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/run_status"
        if run_id is not None:
            path = f"{path}/{run_id}"
        return self._make_request("GET", path)

    def run_analysis(self, sink_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/run_analysis"
        return self._make_request("GET", path, params=params)

    def list_flow_triggers(self, sink_id: int) -> List[Dict[str, Any]]:
        path = f"{self._path}/{sink_id}/flow_triggers"
        return self._make_request("GET", path) or []

    def edit_flow_triggers(
        self,
        sink_id: int,
        payload: Dict[str, Any],
        mode: str,
        all_triggers: bool = False,
    ) -> List[Dict[str, Any]]:
        path = f"{self._path}/{sink_id}/flow_triggers"
        if mode in {"pause", "activate"}:
            path = f"{path}/{mode}"
        if all_triggers:
            path = f"{path}/all"
        method = "PUT" if mode in {"add", "pause", "activate"} else "POST"
        if mode == "remove":
            method = "DELETE"
        return self._make_request(method, path, json=payload) or []

    def list_api_keys(self, sink_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys"
        return self._make_request("GET", path, params=params)

    def search_api_keys(
        self, sink_id: int, filters: Dict[str, Any], **params
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/search"
        return self._make_request("POST", path, json=filters, params=params)

    def get_api_key(self, sink_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/{api_key_id}"
        return self._make_request("GET", path)

    def create_api_key(self, sink_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys"
        return self._make_request("POST", path, json=payload)

    def update_api_key(
        self, sink_id: int, api_key_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/{api_key_id}"
        return self._make_request("PUT", path, json=payload)

    def rotate_api_key(self, sink_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/{api_key_id}/rotate"
        return self._make_request("PUT", path)

    def activate_api_key(self, sink_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/{api_key_id}/activate"
        return self._make_request("PUT", path)

    def pause_api_key(self, sink_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/{api_key_id}/pause"
        return self._make_request("PUT", path)

    def pause_all_api_keys(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/pause"
        return self._make_request("PUT", path)

    def delete_api_key(self, sink_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/{api_key_id}"
        return self._make_request("DELETE", path)

    def trigger_quarantine_aggregation(
        self, sink_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/trigger_quarantine_aggregation"
        return self._make_request("POST", path, json=payload)

    def get_quarantine_aggregation(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/quarantine_aggregation"
        return self._make_request("GET", path)
