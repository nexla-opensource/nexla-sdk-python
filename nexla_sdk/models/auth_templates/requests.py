"""Auth template request models."""

from typing import Any, Dict, List, Optional

from nexla_sdk.models.base import BaseModel


class AuthParameterCreate(BaseModel):
    """Auth parameter for template creation."""

    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    param_type: Optional[str] = None
    required: Optional[bool] = None
    default_value: Optional[Any] = None
    config: Optional[Dict[str, Any]] = None


class AuthTemplateCreate(BaseModel):
    """Request model for creating an auth template (super user only)."""

    name: str
    vendor_id: int
    display_name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    auth_parameters: Optional[List[AuthParameterCreate]] = None


class AuthTemplateUpdate(BaseModel):
    """Request model for updating an auth template (super user only)."""

    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
