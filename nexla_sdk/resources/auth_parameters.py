from typing import Any, Dict, List, Union

from nexla_sdk.models.auth_parameters.requests import (
    AuthParameterCreate,
    AuthParameterUpdate,
)
from nexla_sdk.models.auth_parameters.responses import AuthParameter
from nexla_sdk.resources.base_resource import BaseResource


class AuthParametersResource(BaseResource):
    """Resource for managing auth parameters."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/auth_parameters"
        self._model_class = AuthParameter

    def list(self, **kwargs) -> List[AuthParameter]:
        return super().list(**kwargs)

    def get(self, auth_parameter_id: int) -> AuthParameter:
        return super().get(auth_parameter_id)

    def create(self, data: Union[AuthParameterCreate, Dict[str, Any]]) -> AuthParameter:
        return super().create(data)

    def update(
        self,
        auth_parameter_id: int,
        data: Union[AuthParameterUpdate, Dict[str, Any]],
    ) -> AuthParameter:
        return super().update(auth_parameter_id, data)

    def delete(self, auth_parameter_id: int) -> Dict[str, Any]:
        return super().delete(auth_parameter_id)
