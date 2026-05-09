from typing import Any, Dict, List, Union

from nexla_sdk.models.user_settings.requests import UserSettingCreate, UserSettingUpdate
from nexla_sdk.models.user_settings.responses import UserSetting
from nexla_sdk.resources.base_resource import BaseResource


class UserSettingsResource(BaseResource):
    """Resource for managing user settings."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/user_settings"
        self._model_class = UserSetting

    def list(self, **kwargs) -> List[UserSetting]:
        return super().list(**kwargs)

    def search(self, filters: Dict[str, Any], **params) -> List[UserSetting]:
        path = f"{self._path}/search"
        response = self._make_request("POST", path, json=filters, params=params)
        return self._parse_response(response)

    def get(self, user_setting_id: int) -> UserSetting:
        return super().get(user_setting_id)

    def create(self, data: Union[UserSettingCreate, Dict[str, Any]]) -> UserSetting:
        return super().create(data)

    def update(
        self,
        user_setting_id: int,
        data: Union[UserSettingUpdate, Dict[str, Any]],
    ) -> UserSetting:
        return super().update(user_setting_id, data)

    def delete(self, user_setting_id: int) -> Dict[str, Any]:
        return super().delete(user_setting_id)
