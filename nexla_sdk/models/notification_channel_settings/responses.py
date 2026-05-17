from datetime import datetime
from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel


class NotificationChannelSetting(BaseModel):
    id: int
    channel: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    owner_id: Optional[int] = None
    org_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
