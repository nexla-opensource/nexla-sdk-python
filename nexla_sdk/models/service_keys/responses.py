"""Service key response models."""

from datetime import datetime
from typing import Optional

from nexla_sdk.models.base import BaseModel


class ServiceKey(BaseModel):
    """Service key response model.

    Service keys are long-lived credentials used for programmatic API access.
    They can be rotated and have lifecycle management (activate/pause).
    """

    id: int
    owner_id: Optional[int] = None
    org_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: str  # INIT, ACTIVE, PAUSED
    api_key: str
    last_rotated_key: Optional[str] = None
    last_rotated_at: Optional[datetime] = None
    data_source_id: Optional[int] = None
    cluster_id: Optional[int] = None  # Super user only
    cluster_uid: Optional[str] = None  # Super user only
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
