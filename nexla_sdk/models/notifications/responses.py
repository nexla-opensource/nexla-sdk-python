from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.common import Organization, Owner


class Notification(BaseModel):
    """Notification response model."""

    id: int
    owner: Owner
    org: Organization
    access_roles: List[str]
    level: str
    resource_id: Optional[int] = None
    resource_type: str
    message_id: int
    message: str

    read_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class NotificationType(BaseModel):
    """Notification type information."""

    id: int
    name: str
    description: str
    category: str  # PLATFORM, SYSTEM, DATA
    default: bool
    status: bool
    event_type: str
    resource_type: str


class NotificationChannelSetting(BaseModel):
    """Notification channel configuration."""

    id: int
    owner_id: int
    org_id: int
    channel: str  # APP, EMAIL, SMS, SLACK, WEBHOOKS
    config: Dict[str, Any]


class NotificationSetting(BaseModel):
    """Notification setting configuration."""

    id: int
    org_id: int
    owner_id: int
    channel: str
    notification_resource_type: str
    resource_id: Optional[int] = None
    status: str  # PAUSED, ACTIVE
    notification_type_id: int
    name: str
    description: str
    code: int
    category: str
    event_type: str
    resource_type: str

    config: Dict[str, Any] = Field(default_factory=dict)
    priority: Optional[int] = None


class NotificationCount(BaseModel):
    """Notification count response."""

    count: int


class NotificationSettingBrief(BaseModel):
    """Brief Notification Setting response model for list views."""

    id: int
    notification_type_id: int
    channel: str
    priority: int = 0
    status: str = "ENABLED"
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
