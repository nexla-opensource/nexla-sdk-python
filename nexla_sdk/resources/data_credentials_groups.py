from typing import Any, Dict, List, Union

from nexla_sdk.models.credentials.responses import Credential
from nexla_sdk.models.data_credentials_groups.requests import (
    DataCredentialsGroupCreate,
    DataCredentialsGroupRemoveCredentials,
    DataCredentialsGroupUpdate,
)
from nexla_sdk.models.data_credentials_groups.responses import DataCredentialsGroup
from nexla_sdk.resources.base_resource import BaseResource


class DataCredentialsGroupsResource(BaseResource):
    """Resource for managing data credentials groups."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/data_credentials_groups"
        self._model_class = DataCredentialsGroup

    def list(self, **kwargs) -> List[DataCredentialsGroup]:
        return super().list(**kwargs)

    def get(self, group_id: int, expand: bool = False) -> DataCredentialsGroup:
        return super().get(group_id, expand)

    def create(
        self, data: Union[DataCredentialsGroupCreate, Dict[str, Any]]
    ) -> DataCredentialsGroup:
        return super().create(data)

    def update(
        self,
        group_id: int,
        data: Union[DataCredentialsGroupUpdate, Dict[str, Any]],
    ) -> DataCredentialsGroup:
        return super().update(group_id, data)

    def delete(self, group_id: int) -> Dict[str, Any]:
        return super().delete(group_id)

    def list_credentials(self, group_id: int, **params) -> List[Credential]:
        path = f"{self._path}/{group_id}/data_credentials"
        response = self._make_request("GET", path, params=params)
        return [Credential.model_validate(item) for item in (response or [])]

    def remove_credentials(
        self,
        group_id: int,
        payload: Union[DataCredentialsGroupRemoveCredentials, Dict[str, Any]],
    ) -> Dict[str, Any]:
        path = f"{self._path}/{group_id}/data_credentials"
        data = self._serialize_data(payload)
        return self._make_request("DELETE", path, json=data)
