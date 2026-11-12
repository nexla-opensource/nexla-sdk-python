from typing import Any, Dict, Literal, Optional

from pydantic import Field

from nexla_sdk.models.base import BaseModel


class OauthStartRequest(BaseModel):
    """Request model for POST /oauth/start.

    Set either vendor_id or vendor_name, and either auth_template_id or
    auth_template_name. client_origin is optional; the browser normally sends the
    Origin header, which the backend uses when the field is not set.
    """

    vendor_id: Optional[int] = None
    vendor_name: Optional[str] = None
    auth_template_id: Optional[int] = None
    auth_template_name: Optional[str] = None
    credentials_type: Optional[Literal["rest"]] = None
    auto_create_credential: bool = False
    credential_name: Optional[str] = None
    client_origin: Optional[str] = None
    form_values: Dict[str, Any] = Field(default_factory=dict)
