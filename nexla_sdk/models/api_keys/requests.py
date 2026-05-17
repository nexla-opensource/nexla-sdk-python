from typing import Optional

from nexla_sdk.models.base import BaseModel


class ApiKeyCreate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    scope: Optional[str] = None
    expires_at: Optional[str] = None


class ApiKeyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    scope: Optional[str] = None
    expires_at: Optional[str] = None
