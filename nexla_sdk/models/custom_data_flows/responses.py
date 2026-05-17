from datetime import datetime
from typing import Any, Dict, List, Optional

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.code_containers.responses import CodeContainer
from nexla_sdk.models.common import Organization, Owner
from nexla_sdk.models.credentials.responses import Credential


class CustomDataFlow(BaseModel):
    id: int
    owner: Optional[Owner] = None
    org: Optional[Organization] = None
    name: Optional[str] = None
    description: Optional[str] = None
    flow_type: Optional[str] = None
    status: Optional[str] = None
    managed: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    code_containers: Optional[List[CodeContainer]] = None
    data_credentials: Optional[List[Credential]] = None
    access_roles: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    copied_from_id: Optional[int] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
