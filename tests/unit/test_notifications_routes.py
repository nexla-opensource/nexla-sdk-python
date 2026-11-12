"""Route tests for notification methods added for missing routes.

Each row calls one method and checks the HTTP method, the path, and the
query params it sends.
"""

import pytest

pytestmark = pytest.mark.unit

NOTIFICATION_ROUTE_CALLS = [
    pytest.param(
        lambda c: c.notifications.get_schema(),
        "GET",
        "/notifications/schema",
        {},
        id="notifications.get_schema",
    ),
    pytest.param(
        lambda c: c.notifications.get_schema(method="post"),
        "GET",
        "/notifications/schema",
        {"params": {"method": "post"}},
        id="notifications.get_schema_with_method",
    ),
    pytest.param(
        lambda c: c.notifications.get_summary(
            level="ERROR",
            from_date="2026-01-01",
            to_date="2026-02-01",
            limit=5,
            org_id=3,
        ),
        "GET",
        "/notifications/summary",
        {
            "params": {
                "level": "ERROR",
                "from_date": "2026-01-01",
                "to_date": "2026-02-01",
                "limit": 5,
                "org_id": 3,
            }
        },
        id="notifications.get_summary",
    ),
    pytest.param(
        lambda c: c.notifications.get_summary(),
        "GET",
        "/notifications/summary",
        {"params": {}},
        id="notifications.get_summary_defaults",
    ),
    pytest.param(
        lambda c: c.notifications.get_unread_count(org_id=3),
        "GET",
        "/notifications/unread-count",
        {"params": {"org_id": 3}},
        id="notifications.get_unread_count",
    ),
    pytest.param(
        lambda c: c.notifications.mark_all_as_read(),
        "PUT",
        "/notifications/read-all",
        {"params": {}},
        id="notifications.mark_all_as_read",
    ),
    pytest.param(
        lambda c: c.notifications.mark_all_as_read(org_id=3),
        "PUT",
        "/notifications/read-all",
        {"params": {"org_id": 3}},
        id="notifications.mark_all_as_read_with_org",
    ),
]


@pytest.mark.parametrize("call, method, path, expected", NOTIFICATION_ROUTE_CALLS)
def test_notification_route_sends_method_path_and_params(
    mock_client, mock_http_client, call, method, path, expected
):
    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    for key, value in expected.items():
        assert last[key] == value
