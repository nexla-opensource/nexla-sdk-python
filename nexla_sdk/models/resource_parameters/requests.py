from typing import Any, Dict, List, Optional

from nexla_sdk.models.base import BaseModel


class ResourceParameterCreate(BaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    data_type: Optional[str] = None
    order: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    global_param: Optional[bool] = None
    vendor_endpoint_id: Optional[int] = None
    allowed_values: Optional[List[Any]] = None


class ResourceParameterUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    data_type: Optional[str] = None
    order: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    global_param: Optional[bool] = None
    vendor_endpoint_id: Optional[int] = None
    allowed_values: Optional[List[Any]] = None
