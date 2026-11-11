from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.notifications.requests import (
    NotificationChannelSettingCreate,
    NotificationChannelSettingUpdate,
    NotificationSettingCreate,
    NotificationSettingUpdate,
)
from nexla_sdk.models.notifications.responses import (
    Notification,
    NotificationChannelSetting,
    NotificationCount,
    NotificationSetting,
    NotificationType,
)
from nexla_sdk.resources.base_resource import BaseResource


class NotificationsResource(BaseResource):
    """Resource for managing notifications."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/notifications"
        self._model_class = Notification

    def get(self, notification_id: int, expand: bool = False) -> Notification:
        """
        Get single notification by ID.

        Args:
            notification_id: Notification ID
            expand: Include expanded references

        Returns:
            Notification instance
        """
        return super().get(notification_id, expand)

    def delete(self, notification_id: int) -> Dict[str, Any]:
        """
        Delete notification.

        Args:
            notification_id: Notification ID

        Returns:
            Response with status
        """
        return super().delete(notification_id)

    def list(
        self,
        read: Optional[int] = None,
        level: Optional[str] = None,
        resource_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
        **kwargs,
    ) -> List[Notification]:
        """
        List notifications with optional filters.

        Args:
            read: Filter by read status (0=unread, 1=read)
            level: Filter by level (DEBUG, INFO, WARN, ERROR, RECOVERED, RESOLVED)
            from_timestamp: Start timestamp (unix)
            to_timestamp: End timestamp (unix)
            page: Page number (via kwargs)
            per_page: Items per page (via kwargs)
            **kwargs: Additional parameters

        Returns:
            List of notifications

        Examples:
            client.notifications.list(read=0, level="ERROR", page=1, per_page=50)
        """
        params = kwargs.copy()
        if read is not None:
            params["read"] = read
        if level:
            params["level"] = level
        if resource_id is not None:
            params["resource_id"] = resource_id
        if resource_type is not None:
            params["resource_type"] = resource_type
        if from_timestamp:
            params["from"] = from_timestamp
        if to_timestamp:
            params["to"] = to_timestamp

        return super().list(**params)

    def delete_all(
        self, payload: Optional[Dict[str, Any]] = None, async_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Delete all notifications.

        Returns:
            Response status
        """
        path = f"{self._path}/all"
        params = {"async": 1} if async_mode else None
        return self._make_request(
            "DELETE", path, json=payload or {}, params=params or {}
        )

    def get_count(self, read: Optional[int] = None) -> NotificationCount:
        """
        Get notification count.

        Args:
            read: Filter by read status

        Returns:
            Notification count
        """
        path = f"{self._path}/count"
        params = {"read": read} if read is not None else {}
        response = self._make_request("GET", path, params=params)
        return NotificationCount(**response)

    def mark_read(self, notification_ids: Union[List[int], str]) -> Dict[str, Any]:
        """
        Mark notifications as read.

        Args:
            notification_ids: List of IDs or 'all'

        Returns:
            Response status
        """
        path = f"{self._path}/mark_read"

        if notification_ids == "all":
            params = {"notification_id": "all"}
            return self._make_request("PUT", path, params=params)
        else:
            return self._make_request("PUT", path, json=notification_ids)

    def mark_unread(self, notification_ids: Union[List[int], str]) -> Dict[str, Any]:
        """
        Mark notifications as unread.

        Args:
            notification_ids: List of IDs or 'all'

        Returns:
            Response status
        """
        path = f"{self._path}/mark_unread"

        if notification_ids == "all":
            params = {"notification_id": "all"}
            return self._make_request("PUT", path, params=params)
        else:
            return self._make_request("PUT", path, json=notification_ids)

    def mark_read_for(
        self, notification_id: Union[int, str], payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        path = f"{self._path}/{notification_id}/mark_read"
        return self._make_request("PUT", path, json=payload or {})

    def mark_unread_for(
        self, notification_id: Union[int, str], payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        path = f"{self._path}/{notification_id}/mark_unread"
        return self._make_request("PUT", path, json=payload or {})

    def publish_raw(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", f"{self._path}/raw", json=payload)

    # Notification Types
    def get_types(self, status: Optional[str] = None) -> List[NotificationType]:
        """
        Get all notification types.

        Args:
            status: Filter by status (ACTIVE, PAUSE)

        Returns:
            List of notification types
        """
        path = "/notification_types"
        params = {"status": status} if status else {}
        response = self._make_request("GET", path, params=params)
        return [NotificationType(**item) for item in response]

    def get_type(self, event_type: str, resource_type: str) -> NotificationType:
        """
        Get specific notification type.

        Args:
            event_type: Event type
            resource_type: Resource type

        Returns:
            Notification type
        """
        path = "/notification_types/list"
        params = {"event_type": event_type, "resource_type": resource_type}
        response = self._make_request("GET", path, params=params)
        return NotificationType(**response)

    # Channel Settings
    def list_channel_settings(self) -> List[NotificationChannelSetting]:
        """
        List notification channel settings.

        Returns:
            List of channel settings
        """
        path = "/notification_channel_settings"
        response = self._make_request("GET", path)
        return [NotificationChannelSetting(**item) for item in response]

    def create_channel_setting(
        self, data: NotificationChannelSettingCreate
    ) -> NotificationChannelSetting:
        """
        Create notification channel setting.

        Args:
            data: Channel setting creation data

        Returns:
            Created channel setting
        """
        path = "/notification_channel_settings"
        response = self._make_request("POST", path, json=data.to_dict())
        return NotificationChannelSetting(**response)

    def get_channel_setting(self, setting_id: int) -> NotificationChannelSetting:
        """
        Get notification channel setting.

        Args:
            setting_id: Channel setting ID

        Returns:
            Channel setting
        """
        path = f"/notification_channel_settings/{setting_id}"
        response = self._make_request("GET", path)
        return NotificationChannelSetting(**response)

    def update_channel_setting(
        self, setting_id: int, data: NotificationChannelSettingUpdate
    ) -> NotificationChannelSetting:
        """
        Update notification channel setting.

        Args:
            setting_id: Channel setting ID
            data: Updated channel setting data

        Returns:
            Updated channel setting
        """
        path = f"/notification_channel_settings/{setting_id}"
        response = self._make_request("PUT", path, json=data.to_dict())
        return NotificationChannelSetting(**response)

    def delete_channel_setting(self, setting_id: int) -> Dict[str, Any]:
        """
        Delete notification channel setting.

        Args:
            setting_id: Channel setting ID

        Returns:
            Response status
        """
        path = f"/notification_channel_settings/{setting_id}"
        return self._make_request("DELETE", path)

    # Notification Settings
    def list_settings(
        self,
        event_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[NotificationSetting]:
        """
        List notification settings.

        Args:
            event_type: Filter by event type
            resource_type: Filter by resource type
            status: Filter by status

        Returns:
            List of notification settings
        """
        path = "/notification_settings"
        params = {}
        if event_type:
            params["event_type"] = event_type
        if resource_type:
            params["resource_type"] = resource_type
        if status:
            params["status"] = status

        response = self._make_request("GET", path, params=params)
        return [NotificationSetting(**item) for item in response]

    def create_setting(self, data: NotificationSettingCreate) -> NotificationSetting:
        """
        Create notification setting.

        Args:
            data: Notification setting creation data

        Returns:
            Created setting
        """
        path = "/notification_settings"
        response = self._make_request("POST", path, json=data.to_dict())
        return NotificationSetting(**response)

    def get_setting(self, setting_id: int) -> NotificationSetting:
        """
        Get notification setting.

        Args:
            setting_id: Setting ID

        Returns:
            Notification setting
        """
        path = f"/notification_settings/{setting_id}"
        response = self._make_request("GET", path)
        return NotificationSetting(**response)

    def update_setting(
        self, setting_id: int, data: NotificationSettingUpdate
    ) -> NotificationSetting:
        """
        Update notification setting.

        Args:
            setting_id: Setting ID
            data: Updated notification setting data

        Returns:
            Updated setting
        """
        path = f"/notification_settings/{setting_id}"
        response = self._make_request("PUT", path, json=data.to_dict())
        return NotificationSetting(**response)

    def delete_setting(self, setting_id: int) -> Dict[str, Any]:
        """
        Delete notification setting.

        Args:
            setting_id: Setting ID

        Returns:
            Response status
        """
        path = f"/notification_settings/{setting_id}"
        return self._make_request("DELETE", path)

    def get_settings_by_type(
        self, notification_type_id: int, expand: bool = False
    ) -> List[NotificationSetting]:
        """
        Get notification settings for a type.

        Args:
            notification_type_id: Notification type ID
            expand: Include expanded information

        Returns:
            List of settings
        """
        path = f"/notification_settings/notification_types/{notification_type_id}"
        params = {"expand": expand} if expand else {}
        response = self._make_request("GET", path, params=params)
        return [NotificationSetting(**item) for item in response]

    def get_resource_settings(
        self,
        resource_type: str,
        resource_id: int,
        expand: bool = False,
        filter_overridden: bool = False,
        notification_type_id: Optional[int] = None,
    ) -> List[NotificationSetting]:
        """
        Get notification settings for a resource.

        Args:
            resource_type: Resource type
            resource_id: Resource ID
            expand: Include expanded information
            filter_overridden: Filter overridden settings
            notification_type_id: Filter by type ID

        Returns:
            List of settings
        """
        path = f"/notification_settings/{resource_type}/{resource_id}"
        params = {}
        if expand:
            params["expand"] = expand
        if filter_overridden:
            params["filter_overridden_settings"] = filter_overridden
        if notification_type_id:
            params["notification_type_id"] = notification_type_id

        response = self._make_request("GET", path, params=params)
        return [NotificationSetting(**item) for item in response]
