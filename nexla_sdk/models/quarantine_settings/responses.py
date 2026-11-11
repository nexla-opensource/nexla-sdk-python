from datetime import datetime
from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.common import Organization, Owner
from nexla_sdk.models.credentials.responses import Credential


class QuarantineSetting(BaseModel):
    id: int
    owner: Optional[Owner] = None
    org: Optional[Organization] = None
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    data_credentials_id: Optional[int] = None
    credentials_type: Optional[str] = None
    data_credentials: Optional[Credential] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
