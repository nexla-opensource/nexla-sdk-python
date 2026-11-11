from datetime import datetime
from typing import Optional

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.common import Organization, Owner


class DataCredentialsGroup(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    credentials_type: Optional[str] = None
    data_credentials_count: Optional[int] = None
    owner: Optional[Owner] = None
    org: Optional[Organization] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
