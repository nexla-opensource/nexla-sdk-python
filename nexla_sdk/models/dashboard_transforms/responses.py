from typing import Optional

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.code_containers.responses import CodeContainer
from nexla_sdk.models.common import Organization, Owner


class DashboardTransform(BaseModel):
    id: int
    owner: Optional[Owner] = None
    org: Optional[Organization] = None
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    error_transform: Optional[CodeContainer] = None
