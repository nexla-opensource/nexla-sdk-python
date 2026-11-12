from typing import TYPE_CHECKING, Any, Dict, List, Union, cast

from nexla_sdk.models.user_settings.requests import UserSettingCreate, UserSettingUpdate
from nexla_sdk.models.user_settings.responses import UserSetting
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class UserSettingsResource(BaseResource[UserSetting]):
    """Resource for managing user settings."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/user_settings"
        self._model_class = UserSetting

    def list(self, **kwargs: Any) -> List[UserSetting]:  # type: ignore[override]  # keeps public list() signature; base list() also takes positional filters
        return super().list(**kwargs)

    def search(self, filters: Dict[str, Any], **params: Any) -> List[UserSetting]:
        path = f"{self._path}/search"
        response = self._make_request("POST", path, json=filters, params=params)
        return cast(List[UserSetting], self._parse_response(response))

    def get(self, user_setting_id: int) -> UserSetting:  # type: ignore[override]  # keeps public get() signature; base get() also takes expand
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
