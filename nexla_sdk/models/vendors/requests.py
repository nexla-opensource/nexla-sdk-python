"""Vendor request models."""

from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel


class VendorCreate(BaseModel):
    """Request model for creating a vendor (super user only)."""

    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    small_logo: Optional[str] = None
    logo: Optional[str] = None
    connector_id: Optional[int] = None


class VendorUpdate(BaseModel):
    """Request model for updating a vendor (super user only)."""

    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    small_logo: Optional[str] = None
    logo: Optional[str] = None
