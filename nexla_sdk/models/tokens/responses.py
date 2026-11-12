from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel


class TokenResponse(BaseModel):
    """Response of POST /token and POST /token/refresh (token/schema.py:233-275).

    Unknown fields are kept (``model_extra``).
    """

    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 86400
    sdk_application_id: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    org: Optional[Dict[str, Any]] = None
    org_membership: Optional[Dict[str, Any]] = None
