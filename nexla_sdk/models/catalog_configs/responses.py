from datetime import datetime
from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.common import Organization, Owner
from nexla_sdk.models.credentials.responses import Credential


class CatalogConfig(BaseModel):
    id: int
    owner: Optional[Owner] = None
    org: Optional[Organization] = None
    data_credentials: Optional[Credential] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    templates: Optional[Dict[str, Any]] = None
    mode: Optional[str] = None
    job_id: Optional[str] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
