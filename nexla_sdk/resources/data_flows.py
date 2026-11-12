from typing import TYPE_CHECKING, Any, Dict, List

from nexla_sdk.resources.base_resource import BaseResource
from nexla_sdk.utils.deprecation import missing_route

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class DataFlowsResource(BaseResource):
    """Resource for legacy data_flows endpoints."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/data_flows"
        self._model_class = None

    def list(self, **params) -> List[Dict[str, Any]]:
        response = self._make_request("GET", self._path, params=params)
        return response or []

    def get(self, data_flow_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{data_flow_id}"
        return self._make_request("GET", path, params=params)

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", self._path, json=payload)

    def get_audit_log(self, data_flow_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{data_flow_id}/audit_log"
        return self._make_request("GET", path, params=params)

    @missing_route("GET", "/data_flows/data_source")
    def list_data_source_flows(self, **params) -> List[Dict[str, Any]]:
        return (
            self._make_request("GET", f"{self._path}/data_source", params=params) or []
        )

    def get_data_source_flow(self, data_source_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/data_source/{data_source_id}"
        return self._make_request("GET", path, params=params)

    @missing_route("POST", "/data_flows/data_source")
    def create_data_source_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", f"{self._path}/data_source", json=payload)

    @missing_route("GET", "/data_flows/data_sink")
    def list_data_sink_flows(self, **params) -> List[Dict[str, Any]]:
        return self._make_request("GET", f"{self._path}/data_sink", params=params) or []

    def get_data_sink_flow(self, data_sink_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/data_sink/{data_sink_id}"
        return self._make_request("GET", path, params=params)

    @missing_route("POST", "/data_flows/data_sink")
    def create_data_sink_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", f"{self._path}/data_sink", json=payload)

    def get_flow_audit_log(self, flow_node_id: int) -> Dict[str, Any]:
        return self._make_request("GET", f"/flows/{flow_node_id}/audit_log")

    @missing_route("GET", "/data_flows/data_source/{data_source_id}/audit_log")
    def get_data_source_audit_log(self, data_source_id: int) -> Dict[str, Any]:
        return self._make_request(
            "GET", f"{self._path}/data_source/{data_source_id}/audit_log"
        )

    @missing_route("GET", "/data_flows/data_sink/{data_sink_id}/audit_log")
    def get_data_sink_audit_log(self, data_sink_id: int) -> Dict[str, Any]:
        return self._make_request(
            "GET", f"{self._path}/data_sink/{data_sink_id}/audit_log"
        )
