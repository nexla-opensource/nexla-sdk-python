"""Vendor response models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from nexla_sdk.models.base import BaseModel


class VendorRef(BaseModel):
    """Minimal vendor reference."""

    id: int
    name: Optional[str] = None
    display_name: Optional[str] = None


class Vendor(BaseModel):
    """Vendor response model.

    Vendors represent third-party service providers that can be
    connected via auth templates and endpoints.
    """

    id: int
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    small_logo: Optional[str] = None
    logo: Optional[str] = None
    connection_type: Optional[str] = None  # From associated connector
    auth_templates: Optional[List[Any]] = Field(default_factory=list)  # IDs or objects
    vendor_endpoints: Optional[List[Any]] = Field(
        default_factory=list
    )  # IDs or objects
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
