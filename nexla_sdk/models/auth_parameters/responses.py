from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import Field

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.vendors.responses import Vendor

if TYPE_CHECKING:
    from nexla_sdk.models.auth_templates.responses import AuthTemplate


class AuthParameter(BaseModel):
    id: int
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[str] = None
    order: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    secured: Optional[bool] = None
    global_param: Optional[bool] = Field(default=None, alias="global")
    vendor: Optional[Vendor] = None
    auth_template: Optional["AuthTemplate"] = None
    allowed_values: Optional[List[Any]] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
