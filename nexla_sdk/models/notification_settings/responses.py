"""Notification Setting response models."""

from datetime import datetime
from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel


class NotificationSetting(BaseModel):
    """Notification Setting response model."""

    id: int
    notification_type_id: int
    resource_id: Optional[int] = None
    resource_type: Optional[str] = None
    channel: str
    priority: int = 0
    status: str = "ENABLED"
    payload: Optional[Dict[str, Any]] = None
    owner_id: Optional[int] = None
    org_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class NotificationSettingBrief(BaseModel):
    """Brief Notification Setting response model for list views."""

    id: int
    notification_type_id: int
    channel: str
    priority: int = 0
    status: str = "ENABLED"
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
