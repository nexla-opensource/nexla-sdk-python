from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel


class VendorEndpointCreate(BaseModel):
    name: str
    vendor_id: int
    resource_type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class VendorEndpointUpdate(BaseModel):
    name: Optional[str] = None
    resource_type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
