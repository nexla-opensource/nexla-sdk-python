from typing import TYPE_CHECKING, Any, Dict, cast

from nexla_sdk.models.common import FlowNode
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class FlowNodesResource(BaseResource[FlowNode]):
    """Resource for flow nodes."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/flow_nodes"
        self._model_class = FlowNode

    def get(self, flow_node_id: int) -> FlowNode:  # type: ignore[override]  # keeps public get() signature; base get() also takes expand
        return super().get(flow_node_id)

    def update(self, flow_node_id: int, data: Dict[str, Any]) -> FlowNode:
        return super().update(flow_node_id, data)

    def list_origin_nodes_condensed(self, **params: Any) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._make_request("GET", "/flows/all/condensed", params=params),
        )

    def list_flows_minimal(self, **params: Any) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._make_request("GET", "/flows/all/minimal", params=params),
        )

    def get_access_insights(  # type: ignore[override]  # keeps public parameter name; base uses resource_id
        self, flow_node_id: int, **params: Any
    ) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._make_request("GET", f"/flows/{flow_node_id}/access", params=params),
        )
