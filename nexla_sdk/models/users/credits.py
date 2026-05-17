from datetime import datetime
from typing import Optional

from nexla_sdk.models.base import BaseModel


class UserCredit(BaseModel):
    id: int
    owner_id: Optional[int] = None
    org_id: Optional[int] = None
    grant_type: Optional[str] = None
    credits_available: Optional[int] = None
    credits: Optional[int] = None
    credits_used: Optional[int] = None
    credits_monthly: Optional[int] = None
    credits_used_in_month: Optional[int] = None
    granted_at: Optional[datetime] = None
    refreshed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class UserCreditCreate(BaseModel):
    grant_type: Optional[str] = None
    credits: Optional[int] = None
    credits_monthly: Optional[int] = None
    expires_at: Optional[str] = None
