from typing import TYPE_CHECKING, Any, Dict, List, Union

from nexla_sdk.models.resource_parameters.requests import (
    ResourceParameterCreate,
    ResourceParameterUpdate,
)
from nexla_sdk.models.resource_parameters.responses import ResourceParameter
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class ResourceParametersResource(BaseResource[ResourceParameter]):
    """Resource for managing resource parameters."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/resource_parameters"
        self._model_class = ResourceParameter

    def list(self, **kwargs: Any) -> List[ResourceParameter]:  # type: ignore[override]  # keeps public list() signature; base list() also takes positional filters
        return super().list(**kwargs)

    def get(self, resource_parameter_id: int) -> ResourceParameter:  # type: ignore[override]  # keeps public get() signature; base get() also takes expand
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
