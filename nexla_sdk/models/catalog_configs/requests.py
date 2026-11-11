from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel


class CatalogConfigCreate(BaseModel):
    name: str
    description: Optional[str] = None
    data_credentials_id: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    templates: Optional[Dict[str, Any]] = None
    mode: Optional[str] = None


class CatalogConfigUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data_credentials_id: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    templates: Optional[Dict[str, Any]] = None
    mode: Optional[str] = None
