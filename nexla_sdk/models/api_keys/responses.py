"""API Keys response models."""

from datetime import datetime
from typing import List, Optional

from nexla_sdk.models.base import BaseModel


class ApiKey(BaseModel):
    """API key response model.

    API keys are used for programmatic access to specific resources
    like datasets, data sources, data sinks, and users.
    """

    id: int
    owner_id: Optional[int] = None
    org_id: Optional[int] = None
    data_set_id: Optional[int] = None
    data_source_id: Optional[int] = None
    data_sink_id: Optional[int] = None
    user_id: Optional[int] = None
    cluster_id: Optional[int] = None  # Super user only
    cluster_uid: Optional[str] = None  # Super user only
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    scope: Optional[str] = None
    api_key: Optional[str] = None
    url: Optional[str] = None
    last_rotated_key: Optional[str] = None
    last_rotated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ApiKeysIndex(BaseModel):
    """Response model for API keys index (grouped by type)."""

    data_sets: Optional[List[ApiKey]] = None
    data_sinks: Optional[List[ApiKey]] = None
    data_sources: Optional[List[ApiKey]] = None
    users: Optional[List[ApiKey]] = None
