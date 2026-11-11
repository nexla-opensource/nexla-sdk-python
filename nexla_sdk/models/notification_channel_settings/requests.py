from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel


class NotificationChannelSettingCreate(BaseModel):
    channel: str
    config: Optional[Dict[str, Any]] = None
    org_id: Optional[int] = None


class NotificationChannelSettingUpdate(BaseModel):
    channel: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
