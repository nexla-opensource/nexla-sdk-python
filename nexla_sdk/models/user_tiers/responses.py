from typing import Optional

from nexla_sdk.models.base import BaseModel


class UserTier(BaseModel):
    id: int
    name: Optional[str] = None
    display_name: Optional[str] = None
    record_count_limit: Optional[int] = None
    record_count_limit_time: Optional[str] = None
    data_source_count_limit: Optional[int] = None
    trial_period_days: Optional[int] = None
