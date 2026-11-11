from typing import Any, Dict, List, Optional

from nexla_sdk.models.base import BaseModel


class CustomDataFlowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    flow_type: Optional[str] = None
    status: Optional[str] = None
    managed: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    code_container_ids: Optional[List[int]] = None
    data_credentials_ids: Optional[List[int]] = None


class CustomDataFlowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    flow_type: Optional[str] = None
    status: Optional[str] = None
    managed: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    code_container_ids: Optional[List[int]] = None
    data_credentials_ids: Optional[List[int]] = None
