from typing import Optional

from nexla_sdk.models.base import BaseModel


class DashboardTransformCreate(BaseModel):
    code_container_id: int


class DashboardTransformUpdate(BaseModel):
    code_container_id: Optional[int] = None
