"""Unit tests for NotificationSettingsResource using mocks."""

import pytest

from nexla_sdk.models.notification_settings import (
    NotificationSetting,
    NotificationSettingBrief,
    NotificationSettingCreate,
    NotificationSettingUpdate,
)
from nexla_sdk.resources.notification_settings import NotificationSettingsResource


@pytest.fixture
def notification_settings_resource(mock_client):
    """Create a NotificationSettingsResource instance with mocked client."""
    return NotificationSettingsResource(mock_client)


@pytest.fixture
def sample_notification_setting():
    """Sample notification setting response data."""
    return {
        "id": 1,
        "notification_type_id": 5,
        "resource_id": 123,
        "resource_type": "data_sources",
        "channel": "email",
        "priority": 5,
        "status": "ENABLED",
        "payload": {"recipients": ["user@example.com"]},
        "owner_id": 10,
        "org_id": 1,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
    }


@pytest.fixture
def sample_notification_settings_list():
    """Sample list of notification settings."""
    return [
        {
            "id": 1,
            "notification_type_id": 5,
            "resource_id": 123,
            "resource_type": "data_sources",
            "channel": "email",
            "priority": 5,
            "status": "ENABLED",
            "payload": None,
            "owner_id": 10,
            "org_id": 1,
        },
        {
            "id": 2,
            "notification_type_id": 6,
            "resource_id": None,
            "resource_type": None,
            "channel": "slack",
            "priority": 3,
            "status": "ENABLED",
            "payload": {"webhook_url": "https://hooks.slack.com/xxx"},
            "owner_id": 10,
            "org_id": 1,
        },
    ]


class TestNotificationSettingsResource:
    """Unit tests for NotificationSettingsResource."""

    def test_list_notification_settings_success(
        self,
        mock_client,
        mock_http_client,
        notification_settings_resource,
        sample_notification_settings_list,
    ):
        """Test listing notification settings with successful response."""
        mock_http_client.add_response(
            "/notification_settings", sample_notification_settings_list
        )

        settings = notification_settings_resource.list()
        assert len(settings) == 2
        mock_http_client.assert_request_made("GET", "/notification_settings")

    def test_list_notification_settings_with_filters(
        self, mock_client, mock_http_client, notification_settings_resource
    ):
        """Test listing notification settings with filters."""
        response = [
            {
                "id": 1,
                "notification_type_id": 5,
                "channel": "email",
                "priority": 5,
                "status": "ENABLED",
            }
        ]
        mock_http_client.add_response("/notification_settings", response)

        settings = notification_settings_resource.list(
            notification_resource_type="data_sources",
            resource_id=123,
            sort_by="priority",
            sort_order="ASC",
        )
        assert len(settings) == 1
        params = mock_http_client.get_request()["params"]
        assert params["notification_resource_type"] == "data_sources"
        assert params["resource_id"] == 123

    def test_list_all_notification_settings(
        self,
        mock_client,
        mock_http_client,
        notification_settings_resource,
        sample_notification_settings_list,
    ):
        """Test listing all notification settings (super user)."""
        mock_http_client.add_response(
            "/notification_settings/all", sample_notification_settings_list
        )

        settings = notification_settings_resource.list_all(
            resource_type="data_sources",
            event_type="flow_failed",
            status="ENABLED",
        )
        assert len(settings) == 2
        mock_http_client.assert_request_made("GET", "/notification_settings/all")

    def test_get_notification_setting_success(
        self,
        mock_client,
        mock_http_client,
        notification_settings_resource,
        sample_notification_setting,
    ):
        """Test getting a notification setting by ID."""
        mock_http_client.add_response(
            "/notification_settings/1", sample_notification_setting
        )

        setting = notification_settings_resource.get(1)
        assert setting.id == 1
        assert setting.channel == "email"
        assert setting.priority == 5
        mock_http_client.assert_request_made("GET", "/notification_settings/1")

    def test_create_notification_setting_success(
        self,
        mock_client,
        mock_http_client,
        notification_settings_resource,
        sample_notification_setting,
    ):
        """Test creating a notification setting."""
        mock_http_client.add_response(
            "/notification_settings", sample_notification_setting
        )

        setting = notification_settings_resource.create(
            NotificationSettingCreate(
                notification_type_id=5,
                channel="email",
                priority=5,
            )
        )
        assert setting.id == 1
        assert setting.channel == "email"
        mock_http_client.assert_request_made("POST", "/notification_settings")

    def test_create_notification_setting_with_dict(
        self,
        mock_client,
        mock_http_client,
        notification_settings_resource,
        sample_notification_setting,
    ):
        """Test creating a notification setting with dict input."""
        mock_http_client.add_response(
            "/notification_settings", sample_notification_setting
        )

        setting = notification_settings_resource.create(
            {"notification_type_id": 5, "channel": "email", "priority": 5}
        )
        assert setting.id == 1
        mock_http_client.assert_request_made("POST", "/notification_settings")

    def test_update_notification_setting_success(
        self,
        mock_client,
        mock_http_client,
        notification_settings_resource,
        sample_notification_setting,
    ):
        """Test updating a notification setting."""
        updated_setting = sample_notification_setting.copy()
        updated_setting["priority"] = 10
        mock_http_client.add_response("/notification_settings/1", updated_setting)

        setting = notification_settings_resource.update(
            1, NotificationSettingUpdate(priority=10)
        )
        assert setting.priority == 10
        mock_http_client.assert_request_made("PUT", "/notification_settings/1")

    def test_delete_notification_setting_success(
        self, mock_client, mock_http_client, notification_settings_resource
    ):
        """Test deleting a notification setting."""
        mock_http_client.add_response("/notification_settings/1", {})

        result = notification_settings_resource.delete(1)
        assert result == {}
        mock_http_client.assert_request_made("DELETE", "/notification_settings/1")

    def test_show_resource_settings(
        self,
        mock_client,
        mock_http_client,
        notification_settings_resource,
        sample_notification_settings_list,
    ):
        """Test getting notification settings for a resource."""
        mock_http_client.add_response(
            "/notification_settings/data_sources/123", sample_notification_settings_list
        )

        settings = notification_settings_resource.show_resource_settings(
            resource_type="data_sources",
            resource_id=123,
            filter_overridden_settings=True,
        )
        assert len(settings) == 2
        params = mock_http_client.get_request()["params"]
        assert params["filter_overridden_settings"] == "true"

    def test_show_type_settings(
        self,
        mock_client,
        mock_http_client,
        notification_settings_resource,
        sample_notification_settings_list,
    ):
        """Test getting notification settings for a notification type."""
        mock_http_client.add_response(
            "/notification_settings/notification_types/5",
            sample_notification_settings_list,
        )

        settings = notification_settings_resource.show_type_settings(
            notification_type_id=5
        )
        assert len(settings) == 2
        mock_http_client.assert_request_made(
            "GET", "/notification_settings/notification_types/5"
        )

    def test_org_index(
        self,
        mock_client,
        mock_http_client,
        notification_settings_resource,
        sample_notification_settings_list,
    ):
        """Test listing organization notification settings."""
        mock_http_client.add_response(
            "/orgs/1/notification_settings", sample_notification_settings_list
        )

        settings = notification_settings_resource.org_index(org_id=1)
        assert len(settings) == 2
        mock_http_client.assert_request_made("GET", "/orgs/1/notification_settings")

    def test_org_create(
        self,
        mock_client,
        mock_http_client,
        notification_settings_resource,
        sample_notification_setting,
    ):
        """Test creating an organization notification setting."""
        mock_http_client.add_response(
            "/orgs/1/notification_settings", sample_notification_setting
        )

        setting = notification_settings_resource.org_create(
            org_id=1,
            data=NotificationSettingCreate(
                notification_type_id=5, channel="email", priority=5
            ),
        )
        assert setting.id == 1
        mock_http_client.assert_request_made("POST", "/orgs/1/notification_settings")

    def test_org_update(
        self,
        mock_client,
        mock_http_client,
        notification_settings_resource,
        sample_notification_setting,
    ):
        """Test updating an organization notification setting."""
        updated_setting = sample_notification_setting.copy()
        updated_setting["priority"] = 8
        mock_http_client.add_response(
            "/orgs/1/notification_settings/1", updated_setting
        )

        setting = notification_settings_resource.org_update(
            org_id=1,
            notification_settings_id=1,
            data=NotificationSettingUpdate(priority=8),
        )
        assert setting.priority == 8
        mock_http_client.assert_request_made("PUT", "/orgs/1/notification_settings/1")

    def test_org_delete(
        self, mock_client, mock_http_client, notification_settings_resource
    ):
        """Test deleting an organization notification setting."""
        mock_http_client.add_response("/orgs/1/notification_settings/1", {})

        result = notification_settings_resource.org_delete(
            org_id=1, notification_settings_id=1
        )
        assert result == {}
        mock_http_client.assert_request_made(
            "DELETE", "/orgs/1/notification_settings/1"
        )


