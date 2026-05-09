from typing import Any, Dict, List, Union

from nexla_sdk.models.dashboard_transforms.requests import (
    DashboardTransformCreate,
    DashboardTransformUpdate,
)
from nexla_sdk.models.dashboard_transforms.responses import DashboardTransform
from nexla_sdk.resources.base_resource import BaseResource


class DashboardTransformsResource(BaseResource):
    """Resource for dashboard transforms (global endpoints)."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/dashboard_transforms"
        self._model_class = DashboardTransform

    def list(self, **kwargs) -> List[DashboardTransform]:
        return super().list(**kwargs)

    def list_all(self, **params) -> List[DashboardTransform]:
        response = self._make_request("GET", f"{self._path}/all", params=params)
        return self._parse_response(response)

    def get(self, dashboard_transform_id: int) -> DashboardTransform:
        return super().get(dashboard_transform_id)

    def create(
        self, data: Union[DashboardTransformCreate, Dict[str, Any]]
    ) -> DashboardTransform:
        return super().create(data)

    def update(
        self,
        dashboard_transform_id: int,
        data: Union[DashboardTransformUpdate, Dict[str, Any]],
    ) -> DashboardTransform:
        return super().update(dashboard_transform_id, data)

    def delete(self, dashboard_transform_id: int) -> Dict[str, Any]:
        return super().delete(dashboard_transform_id)
