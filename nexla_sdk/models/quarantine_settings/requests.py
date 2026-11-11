from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel


class QuarantineSettingCreate(BaseModel):
    data_credentials_id: int
    config: Dict[str, Any]
    owner_id: Optional[int] = None
    org_id: Optional[int] = None


class QuarantineSettingUpdate(BaseModel):
    data_credentials_id: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    owner_id: Optional[int] = None
    org_id: Optional[int] = None
