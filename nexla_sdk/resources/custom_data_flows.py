from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.custom_data_flows.requests import (
    CustomDataFlowCreate,
    CustomDataFlowUpdate,
)
from nexla_sdk.models.custom_data_flows.responses import CustomDataFlow
from nexla_sdk.resources.base_resource import BaseResource


class CustomDataFlowsResource(BaseResource):
    """Resource for managing custom data flows."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/custom_data_flows"
        self._model_class = CustomDataFlow

    def list(self, **kwargs) -> List[CustomDataFlow]:
        return super().list(**kwargs)

    def list_accessible(self, **params) -> List[CustomDataFlow]:
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
        return self._parse_response(response)

    def get_metrics(self, custom_data_flow_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{custom_data_flow_id}/metrics"
        return self._make_request("GET", path, params=params)

    def edit_code_containers(
        self, custom_data_flow_id: int, payload: Dict[str, Any], mode: str
    ) -> Dict[str, Any]:
        path = f"{self._path}/{custom_data_flow_id}/code_containers"
        method_map = {"list": "GET", "reset": "POST", "add": "PUT", "remove": "DELETE"}
        method = method_map.get(mode, "GET")
        return self._make_request(method, path, json=payload)

    def edit_data_credentials(
        self, custom_data_flow_id: int, payload: Dict[str, Any], mode: str
    ) -> Dict[str, Any]:
        path = f"{self._path}/{custom_data_flow_id}/data_credentials"
        method_map = {"list": "GET", "reset": "POST", "add": "PUT", "remove": "DELETE"}
        method = method_map.get(mode, "GET")
        return self._make_request(method, path, json=payload)

    def search(self, filters: Dict[str, Any], **params) -> List[CustomDataFlow]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params) -> List[CustomDataFlow]:
        return super().search_tags(tags, **params)
