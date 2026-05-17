from typing import Any, Dict

from nexla_sdk.models.common import FlowNode
from nexla_sdk.resources.base_resource import BaseResource


class FlowNodesResource(BaseResource):
    """Resource for flow nodes."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/flow_nodes"
        self._model_class = FlowNode

    def get(self, flow_node_id: int) -> FlowNode:
        return super().get(flow_node_id)

    def update(self, flow_node_id: int, data: Dict[str, Any]) -> FlowNode:
        return super().update(flow_node_id, data)

    def list_origin_nodes_condensed(self, **params) -> Dict[str, Any]:
        return self._make_request("GET", "/flows/all/condensed", params=params)

    def list_flows_minimal(self, **params) -> Dict[str, Any]:
        return self._make_request("GET", "/flows/all/minimal", params=params)

    def get_access_insights(self, flow_node_id: int, **params) -> Dict[str, Any]:
        return self._make_request("GET", f"/flows/{flow_node_id}/access", params=params)
