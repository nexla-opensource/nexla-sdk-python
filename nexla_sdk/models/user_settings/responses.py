from datetime import datetime
from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.common import Organization, Owner


class UserSetting(BaseModel):
    id: int
    owner: Optional[Owner] = None
    org: Optional[Organization] = None
    user_settings_type: Optional[str] = None
    primary_key_value: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    copied_from_id: Optional[int] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
