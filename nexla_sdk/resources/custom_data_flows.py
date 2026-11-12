from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

from nexla_sdk.models.custom_data_flows.requests import (
    CustomDataFlowCreate,
    CustomDataFlowUpdate,
)
from nexla_sdk.models.custom_data_flows.responses import CustomDataFlow
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class CustomDataFlowsResource(BaseResource[CustomDataFlow]):
    """Resource for managing custom data flows."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/custom_data_flows"
        self._model_class = CustomDataFlow

    def list(self, **kwargs: Any) -> List[CustomDataFlow]:  # type: ignore[override]  # keeps public list() signature; base list() also takes positional filters
        return super().list(**kwargs)

    def list_accessible(self, **params: Any) -> List[CustomDataFlow]:
        return super().list_accessible(**params)

    def get(self, custom_data_flow_id: int, expand: bool = False) -> CustomDataFlow:
        return super().get(custom_data_flow_id, expand)

    def create(
        self, data: Union[CustomDataFlowCreate, Dict[str, Any]]
    ) -> CustomDataFlow:
        return super().create(data)

    def update(
        self,
        custom_data_flow_id: int,
        data: Union[CustomDataFlowUpdate, Dict[str, Any]],
    ) -> CustomDataFlow:
        return super().update(custom_data_flow_id, data)

    def delete(self, custom_data_flow_id: int) -> Dict[str, Any]:
        return super().delete(custom_data_flow_id)

    def copy(
        self, custom_data_flow_id: int, payload: Optional[Dict[str, Any]] = None
    ) -> CustomDataFlow:
        return super().copy(custom_data_flow_id, payload)

    def activate(
        self, custom_data_flow_id: int, activate: bool = True
    ) -> CustomDataFlow:
        action = "activate" if activate else "pause"
        path = f"{self._path}/{custom_data_flow_id}/{action}"
        response = self._make_request("PUT", path)
        return cast(CustomDataFlow, self._parse_response(response))

    def get_metrics(self, custom_data_flow_id: int, **params: Any) -> Dict[str, Any]:
        path = f"{self._path}/{custom_data_flow_id}/metrics"
        return cast(Dict[str, Any], self._make_request("GET", path, params=params))

    def edit_code_containers(
        self, custom_data_flow_id: int, payload: Dict[str, Any], mode: str
    ) -> Dict[str, Any]:
        path = f"{self._path}/{custom_data_flow_id}/code_containers"
        method_map = {"list": "GET", "reset": "POST", "add": "PUT", "remove": "DELETE"}
        method = method_map.get(mode, "GET")
        return cast(Dict[str, Any], self._make_request(method, path, json=payload))

    def edit_data_credentials(
        self, custom_data_flow_id: int, payload: Dict[str, Any], mode: str
    ) -> Dict[str, Any]:
        path = f"{self._path}/{custom_data_flow_id}/data_credentials"
        method_map = {"list": "GET", "reset": "POST", "add": "PUT", "remove": "DELETE"}
        method = method_map.get(mode, "GET")
        return cast(Dict[str, Any], self._make_request(method, path, json=payload))

    def search(self, filters: Dict[str, Any], **params: Any) -> List[CustomDataFlow]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params: Any) -> List[CustomDataFlow]:
        return super().search_tags(tags, **params)

    def custom_data_flows_update_custom_data_flow(
        self, custom_data_flow_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Partially update a custom data flow (PATCH).

        Args:
            custom_data_flow_id: Custom data flow ID
            data: Fields to update. The backend reads this as a JSON body.

        Returns:
            Updated custom data flow as a dict
        """
        path = f"{self._path}/{custom_data_flow_id}"
        return cast(Dict[str, Any], self._make_request("PATCH", path, json=data))

    def get_custom_data_flow_metrics_by_name(
        self, custom_data_flow_id: int, metrics_name: str
    ) -> Dict[str, Any]:
        """
        Get one named metrics group for a custom data flow.

        Args:
            custom_data_flow_id: Custom data flow ID
            metrics_name: Metrics name, for example "summary"

        Returns:
            Metrics response
        """
        path = f"{self._path}/{custom_data_flow_id}/metrics/{metrics_name}"
        return cast(Dict[str, Any], self._make_request("GET", path))
