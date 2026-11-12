"""Request shape for data credentials group routes served by DataCredentialsGroupsResource."""

import pytest

pytestmark = pytest.mark.unit

ROUTE_CALLS = [
    pytest.param(
        lambda c: c.data_credentials_groups.data_credentials_groups_update_data_credentials_group(
            7, {"name": "renamed"}
        ),
        "PATCH",
        "/data_credentials_groups/7",
        {"json": {"name": "renamed"}},
        id="data_credentials_groups.data_credentials_groups_update_data_credentials_group",
    ),
]


@pytest.mark.parametrize("call, method, path, expected", ROUTE_CALLS)
def test_data_credentials_group_route_sends_expected_request(
    mock_client, mock_http_client, call, method, path, expected
):
    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    for key, value in expected.items():
        assert last[key] == value
