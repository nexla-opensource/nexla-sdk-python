from typing import Optional

from nexla_sdk.models.base import BaseModel


class NotificationType(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    default: Optional[bool] = None
    status: Optional[str] = None
    event_type: Optional[str] = None
    resource_type: Optional[str] = None
