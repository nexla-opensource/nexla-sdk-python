from typing import TYPE_CHECKING, Any, Dict, List, Union, cast

from nexla_sdk.models.dashboard_transforms.requests import (
    DashboardTransformCreate,
    DashboardTransformUpdate,
)
from nexla_sdk.models.dashboard_transforms.responses import DashboardTransform
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class DashboardTransformsResource(BaseResource[DashboardTransform]):
    """Resource for dashboard transforms (global endpoints)."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/dashboard_transforms"
        self._model_class = DashboardTransform

    def list(self, **kwargs: Any) -> List[DashboardTransform]:  # type: ignore[override]  # keeps public list() signature; base list() also takes positional filters
        return super().list(**kwargs)

    def list_all(self, **params: Any) -> List[DashboardTransform]:
        response = self._make_request("GET", f"{self._path}/all", params=params)
        return cast(List[DashboardTransform], self._parse_response(response))

    def get(self, dashboard_transform_id: int) -> DashboardTransform:  # type: ignore[override]  # keeps public get() signature; base get() also takes expand
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
