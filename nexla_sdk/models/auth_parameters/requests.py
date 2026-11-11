from typing import Any, Dict, List, Optional

from nexla_sdk.models.base import BaseModel


class AuthParameterCreate(BaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[str] = None
    order: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    secured: Optional[bool] = None
    global_param: Optional[bool] = None
    auth_template_id: Optional[int] = None
    vendor_id: Optional[int] = None
    allowed_values: Optional[List[Any]] = None


class AuthParameterUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[str] = None
    order: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    secured: Optional[bool] = None
    global_param: Optional[bool] = None
    auth_template_id: Optional[int] = None
    vendor_id: Optional[int] = None
    allowed_values: Optional[List[Any]] = None
