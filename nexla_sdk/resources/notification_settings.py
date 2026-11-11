"""Resource for managing notification settings."""

from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.notification_settings.requests import (
    NotificationSettingCreate,
    NotificationSettingUpdate,
)
from nexla_sdk.models.notification_settings.responses import NotificationSetting
from nexla_sdk.resources.base_resource import BaseResource


class NotificationSettingsResource(BaseResource):
    """Resource for managing notification settings.

    Notification settings control how and when users receive notifications
    for different events and resources.

    Examples:
        # List notification settings
        settings = client.notification_settings.list()

        # Get a specific setting
        setting = client.notification_settings.get(123)

        # Create a new notification setting
        setting = client.notification_settings.create(NotificationSettingCreate(
            notification_type_id=1,
            channel="email",
            priority=5
        ))

        # Update a setting
        setting = client.notification_settings.update(123, NotificationSettingUpdate(
            priority=10
        ))
    """

    def __init__(self, client):
        """Initialize the notification settings resource.

        Args:
            client: Nexla client instance
        """
        super().__init__(client)
        self._path = "/notification_settings"
        self._model_class = NotificationSetting

    def list(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        notification_resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        **kwargs,
    ) -> List[NotificationSetting]:
        """List notification settings for the current user.

        Args:
            page: Page number (1-based)
            per_page: Items per page
            notification_resource_type: Filter by resource type
            resource_id: Filter by resource ID
            sort_by: Sort field (default: priority)
            sort_order: Sort order (ASC or DESC)
            **kwargs: Additional query parameters

        Returns:
            List of notification settings
        """
        params = kwargs.copy()
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if notification_resource_type is not None:
            params["notification_resource_type"] = notification_resource_type
        if resource_id is not None:
            params["resource_id"] = resource_id
        if sort_by is not None:
            params["sort_by"] = sort_by
        if sort_order is not None:
            params["sort_order"] = sort_order

        response = self._make_request("GET", self._path, params=params)
        return self._parse_response(response)

    def list_all(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        resource_type: Optional[str] = None,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[NotificationSetting]:
        """List all notification settings (super user only).

        Args:
            page: Page number (1-based)
            per_page: Items per page
            resource_type: Filter by resource type
            event_type: Filter by event type
            status: Filter by status

        Returns:
            List of all notification settings
        """
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if resource_type is not None:
            params["resource_type"] = resource_type
        if event_type is not None:
            params["event_type"] = event_type
        if status is not None:
            params["status"] = status

        response = self._make_request("GET", f"{self._path}/all", params=params)
        return self._parse_response(response)

    def get(self, setting_id: int, expand: bool = False) -> NotificationSetting:
        """Get notification setting by ID.

        Args:
            setting_id: Notification setting ID
            expand: Include expanded details

        Returns:
            Notification setting instance
        """
        return super().get(setting_id, expand=expand)

    def create(
        self, data: Union[NotificationSettingCreate, Dict[str, Any]]
    ) -> NotificationSetting:
        """Create a new notification setting.

        Args:
            data: Notification setting creation data

        Returns:
            Created notification setting
        """
        return super().create(data)

    def update(
        self,
        setting_id: int,
        data: Union[NotificationSettingUpdate, Dict[str, Any]],
    ) -> NotificationSetting:
        """Update a notification setting.

        Args:
            setting_id: Notification setting ID
            data: Updated notification setting data

        Returns:
            Updated notification setting
        """
        return super().update(setting_id, data)

    def delete(self, setting_id: int) -> Dict[str, Any]:
        """Delete a notification setting.

        Args:
            setting_id: Notification setting ID

        Returns:
            Response with status
        """
        return super().delete(setting_id)

    def show_resource_settings(
        self,
        resource_type: str,
        resource_id: int,
        notification_type_id: Optional[int] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        filter_overridden_settings: bool = False,
    ) -> List[NotificationSetting]:
        """Get notification settings for a specific resource.

        Args:
            resource_type: Resource type (data_sources, data_sets, data_sinks)
            resource_id: Resource ID
            notification_type_id: Optional notification type ID to filter
            page: Page number (1-based)
            per_page: Items per page
            filter_overridden_settings: Filter overridden settings

        Returns:
            List of notification settings for the resource
        """
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if notification_type_id is not None:
            params["notification_type_id"] = notification_type_id
        if filter_overridden_settings:
            params["filter_overridden_settings"] = "true"

        path = f"/notification_settings/{resource_type}/{resource_id}"
        response = self._make_request("GET", path, params=params)
        return self._parse_response(response)

    def show_type_settings(
        self,
        notification_type_id: int,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> List[NotificationSetting]:
        """Get notification settings for a specific notification type.

        Args:
            notification_type_id: Notification type ID
            page: Page number (1-based)
            per_page: Items per page
            sort_by: Sort field (default: priority)
            sort_order: Sort order (ASC or DESC)

        Returns:
            List of notification settings for the type
        """
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if sort_by is not None:
            params["sort_by"] = sort_by
        if sort_order is not None:
            params["sort_order"] = sort_order

        path = f"/notification_settings/notification_types/{notification_type_id}"
        response = self._make_request("GET", path, params=params)
        return self._parse_response(response)

    def list_by(
        self, payload: Dict[str, Any], method: str = "POST"
    ) -> List[NotificationSetting]:
        path = "/notification_setting/list"
        response = self._make_request(method.upper(), path, json=payload)
        return self._parse_response(response)

    def org_index(
        self,
        org_id: int,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> List[NotificationSetting]:
        """List notification settings for an organization.

        Args:
            org_id: Organization ID
            page: Page number (1-based)
            per_page: Items per page
            sort_by: Sort field (default: priority)
            sort_order: Sort order (ASC or DESC)

        Returns:
            List of organization notification settings
        """
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if sort_by is not None:
            params["sort_by"] = sort_by
        if sort_order is not None:
            params["sort_order"] = sort_order

        path = f"/orgs/{org_id}/notification_settings"
        response = self._make_request("GET", path, params=params)
        return self._parse_response(response)

    def org_create(
        self, org_id: int, data: Union[NotificationSettingCreate, Dict[str, Any]]
    ) -> NotificationSetting:
        """Create a notification setting for an organization.

        Args:
            org_id: Organization ID
            data: Notification setting creation data

        Returns:
            Created notification setting
        """
        serialized_data = self._serialize_data(data)
        path = f"/orgs/{org_id}/notification_settings"
        response = self._make_request("POST", path, json=serialized_data)
        return self._parse_response(response)

    def org_update(
        self,
        org_id: int,
        notification_settings_id: int,
        data: Union[NotificationSettingUpdate, Dict[str, Any]],
    ) -> NotificationSetting:
        """Update an organization notification setting.

        Args:
            org_id: Organization ID
            notification_settings_id: Notification setting ID
            data: Updated notification setting data

        Returns:
            Updated notification setting
        """
        serialized_data = self._serialize_data(data)
        path = f"/orgs/{org_id}/notification_settings/{notification_settings_id}"
        response = self._make_request("PUT", path, json=serialized_data)
        return self._parse_response(response)

    def org_delete(self, org_id: int, notification_settings_id: int) -> Dict[str, Any]:
        """Delete an organization notification setting.

        Args:
            org_id: Organization ID
            notification_settings_id: Notification setting ID

        Returns:
            Response with status
        """
        path = f"/orgs/{org_id}/notification_settings/{notification_settings_id}"
        return self._make_request("DELETE", path)
