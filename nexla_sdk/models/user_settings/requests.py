from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel


class UserSettingCreate(BaseModel):
    user_settings_type: str
    primary_key_value: str
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    copied_from_id: Optional[int] = None


class UserSettingUpdate(BaseModel):
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
