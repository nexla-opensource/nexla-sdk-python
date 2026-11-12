"""Methods whose route does not exist on the Nexla API.

Each method is kept for compatibility. Each call still sends its original
request and must emit a DeprecationWarning that names the missing route.
"""

import pytest

pytestmark = pytest.mark.unit

MISSING_ROUTE_CALLS = [
    pytest.param(
        lambda c: c.genai.delete_org_settings({"x": 1}),
        "DELETE",
        "/gen_ai_org_settings",
        id="genai.delete_org_settings",
    ),
    pytest.param(
        lambda c: c.projects.get_data_flows_legacy(1),
        "GET",
        "/projects/1/data_flows",
        id="projects.get_data_flows_legacy",
    ),
    pytest.param(
        lambda c: c.projects.add_data_flows_legacy(1, {"data_flows": []}),
        "PUT",
        "/projects/1/data_flows",
        id="projects.add_data_flows_legacy",
    ),
    pytest.param(
        lambda c: c.projects.replace_data_flows_legacy(1, {"data_flows": []}),
        "POST",
        "/projects/1/data_flows",
        id="projects.replace_data_flows_legacy",
    ),
    pytest.param(
        lambda c: c.projects.remove_data_flows_legacy(1),
        "DELETE",
        "/projects/1/data_flows",
        id="projects.remove_data_flows_legacy",
    ),
    pytest.param(
        lambda c: c.data_flows.list_data_source_flows(),
        "GET",
        "/data_flows/data_source",
        id="data_flows.list_data_source_flows",
    ),
    pytest.param(
        lambda c: c.data_flows.create_data_source_flow({"name": "x"}),
        "POST",
        "/data_flows/data_source",
        id="data_flows.create_data_source_flow",
    ),
    pytest.param(
        lambda c: c.data_flows.list_data_sink_flows(),
        "GET",
        "/data_flows/data_sink",
        id="data_flows.list_data_sink_flows",
    ),
    pytest.param(
        lambda c: c.data_flows.create_data_sink_flow({"name": "x"}),
        "POST",
        "/data_flows/data_sink",
        id="data_flows.create_data_sink_flow",
    ),
    pytest.param(
        lambda c: c.data_flows.get_data_source_audit_log(1),
        "GET",
        "/data_flows/data_source/1/audit_log",
        id="data_flows.get_data_source_audit_log",
    ),
    pytest.param(
        lambda c: c.data_flows.get_data_sink_audit_log(1),
        "GET",
        "/data_flows/data_sink/1/audit_log",
        id="data_flows.get_data_sink_audit_log",
    ),
    pytest.param(
        lambda c: c.cubejs.query({"query": {}}),
        "POST",
        "/cubejs/query",
        id="cubejs.query",
    ),
    pytest.param(
        lambda c: c.sources.validate_config({"name": "x"}),
        "POST",
        "/data_sources/config/validate",
        id="sources.validate_config",
    ),
    pytest.param(
        lambda c: c.destinations.validate_config({"name": "x"}),
        "POST",
        "/data_sinks/config/validate",
        id="destinations.validate_config",
    ),
    pytest.param(
        lambda c: c.nexsets.catalog_add(1, {"catalog_ref": 2}),
        "POST",
        "/data_sets/1/catalog",
        id="nexsets.catalog_add",
    ),
    pytest.param(
        lambda c: c.organizations.get_auth_settings(1),
        "GET",
        "/orgs/1/auth_settings",
        id="organizations.get_auth_settings",
    ),
    pytest.param(
        lambda c: c.organizations.update_auth_setting(1, 2, True),
        "PUT",
        "/orgs/1/auth_settings/2",
        id="organizations.update_auth_setting",
    ),
]


@pytest.mark.parametrize("call, method, path", MISSING_ROUTE_CALLS)
def test_missing_route_warns_and_keeps_request(
    mock_client, mock_http_client, call, method, path
):
    mock_http_client.add_response(path, [])

    with pytest.warns(DeprecationWarning, match="does not exist on the Nexla API"):
        call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
