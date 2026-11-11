from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.vendor_endpoints.responses import VendorEndpoint


class ResourceParameter(BaseModel):
    id: int
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    data_type: Optional[str] = None
    order: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    global_param: Optional[bool] = Field(default=None, alias="global")
    vendor_endpoint: Optional[VendorEndpoint] = None
    allowed_values: Optional[List[Any]] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
