"""Request shape for the GET /<resource>/accessible routes.

Six of these methods already exist as list_accessible overrides; the coverage
matrix does not credit them, so each one is pinned here. Each row names the
method, the path the call must send, and the expected query params.
"""

import pytest

pytestmark = pytest.mark.unit

ACCESSIBLE_ROUTE_CALLS = [
    pytest.param(
        lambda c: c.code_containers.list_accessible(),
        "/code_containers/accessible",
        id="code_containers.list_accessible",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.list_accessible(),
        "/custom_data_flows/accessible",
        id="custom_data_flows.list_accessible",
    ),
    pytest.param(
        lambda c: c.credentials.list_accessible(),
        "/data_credentials/accessible",
        id="credentials.list_accessible",
    ),
    pytest.param(
        lambda c: c.lookups.list_accessible(),
        "/data_maps/accessible",
        id="lookups.list_accessible",
    ),
    pytest.param(
        lambda c: c.data_schemas.list_accessible(),
        "/data_schemas/accessible",
        id="data_schemas.list_accessible",
    ),
    pytest.param(
        lambda c: c.destinations.list_accessible(),
        "/data_sinks/accessible",
        id="destinations.list_accessible",
    ),
    pytest.param(
        lambda c: c.sources.list_accessible(),
        "/data_sources/accessible",
        id="sources.list_accessible",
    ),
    pytest.param(
        lambda c: c.transforms.transform_accessible_resources(),
        "/transform/accessible",
        id="transforms.transform_accessible_resources",
    ),
]


@pytest.mark.parametrize("call, path", ACCESSIBLE_ROUTE_CALLS)
def test_accessible_route_sends_get_request(mock_client, mock_http_client, call, path):
    # list_accessible parses the body into models, so answer with an empty list.
    mock_http_client.add_response(path, [])

    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == "GET"
    assert last["url"].endswith(path)
    assert last["params"] == {}
