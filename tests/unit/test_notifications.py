import pytest

from nexla_sdk import NexlaClient
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

pytestmark = pytest.mark.unit


@pytest.fixture
def client(mock_client: NexlaClient) -> NexlaClient:
    return mock_client


class TestNotificationsResource:
    def test_notifications_listing_and_bulk_ops(self, client, mock_http_client):
        mock_http_client.add_response(
            "/notifications",
            [
                {
                    "id": 1,
                    "owner": {"id": 1, "full_name": "A", "email": "a@b.com"},
                    "org": {"id": 1, "name": "Org"},
                    "access_roles": ["owner"],
                    "level": "ERROR",
                    "resource_id": 7,
                    "resource_type": "SOURCE",
                    "message_id": 2,
                    "message": "...",
                }
            ],
        )
        out = client.notifications.list(
            read=0, level="ERROR", from_timestamp=1, to_timestamp=2, page=1, per_page=10
        )
        assert isinstance(out[0], Notification)

        mock_http_client.clear_responses()
        mock_http_client.add_response("/notifications/all", {"status": "deleted"})
        d = client.notifications.delete_all()
        assert d.get("status") == "deleted"

        mock_http_client.clear_responses()
        mock_http_client.add_response("/notifications/count", {"count": 3})
        cnt = client.notifications.get_count(read=0)
        assert isinstance(cnt, NotificationCount) and cnt.count == 3

        mock_http_client.clear_responses()
        mock_http_client.add_response("/notifications/mark_read", {"status": "ok"})
        r = client.notifications.mark_read([1, 2])
        assert r.get("status") == "ok"

        mock_http_client.clear_responses()
        mock_http_client.add_response("/notifications/mark_read", {"status": "ok"})
        r_all = client.notifications.mark_read("all")
        assert r_all.get("status") == "ok"

        mock_http_client.clear_responses()
        mock_http_client.add_response("/notifications/mark_unread", {"status": "ok"})
        ur = client.notifications.mark_unread([1])
        assert ur.get("status") == "ok"

    def test_notification_types_and_settings(self, client, mock_http_client):
        mock_http_client.add_response(
            "/notification_types",
            [
                {
                    "id": 1,
                    "name": "Flow",
                    "description": "",
                    "category": "SYSTEM",
                    "default": True,
                    "status": True,
                    "event_type": "X",
                    "resource_type": "SOURCE",
                }
            ],
        )
        types = client.notifications.get_types(status="ACTIVE")
        assert isinstance(types[0], NotificationType)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/notification_types/list",
            {
                "id": 2,
                "name": "Flow",
                "description": "",
                "category": "SYSTEM",
                "default": True,
                "status": True,
                "event_type": "X",
                "resource_type": "SOURCE",
            },
        )
        t = client.notifications.get_type(event_type="X", resource_type="SOURCE")
        assert isinstance(t, NotificationType)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/notification_channel_settings",
            [{"id": 1, "owner_id": 1, "org_id": 1, "channel": "APP", "config": {}}],
        )
        ch = client.notifications.list_channel_settings()
        assert isinstance(ch[0], NotificationChannelSetting)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/notification_channel_settings",
            {"id": 2, "owner_id": 1, "org_id": 1, "channel": "EMAIL", "config": {}},
        )
        ch_created = client.notifications.create_channel_setting(
            NotificationChannelSettingCreate(channel="EMAIL", config={})
        )
        assert isinstance(ch_created, NotificationChannelSetting)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/notification_channel_settings/2",
            {"id": 2, "owner_id": 1, "org_id": 1, "channel": "EMAIL", "config": {}},
        )
        ch_get = client.notifications.get_channel_setting(2)
        assert isinstance(ch_get, NotificationChannelSetting)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/notification_channel_settings/2",
            {
                "id": 2,
                "owner_id": 1,
                "org_id": 1,
                "channel": "EMAIL",
                "config": {"on": True},
            },
        )
        ch_upd = client.notifications.update_channel_setting(
            2, NotificationChannelSettingUpdate(config={"on": True})
        )
        assert isinstance(ch_upd, NotificationChannelSetting)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/notification_channel_settings/2", {"status": "deleted"}
        )
        ch_del = client.notifications.delete_channel_setting(2)
        assert ch_del.get("status") == "deleted"

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/notification_settings",
            [
                {
                    "id": 1,
                    "org_id": 1,
                    "owner_id": 1,
                    "channel": "APP",
                    "notification_resource_type": "SOURCE",
                    "resource_id": 1,
                    "status": "ACTIVE",
                    "notification_type_id": 1,
                    "name": "n",
                    "description": "d",
                    "code": 0,
                    "category": "SYSTEM",
                    "event_type": "X",
                    "resource_type": "SOURCE",
                    "config": {},
                }
            ],
        )
        lst = client.notifications.list_settings(
            event_type="X", resource_type="SOURCE", status="ACTIVE"
        )
        assert isinstance(lst[0], NotificationSetting)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/notification_settings",
            {
                "id": 2,
                "org_id": 1,
                "owner_id": 1,
                "channel": "APP",
                "notification_resource_type": "SOURCE",
                "resource_id": 1,
                "status": "ACTIVE",
                "notification_type_id": 1,
                "name": "n",
                "description": "d",
                "code": 0,
                "category": "SYSTEM",
                "event_type": "X",
                "resource_type": "SOURCE",
                "config": {},
            },
        )
        st_created = client.notifications.create_setting(
            NotificationSettingCreate(channel="APP", notification_type_id=1, config={})
        )
        assert isinstance(st_created, NotificationSetting)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/notification_settings/2",
            {
                "id": 2,
                "org_id": 1,
                "owner_id": 1,
                "channel": "APP",
                "notification_resource_type": "SOURCE",
                "resource_id": 1,
                "status": "ACTIVE",
                "notification_type_id": 1,
                "name": "n",
                "description": "d",
                "code": 0,
                "category": "SYSTEM",
                "event_type": "X",
                "resource_type": "SOURCE",
                "config": {},
            },
        )
        st_get = client.notifications.get_setting(2)
        assert isinstance(st_get, NotificationSetting)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/notification_settings/2",
            {
                "id": 2,
                "org_id": 1,
                "owner_id": 1,
                "channel": "APP",
                "notification_resource_type": "SOURCE",
                "resource_id": 1,
                "status": "PAUSED",
                "notification_type_id": 1,
                "name": "n",
                "description": "d",
                "code": 0,
                "category": "SYSTEM",
                "event_type": "X",
                "resource_type": "SOURCE",
                "config": {},
            },
        )
        st_upd = client.notifications.update_setting(
            2, NotificationSettingUpdate(status="PAUSED")
        )
        assert isinstance(st_upd, NotificationSetting)

        mock_http_client.clear_responses()
        mock_http_client.add_response("/notification_settings/2", {"status": "deleted"})
        st_del = client.notifications.delete_setting(2)
        assert st_del.get("status") == "deleted"

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/notification_settings/notification_types/1", [st_get.model_dump()]
        )
        lst2 = client.notifications.get_settings_by_type(1, expand=True)
        assert isinstance(lst2[0], NotificationSetting)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/notification_settings/SOURCE/1", [st_get.model_dump()]
        )
        lst3 = client.notifications.get_resource_settings(
            "SOURCE", 1, expand=True, filter_overridden=True, notification_type_id=1
        )
        assert isinstance(lst3[0], NotificationSetting)

    def test_notification_setting_with_null_resource_id(self, client, mock_http_client):
        mock_http_client.add_response(
            "/notification_settings",
            [
                {
                    "id": 10,
                    "org_id": 1,
                    "owner_id": 1,
                    "channel": "APP",
                    "notification_resource_type": "USER",
                    "resource_id": None,
                    "status": "ACTIVE",
                    "notification_type_id": 1,
                    "name": "n",
                    "description": "d",
                    "code": 0,
                    "category": "SYSTEM",
                    "event_type": "X",
                    "resource_type": "SOURCE",
                    "config": {},
                }
            ],
        )
        lst = client.notifications.list_settings()
        assert isinstance(lst[0], NotificationSetting)
        assert lst[0].resource_id is None

    def test_notification_setting_model_with_null_resource_id(self):
        data = {
            "id": 10,
            "org_id": 1,
            "owner_id": 1,
            "channel": "APP",
            "notification_resource_type": "USER",
            "resource_id": None,
            "status": "ACTIVE",
            "notification_type_id": 1,
            "name": "n",
            "description": "d",
            "code": 0,
            "category": "SYSTEM",
            "event_type": "X",
            "resource_type": "SOURCE",
            "config": {},
        }
        model = NotificationSetting.model_validate(data)
        assert model.resource_id is None
