"""Notification Setting request models."""

from typing import Any, Dict, Optional

from pydantic import ConfigDict, Field

from nexla_sdk.models.base import BaseModel


class NotificationSettingCreate(BaseModel):
    """Notification Setting creation request model."""

    model_config = ConfigDict(populate_by_name=True)

    notification_type_id: int
    resource_id: Optional[int] = None
    resource_type: Optional[str] = None
    channel: str = Field(..., description="Notification channel (e.g., email, slack)")
    priority: int = Field(default=0, ge=0, le=100, description="Priority level")
    status: str = Field(
        default="ENABLED",
        description="Status (ENABLED, DISABLED)",
    )
    payload: Optional[Dict[str, Any]] = None


class NotificationSettingUpdate(BaseModel):
    """Notification Setting update request model."""

    model_config = ConfigDict(populate_by_name=True)

    channel: Optional[str] = None
    priority: Optional[int] = Field(default=None, ge=0, le=100)
    status: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
