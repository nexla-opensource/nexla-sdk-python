from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

from nexla_sdk.models.destinations.requests import (
    DestinationCopyOptions,
    DestinationCreate,
    DestinationUpdate,
)
from nexla_sdk.models.destinations.responses import Destination
from nexla_sdk.resources.base_resource import BaseResource
from nexla_sdk.utils.deprecation import missing_route

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class DestinationsResource(BaseResource[Destination]):
    """Resource for managing destinations (data sinks)."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/data_sinks"
        self._model_class = Destination

    def list(self, **kwargs: Any) -> List[Destination]:  # type: ignore[override]  # keeps public list() signature; base list() also takes positional filters
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

    def search(self, filters: Dict[str, Any], **params: Any) -> List[Destination]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params: Any) -> List[Destination]:
        return super().search_tags(tags, **params)

    def list_all(self, **params: Any) -> List[Destination]:
        response = self._make_request("GET", f"{self._path}/all", params=params)
        return cast(List[Destination], self._parse_response(response))

    def list_all_condensed(self, **params: Any) -> List[Dict[str, Any]]:
        return cast(
            List[Dict[str, Any]],
            self._make_request("GET", f"{self._path}/all/condensed", params=params),
        )

    def list_all_ids(self, **params: Any) -> List[int]:
        return cast(
            List[int], self._make_request("GET", f"{self._path}/all/ids", params=params)
        )

    def list_all_by_data_set(self, **params: Any) -> List[Destination]:
        response = self._make_request(
            "GET", f"{self._path}/all/data_set", params=params
        )
        return cast(List[Destination], self._parse_response(response))

    def list_accessible(self, **params: Any) -> List[Destination]:
        return super().list_accessible(**params)

    def script_sink_config(self) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._make_request("GET", f"{self._path}/script_sink_config"),
        )

    def update_runtime_status(self, sink_id: int, status: str) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/runtime_status/{status}"
        return cast(Dict[str, Any], self._make_request("PUT", path))

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

    def create(self, data: Union[DestinationCreate, Dict[str, Any]]) -> Destination:
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

    def update(
        self, sink_id: int, data: Union[DestinationUpdate, Dict[str, Any]]
    ) -> Destination:
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
        return cast(
            Dict[str, Any], self._make_request("GET", f"{self._path}/{sink_id}/flow")
        )

    def get_flow_dashboard(self, sink_id: int, **params: Any) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._make_request(
                "GET", f"{self._path}/{sink_id}/flow/dashboard", params=params
            ),
        )

    def get_flow_status_metrics(self, sink_id: int, **params: Any) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._make_request(
                "GET", f"{self._path}/{sink_id}/flow/status_metrics", params=params
            ),
        )

    def get_flow_metrics(self, sink_id: int, **params: Any) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._make_request(
                "GET", f"{self._path}/{sink_id}/flow/metrics", params=params
            ),
        )

    def get_flow_logs(self, sink_id: int, **params: Any) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._make_request(
                "GET", f"{self._path}/{sink_id}/flow/logs", params=params
            ),
        )

    def get_metrics(
        self, sink_id: int, metrics_name: Optional[str] = None, **params: Any
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/metrics"
        if metrics_name:
            path = f"{path}/{metrics_name}"
        return cast(Dict[str, Any], self._make_request("GET", path, params=params))

    def get_quarantine_offset(
        self, sink_id: int, data_set_id: Optional[int] = None
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/quarantine/offset"
        if data_set_id:
            path = f"{path}/{data_set_id}"
        return cast(Dict[str, Any], self._make_request("GET", path))

    def get_offset(
        self, sink_id: int, data_set_id: Optional[int] = None
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/offset"
        if data_set_id:
            path = f"{path}/{data_set_id}"
        return cast(Dict[str, Any], self._make_request("GET", path))

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
        self,
        sink_id: int,
        options: Optional[DestinationCopyOptions] = None,  # type: ignore[override]  # dict options are not supported: body calls options.to_dict()
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
        return cast(Dict[str, Any], self._make_request("GET", path))

    def probe_summary(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe/summary"
        return cast(Dict[str, Any], self._make_request("GET", path))

    def probe_authenticate(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe/authenticate"
        return cast(Dict[str, Any], self._make_request("GET", path))

    def probe_list_files(self, sink_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe/buckets"
        return cast(Dict[str, Any], self._make_request("POST", path, json=payload))

    def probe_tree(self, sink_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe/tree"
        return cast(Dict[str, Any], self._make_request("POST", path, json=payload))

    def probe_read_file(self, sink_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe/files"
        return cast(Dict[str, Any], self._make_request("POST", path, json=payload))

    def probe_detect_schemas(
        self, sink_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe/schemas"
        return cast(Dict[str, Any], self._make_request("POST", path, json=payload))

    def probe_quarantine_sample(
        self, sink_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/probe/quarantine/sample"
        return cast(Dict[str, Any], self._make_request("POST", path, json=payload))

    def get_quarantine_settings(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/quarantine_settings"
        return cast(Dict[str, Any], self._make_request("GET", path))

    def create_quarantine_settings(
        self, sink_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/quarantine_settings"
        return cast(Dict[str, Any], self._make_request("POST", path, json=payload))

    def update_quarantine_settings(
        self, sink_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/quarantine_settings"
        return cast(Dict[str, Any], self._make_request("PUT", path, json=payload))

    def delete_quarantine_settings(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/quarantine_settings"
        return cast(Dict[str, Any], self._make_request("DELETE", path))

    def get_dashboard_transforms(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/dashboard_transforms"
        return cast(Dict[str, Any], self._make_request("GET", path))

    def create_dashboard_transforms(
        self, sink_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/dashboard_transforms"
        return cast(Dict[str, Any], self._make_request("POST", path, json=payload))

    def update_dashboard_transforms(
        self, sink_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/dashboard_transforms"
        return cast(Dict[str, Any], self._make_request("PUT", path, json=payload))

    def delete_dashboard_transforms(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/dashboard_transforms"
        return cast(Dict[str, Any], self._make_request("DELETE", path))

    @missing_route("POST", "/data_sinks/config/validate")
    def validate_config(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._make_request("POST", f"{self._path}/config/validate", json=payload),
        )

    def test_config(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._make_request("POST", f"{self._path}/test_config", json=payload),
        )

    def run_status(self, sink_id: int, run_id: Optional[int] = None) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/run_status"
        if run_id is not None:
            path = f"{path}/{run_id}"
        return cast(Dict[str, Any], self._make_request("GET", path))

    def run_analysis(self, sink_id: int, **params: Any) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/run_analysis"
        return cast(Dict[str, Any], self._make_request("GET", path, params=params))

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

    def list_api_keys(self, sink_id: int, **params: Any) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys"
        return cast(Dict[str, Any], self._make_request("GET", path, params=params))

    def search_api_keys(
        self, sink_id: int, filters: Dict[str, Any], **params: Any
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/search"
        return cast(
            Dict[str, Any],
            self._make_request("POST", path, json=filters, params=params),
        )

    def get_api_key(self, sink_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/{api_key_id}"
        return cast(Dict[str, Any], self._make_request("GET", path))

    def create_api_key(self, sink_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys"
        return cast(Dict[str, Any], self._make_request("POST", path, json=payload))

    def update_api_key(
        self, sink_id: int, api_key_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/{api_key_id}"
        return cast(Dict[str, Any], self._make_request("PUT", path, json=payload))

    def rotate_api_key(self, sink_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/{api_key_id}/rotate"
        return cast(Dict[str, Any], self._make_request("PUT", path))

    def activate_api_key(self, sink_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/{api_key_id}/activate"
        return cast(Dict[str, Any], self._make_request("PUT", path))

    def pause_api_key(self, sink_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/{api_key_id}/pause"
        return cast(Dict[str, Any], self._make_request("PUT", path))

    def pause_all_api_keys(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/pause"
        return cast(Dict[str, Any], self._make_request("PUT", path))

    def delete_api_key(self, sink_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/api_keys/{api_key_id}"
        return cast(Dict[str, Any], self._make_request("DELETE", path))

    def trigger_quarantine_aggregation(
        self, sink_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/trigger_quarantine_aggregation"
        return cast(Dict[str, Any], self._make_request("POST", path, json=payload))

    def get_quarantine_aggregation(self, sink_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{sink_id}/quarantine_aggregation"
        return cast(Dict[str, Any], self._make_request("GET", path))

    def data_sinks_update_data_sink(
        self,
        data_sink_id: int,
        data: Dict[str, Any],
        expand: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Partially update a data sink (PATCH).

        Args:
            data_sink_id: Data sink ID
            data: Fields to update
            expand: Include expanded references

        Returns:
            Updated data sink
        """
        params = {"expand": expand}
        path = f"{self._path}/{data_sink_id}"
        return cast(
            Dict[str, Any],
            self._make_request(
                "PATCH",
                path,
                params={k: v for k, v in params.items() if v is not None},
                json=data,
            ),
        )

    def validate_data_sink_config(
        self, data_sink_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate the configuration of a data sink.

        Args:
            data_sink_id: Data sink ID
            data: Configuration to validate. Default is the stored sink config.

        Returns:
            Validation result
        """
        path = f"{self._path}/{data_sink_id}/config/validate"
        return cast(Dict[str, Any], self._make_request("POST", path, json=data))

    def list_flow_accessors_via_data_sink(
        self, resource_id: int
    ) -> List[Dict[str, Any]]:
        """
        List the accessors of the flow of a data sink.

        Args:
            resource_id: Data sink ID

        Returns:
            List of accessors
        """
        path = f"{self._path}/{resource_id}/flow/accessors"
        return cast(List[Dict[str, Any]], self._make_request("GET", path))

    def reset_flow_accessors_via_data_sink(
        self, resource_id: int, data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Replace the accessors of the flow of a data sink.

        Args:
            resource_id: Data sink ID
            data: Accessors payload

        Returns:
            Updated list of accessors
        """
        path = f"{self._path}/{resource_id}/flow/accessors"
        return cast(List[Dict[str, Any]], self._make_request("POST", path, json=data))

    def add_flow_accessors_via_data_sink(
        self, resource_id: int, data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Add accessors to the flow of a data sink.

        Args:
            resource_id: Data sink ID
            data: Accessors payload

        Returns:
            Updated list of accessors
        """
        path = f"{self._path}/{resource_id}/flow/accessors"
        return cast(List[Dict[str, Any]], self._make_request("PUT", path, json=data))

    def remove_flow_accessors_via_data_sink(
        self, resource_id: int, data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Remove accessors from the flow of a data sink.

        Args:
            resource_id: Data sink ID
            data: Accessors payload to remove

        Returns:
            Remaining list of accessors
        """
        path = f"{self._path}/{resource_id}/flow/accessors"
        return cast(List[Dict[str, Any]], self._make_request("DELETE", path, json=data))

    def list_flow_docs_via_data_sink(self, resource_id: int) -> Any:
        """
        List the docs of the flow of a data sink.

        Args:
            resource_id: Data sink ID

        Returns:
            Docs payload
        """
        path = f"{self._path}/{resource_id}/flow/docs"
        return self._make_request("GET", path)

    def reset_flow_docs_via_data_sink(
        self, resource_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Replace the docs of the flow of a data sink.

        Args:
            resource_id: Data sink ID
            data: Docs payload

        Returns:
            Updated docs payload
        """
        path = f"{self._path}/{resource_id}/flow/docs"
        return self._make_request("POST", path, json=data)

    def add_flow_docs_via_data_sink(
        self, resource_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Add docs to the flow of a data sink.

        Args:
            resource_id: Data sink ID
            data: Docs payload to add

        Returns:
            Updated docs payload
        """
        path = f"{self._path}/{resource_id}/flow/docs"
        return self._make_request("PUT", path, json=data)

    def remove_flow_docs_via_data_sink(
        self, resource_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Remove docs from the flow of a data sink.

        Args:
            resource_id: Data sink ID
            data: Docs payload to remove

        Returns:
            Remaining docs payload
        """
        path = f"{self._path}/{resource_id}/flow/docs"
        return self._make_request("DELETE", path, json=data)

    def activate_flow_via_data_sink(
        self,
        resource_id: int,
        all: Optional[bool] = None,
        full_tree: Optional[bool] = None,
        run_now: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Activate the flow of a data sink.

        Args:
            resource_id: Data sink ID
            all: Activate the entire flow tree
            full_tree: Include the full tree in the response
            run_now: Run value passed to the backend

        Returns:
            Flow response
        """
        params = {"all": all, "full_tree": full_tree, "run_now": run_now}
        path = f"{self._path}/{resource_id}/flow/activate"
        return cast(
            Dict[str, Any],
            self._make_request(
                "PUT", path, params={k: v for k, v in params.items() if v is not None}
            ),
        )

    def pause_flow_via_data_sink(
        self,
        resource_id: int,
        all: Optional[bool] = None,
        full_tree: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Pause the flow of a data sink.

        Args:
            resource_id: Data sink ID
            all: Pause the entire flow tree
            full_tree: Include the full tree in the response

        Returns:
            Flow response
        """
        params = {"all": all, "full_tree": full_tree}
        path = f"{self._path}/{resource_id}/flow/pause"
        return cast(
            Dict[str, Any],
            self._make_request(
                "PUT", path, params={k: v for k, v in params.items() if v is not None}
            ),
        )

    def data_sinks_flow_audit_log(
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
    ) -> Any:
        """
        Get the audit log for the flow of a data sink.

        Args:
            resource_id: Data sink ID
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

    def data_sinks_get_data_sink_offset(
        self, data_sink_id: int, data_set_id: Optional[int] = None
    ) -> Any:
        """
        Get the offset of a data sink, optionally for one nexset.

        Args:
            data_sink_id: Data sink ID
            data_set_id: Nexset ID filter

        Returns:
            Offset payload
        """
        params = {"data_set_id": data_set_id}
        path = f"{self._path}/{data_sink_id}/offset"
        return self._make_request(
            "GET", path, params={k: v for k, v in params.items() if v is not None}
        )

    def data_sinks_get_data_sink_quarantine_offset(
        self, data_sink_id: int, data_set_id: Optional[int] = None
    ) -> Any:
        """
        Get the quarantine offset of a data sink, optionally for one nexset.

        Args:
            data_sink_id: Data sink ID
            data_set_id: Nexset ID filter

        Returns:
            Quarantine offset payload
        """
        params = {"data_set_id": data_set_id}
        path = f"{self._path}/{data_sink_id}/quarantine/offset"
        return self._make_request(
            "GET", path, params={k: v for k, v in params.items() if v is not None}
        )

    def data_sinks_get_data_sink_run_status(
        self, data_sink_id: int, run_id: Optional[str] = None
    ) -> Any:
        """
        Get the run status of a data sink, optionally for one run.

        Args:
            data_sink_id: Data sink ID
            run_id: Run ID filter

        Returns:
            Run status payload
        """
        params = {"run_id": run_id}
        path = f"{self._path}/{data_sink_id}/run_status"
        return self._make_request(
            "GET", path, params={k: v for k, v in params.items() if v is not None}
        )

    def data_sinks_probe_list_files_in_bucket_data_sink(
        self, data_sink_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Probe a data sink to list files in a bucket (PUT).

        Args:
            data_sink_id: Data sink ID
            data: Probe input

        Returns:
            Probe result
        """
        path = f"{self._path}/{data_sink_id}/probe/buckets"
        return self._make_request("PUT", path, json=data)

    def data_sinks_probe_read_file_data_sink(
        self, data_sink_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Probe a data sink to read a file (PUT).

        Args:
            data_sink_id: Data sink ID
            data: Probe input

        Returns:
            Probe result
        """
        path = f"{self._path}/{data_sink_id}/probe/files"
        return self._make_request("PUT", path, json=data)

    def data_sinks_probe_read_quarantine_data_sink(
        self, data_sink_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Probe a data sink to read a quarantine sample (PUT).

        Args:
            data_sink_id: Data sink ID
            data: Probe input

        Returns:
            Probe result
        """
        path = f"{self._path}/{data_sink_id}/probe/quarantine/sample"
        return self._make_request("PUT", path, json=data)

    def data_sinks_probe_detect_schemas_data_sink(
        self, data_sink_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Probe a data sink to detect schemas (PUT).

        Args:
            data_sink_id: Data sink ID
            data: Probe input

        Returns:
            Probe result
        """
        path = f"{self._path}/{data_sink_id}/probe/schemas"
        return self._make_request("PUT", path, json=data)

    def data_sinks_probe_list_tree_data_sink(
        self, data_sink_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Probe a data sink to list the tree (PUT).

        Args:
            data_sink_id: Data sink ID
            data: Probe input

        Returns:
            Probe result
        """
        path = f"{self._path}/{data_sink_id}/probe/tree"
        return self._make_request("PUT", path, json=data)
