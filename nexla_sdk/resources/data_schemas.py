from typing import Any, Dict, List, Optional

from nexla_sdk.models.common import LogEntry
from nexla_sdk.models.data_schemas.responses import DataSchema
from nexla_sdk.resources.base_resource import BaseResource


class DataSchemasResource(BaseResource):
    """Resource for data schemas."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/data_schemas"
        self._model_class = DataSchema

    def list(self, **kwargs) -> List[DataSchema]:
        return super().list(**kwargs)

    def list_all(self, **params) -> List[DataSchema]:
        response = self._make_request("GET", f"{self._path}/all", params=params)
        return self._parse_response(response)

    def list_public(self, **params) -> List[DataSchema]:
        response = self._make_request("GET", f"{self._path}/public", params=params)
        return self._parse_response(response)

    def list_accessible(self, **params) -> List[DataSchema]:
        return super().list_accessible(**params)

    def get(self, schema_id: int, expand: bool = False) -> DataSchema:
        return super().get(schema_id, expand)

    def create(self, data: Dict[str, Any]) -> DataSchema:
        return super().create(data)

    def update(self, schema_id: int, data: Dict[str, Any]) -> DataSchema:
        return super().update(schema_id, data)

    def delete(self, schema_id: int) -> Dict[str, Any]:
        return super().delete(schema_id)

    def get_metrics(
        self, schema_id: int, metrics_name: Optional[str] = None, **params
    ) -> Dict[str, Any]:
        path = f"{self._path}/{schema_id}/metrics"
        if metrics_name:
            path = f"{path}/{metrics_name}"
        return self._make_request("GET", path, params=params)

    def search(self, filters: Dict[str, Any], **params) -> List[DataSchema]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params) -> List[DataSchema]:
        return super().search_tags(tags, **params)

    def copy(
        self, schema_id: int, payload: Optional[Dict[str, Any]] = None
    ) -> DataSchema:
        return super().copy(schema_id, payload)

    def get_audit_log(self, schema_id: int, **params) -> List[LogEntry]:
        path = f"{self._path}/{schema_id}/audit_log"
        response = self._make_request("GET", path, params=params)
        return [LogEntry.model_validate(item) for item in (response or [])]
