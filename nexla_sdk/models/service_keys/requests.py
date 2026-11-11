"""Service key request models."""

from typing import Optional

from nexla_sdk.models.base import BaseModel


class ServiceKeyCreate(BaseModel):
    """Request model for creating a service key."""

    name: str
    description: str
    data_source_id: Optional[int] = None


class ServiceKeyUpdate(BaseModel):
    """Request model for updating a service key."""

    name: Optional[str] = None
    description: Optional[str] = None
