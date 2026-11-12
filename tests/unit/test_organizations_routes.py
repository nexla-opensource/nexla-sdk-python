"""Route tests for organization methods added for missing routes.

Each row calls one method and checks the HTTP method, the path, and the
query params or JSON body it sends.
"""

import pytest

pytestmark = pytest.mark.unit

ORG_ROUTE_CALLS = [
    pytest.param(
        lambda c: c.organizations.activate_sources(3),
        "PUT",
        "/orgs/3/source_activate",
        {},
        id="organizations.activate_sources",
    ),
    pytest.param(
        lambda c: c.organizations.activate_sources(3, status="paused"),
        "PUT",
        "/orgs/3/source_activate/paused",
        {},
        id="organizations.activate_sources_with_status",
    ),
    pytest.param(
        lambda c: c.organizations.pause_sources(3),
        "PUT",
        "/orgs/3/source_pause",
        {},
        id="organizations.pause_sources",
    ),
    pytest.param(
        lambda c: c.organizations.pause_sources(3, status="ready"),
        "PUT",
        "/orgs/3/source_pause/ready",
        {},
        id="organizations.pause_sources_with_status",
    ),
    pytest.param(
        lambda c: c.organizations.get_allowed_clusters(3),
        "GET",
        "/orgs/3/allowed_clusters",
        {},
        id="organizations.get_allowed_clusters",
    ),
    pytest.param(
        lambda c: c.organizations.get_quarantine_settings(3),
        "GET",
        "/orgs/3/quarantine_settings",
        {},
        id="organizations.get_quarantine_settings",
    ),
    pytest.param(
        lambda c: c.organizations.create_quarantine_settings(
            3, {"data_credentials_id": 9}
        ),
        "POST",
        "/orgs/3/quarantine_settings",
        {"json": {"data_credentials_id": 9}},
        id="organizations.create_quarantine_settings",
    ),
    pytest.param(
        lambda c: c.organizations.update_quarantine_settings(
            3, {"data_credentials_id": 9}
        ),
        "PUT",
        "/orgs/3/quarantine_settings",
        {"json": {"data_credentials_id": 9}},
        id="organizations.update_quarantine_settings",
    ),
    pytest.param(
        lambda c: c.organizations.delete_quarantine_settings(3),
        "DELETE",
        "/orgs/3/quarantine_settings",
        {},
        id="organizations.delete_quarantine_settings",
    ),
]


@pytest.mark.parametrize("call, method, path, expected", ORG_ROUTE_CALLS)
def test_org_route_sends_method_path_and_payload(
    mock_client, mock_http_client, call, method, path, expected
):
    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    for key, value in expected.items():
        assert last[key] == value
