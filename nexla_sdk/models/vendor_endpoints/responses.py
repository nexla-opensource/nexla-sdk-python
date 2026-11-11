from datetime import datetime
from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.vendors.responses import VendorRef


class VendorEndpoint(BaseModel):
    id: int
    name: Optional[str] = None
    resource_type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    vendor: Optional[VendorRef] = None
    vendor_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
