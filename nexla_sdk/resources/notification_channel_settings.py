from typing import Any, Dict, List, Union

from nexla_sdk.models.notification_channel_settings.requests import (
    NotificationChannelSettingCreate,
    NotificationChannelSettingUpdate,
)
from nexla_sdk.models.notification_channel_settings.responses import (
    NotificationChannelSetting,
)
from nexla_sdk.resources.base_resource import BaseResource


class NotificationChannelSettingsResource(BaseResource):
    """Resource for managing notification channel settings."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/notification_channel_settings"
        self._model_class = NotificationChannelSetting

    def list(self, **kwargs) -> List[NotificationChannelSetting]:
        return super().list(**kwargs)

    def get(self, setting_id: int) -> NotificationChannelSetting:
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
