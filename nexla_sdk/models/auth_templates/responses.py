"""Auth template response models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.vendors.responses import VendorRef


class AuthTemplateParameter(BaseModel):
    """Auth parameter configuration for auth templates.

    This is a lightweight nested model used within AuthTemplate responses.
    For the full auth parameter resource model, see nexla_sdk.models.auth_parameters.
    """

    id: Optional[int] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    param_type: Optional[str] = None
    required: Optional[bool] = None
    default_value: Optional[Any] = None
    config: Optional[Dict[str, Any]] = None


# Deprecated alias for backward compatibility
AuthParameter = AuthTemplateParameter


class AuthTemplate(BaseModel):
    """Auth template response model.

    Auth templates define authentication configurations for vendors.
    """

    id: int
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    credentials_type: Optional[str] = None  # From associated connector
    vendor: Optional[VendorRef] = None
    vendor_id: Optional[int] = None
    auth_parameters: Optional[List[AuthTemplateParameter]] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