class TestNotificationSettingModels:
    """Unit tests for Notification Setting model validation."""

    def test_notification_setting_model_validation(
        self, notification_settings_resource, sample_notification_setting
    ):
        """Test NotificationSetting model validation."""
        setting = NotificationSetting.model_validate(sample_notification_setting)
        assert setting.id == 1
        assert setting.channel == "email"
        assert setting.priority == 5
        assert setting.status == "ENABLED"

    def test_notification_setting_brief_model(self):
        """Test NotificationSettingBrief model validation."""
        brief_data = {
            "id": 1,
            "notification_type_id": 5,
            "channel": "email",
            "priority": 5,
            "status": "ENABLED",
            "resource_type": "data_sources",
            "resource_id": 123,
        }
        brief = NotificationSettingBrief.model_validate(brief_data)
        assert brief.id == 1
        assert brief.channel == "email"

    def test_notification_setting_create_model(self):
        """Test NotificationSettingCreate model validation."""
        create_data = {
            "notification_type_id": 5,
            "channel": "email",
            "priority": 5,
            "status": "ENABLED",
        }
        create = NotificationSettingCreate.model_validate(create_data)
        assert create.notification_type_id == 5
        assert create.channel == "email"
        assert create.priority == 5
        assert create.status == "ENABLED"

    def test_notification_setting_create_with_payload(self):
        """Test NotificationSettingCreate with payload."""
        create_data = {
            "notification_type_id": 5,
            "channel": "email",
            "payload": {"recipients": ["user@example.com"]},
        }
        create = NotificationSettingCreate.model_validate(create_data)
        assert create.payload == {"recipients": ["user@example.com"]}

    def test_notification_setting_update_model(self):
        """Test NotificationSettingUpdate model validation."""
        update_data = {"priority": 10, "status": "DISABLED"}
        update = NotificationSettingUpdate.model_validate(update_data)
        assert update.priority == 10
        assert update.status == "DISABLED"

    def test_notification_setting_update_partial(self):
        """Test NotificationSettingUpdate with partial data."""
        update_data = {"priority": 8}
        update = NotificationSettingUpdate.model_validate(update_data)
        assert update.priority == 8
        assert update.channel is None
        assert update.status is None
