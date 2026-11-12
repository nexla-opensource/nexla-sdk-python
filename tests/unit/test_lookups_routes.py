"""Request shape for the lookups (data_maps) resource methods added for missing routes.

Each row names the method, the HTTP verb and path the call must send, the
expected query params, and the expected JSON body (None means not checked).
"""

import pytest

pytestmark = pytest.mark.unit

LOOKUPS_ROUTE_CALLS = [
    pytest.param(
        lambda c: c.lookups.data_maps_update_data_map(1, {"name": "x"}),
        "PATCH",
        "/data_maps/1",
        {},
        {"name": "x"},
        id="lookups.data_maps_update_data_map",
    ),
    pytest.param(
        lambda c: c.lookups.data_maps_read_data_map_sample(1, page=2, per_page=10),
        "PUT",
        "/data_maps/1/probe/sample",
        {"page": 2, "per_page": 10},
        {},
        id="lookups.data_maps_read_data_map_sample",
    ),
]


@pytest.mark.parametrize("call, method, path, params, json_body", LOOKUPS_ROUTE_CALLS)
def test_lookups_route_sends_expected_request(
    mock_client, mock_http_client, call, method, path, params, json_body
):
    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    assert last["params"] == params
    if json_body is not None:
        assert last["json"] == json_body
