from typing import Any, Dict, List, Union

from nexla_sdk.models.resource_parameters.requests import (
    ResourceParameterCreate,
    ResourceParameterUpdate,
)
from nexla_sdk.models.resource_parameters.responses import ResourceParameter
from nexla_sdk.resources.base_resource import BaseResource


class ResourceParametersResource(BaseResource):
    """Resource for managing resource parameters."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/resource_parameters"
        self._model_class = ResourceParameter

    def list(self, **kwargs) -> List[ResourceParameter]:
        return super().list(**kwargs)

    def get(self, resource_parameter_id: int) -> ResourceParameter:
        return super().get(resource_parameter_id)

    def create(
        self, data: Union[ResourceParameterCreate, Dict[str, Any]]
    ) -> ResourceParameter:
        return super().create(data)

    def update(
        self,
        resource_parameter_id: int,
        data: Union[ResourceParameterUpdate, Dict[str, Any]],
    ) -> ResourceParameter:
        return super().update(resource_parameter_id, data)

    def delete(self, resource_parameter_id: int) -> Dict[str, Any]:
        return super().delete(resource_parameter_id)
