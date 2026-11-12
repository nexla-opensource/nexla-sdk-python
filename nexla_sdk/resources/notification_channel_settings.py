from typing import TYPE_CHECKING, Any, Dict, List, Union

from nexla_sdk.models.notification_channel_settings.requests import (
    NotificationChannelSettingCreate,
    NotificationChannelSettingUpdate,
)
from nexla_sdk.models.notification_channel_settings.responses import (
    NotificationChannelSetting,
)
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class NotificationChannelSettingsResource(BaseResource[NotificationChannelSetting]):
    """Resource for managing notification channel settings."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/notification_channel_settings"
        self._model_class = NotificationChannelSetting

    def list(self, **kwargs: Any) -> List[NotificationChannelSetting]:  # type: ignore[override]  # keeps public list() signature; base list() also takes positional filters
        return super().list(**kwargs)

    def get(self, setting_id: int) -> NotificationChannelSetting:  # type: ignore[override]  # keeps public get() signature; base get() also takes expand
        return super().get(setting_id)

    def create(
        self, data: Union[NotificationChannelSettingCreate, Dict[str, Any]]
    ) -> NotificationChannelSetting:
        return super().create(data)

    def update(
        self,
        setting_id: int,
        data: Union[NotificationChannelSettingUpdate, Dict[str, Any]],
    ) -> NotificationChannelSetting:
        return super().update(setting_id, data)

    def delete(self, setting_id: int) -> Dict[str, Any]:
        return super().delete(setting_id)
