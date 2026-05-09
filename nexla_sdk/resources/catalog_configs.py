from typing import Any, Dict, List, Union

from nexla_sdk.models.catalog_configs.requests import (
    CatalogConfigCreate,
    CatalogConfigUpdate,
)
from nexla_sdk.models.catalog_configs.responses import CatalogConfig
from nexla_sdk.resources.base_resource import BaseResource


class CatalogConfigsResource(BaseResource):
    """Resource for managing catalog configs."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/catalog_configs"
        self._model_class = CatalogConfig

    def list(self, **kwargs) -> List[CatalogConfig]:
        return super().list(**kwargs)

    def list_all(self, **params) -> List[CatalogConfig]:
        response = self._make_request("GET", f"{self._path}/all", params=params)
        return self._parse_response(response)

    def get(self, catalog_config_id: int) -> CatalogConfig:
        return super().get(catalog_config_id)

    def create(self, data: Union[CatalogConfigCreate, Dict[str, Any]]) -> CatalogConfig:
        return super().create(data)

    def update(
        self, catalog_config_id: int, data: Union[CatalogConfigUpdate, Dict[str, Any]]
    ) -> CatalogConfig:
        return super().update(catalog_config_id, data)

    def delete(self, catalog_config_id: int) -> Dict[str, Any]:
        return super().delete(catalog_config_id)

    def mock_catalog_add(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/mock_catalog_add", json=payload)

    def check_job_status(self, catalog_config_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{catalog_config_id}/check_job_status"
        return self._make_request("GET", path)

    def start_bulk_create_update(self, catalog_config_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{catalog_config_id}/bulk_create_update_refs"
        return self._make_request("GET", path)
