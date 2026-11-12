"""Request shape for custom data flow routes served by CustomDataFlowsResource."""

import pytest

pytestmark = pytest.mark.unit

ROUTE_CALLS = [
    pytest.param(
        lambda c: c.custom_data_flows.custom_data_flows_update_custom_data_flow(
            3, {"name": "renamed"}
        ),
        "PATCH",
        "/custom_data_flows/3",
        {"json": {"name": "renamed"}},
        id="custom_data_flows.custom_data_flows_update_custom_data_flow",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.get_custom_data_flow_metrics_by_name(
            3, "summary"
        ),
        "GET",
        "/custom_data_flows/3/metrics/summary",
        {},
        id="custom_data_flows.get_custom_data_flow_metrics_by_name",
    ),
    # Already served by edit_code_containers, which maps mode to verb.
    pytest.param(
        lambda c: c.custom_data_flows.edit_code_containers(3, {"ids": [1]}, "list"),
        "GET",
        "/custom_data_flows/3/code_containers",
        {"json": {"ids": [1]}},
        id="custom_data_flows.edit_code_containers_list",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.edit_code_containers(3, {"ids": [1]}, "reset"),
        "POST",
        "/custom_data_flows/3/code_containers",
        {"json": {"ids": [1]}},
        id="custom_data_flows.edit_code_containers_reset",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.edit_code_containers(3, {"ids": [1]}, "add"),
        "PUT",
        "/custom_data_flows/3/code_containers",
        {"json": {"ids": [1]}},
        id="custom_data_flows.edit_code_containers_add",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.edit_code_containers(3, {"ids": [1]}, "remove"),
        "DELETE",
        "/custom_data_flows/3/code_containers",
        {"json": {"ids": [1]}},
        id="custom_data_flows.edit_code_containers_remove",
    ),
    # Already served by edit_data_credentials, which maps mode to verb.
    pytest.param(
        lambda c: c.custom_data_flows.edit_data_credentials(3, {"ids": [1]}, "list"),
        "GET",
        "/custom_data_flows/3/data_credentials",
        {"json": {"ids": [1]}},
        id="custom_data_flows.edit_data_credentials_list",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.edit_data_credentials(3, {"ids": [1]}, "reset"),
        "POST",
        "/custom_data_flows/3/data_credentials",
        {"json": {"ids": [1]}},
        id="custom_data_flows.edit_data_credentials_reset",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.edit_data_credentials(3, {"ids": [1]}, "add"),
        "PUT",
        "/custom_data_flows/3/data_credentials",
        {"json": {"ids": [1]}},
        id="custom_data_flows.edit_data_credentials_add",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.edit_data_credentials(3, {"ids": [1]}, "remove"),
        "DELETE",
        "/custom_data_flows/3/data_credentials",
        {"json": {"ids": [1]}},
        id="custom_data_flows.edit_data_credentials_remove",
    ),
]


@pytest.mark.parametrize("call, method, path, expected", ROUTE_CALLS)
def test_custom_data_flow_route_sends_expected_request(
    mock_client, mock_http_client, call, method, path, expected
):
    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    for key, value in expected.items():
        assert last[key] == value
