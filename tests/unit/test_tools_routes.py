"""Request shape for the tools resource methods.

Each row names the method, the HTTP verb and path the call must send, the
expected query params, and the expected JSON body (None means not checked).
"""

import pytest

pytestmark = pytest.mark.unit

TOOLS_ROUTE_CALLS = [
    pytest.param(
        lambda c: c.tools.get("t1"),
        "GET",
        "/tools/t1",
        {},
        None,
        id="tools.get",
    ),
    pytest.param(
        lambda c: c.tools.update("t1", {"name": "x"}),
        "PUT",
        "/tools/t1",
        {},
        {"name": "x"},
        id="tools.update",
    ),
    pytest.param(
        lambda c: c.tools.delete("t1"),
        "DELETE",
        "/tools/t1",
        {},
        None,
        id="tools.delete",
    ),
    pytest.param(
        lambda c: c.tools.tools_update_tool("t1", {"name": "x"}),
        "PATCH",
        "/tools/t1",
        {},
        {"name": "x"},
        id="tools.tools_update_tool",
    ),
    pytest.param(
        lambda c: c.tools.top_level_receipts_index(tool_id=7, page=2),
        "GET",
        "/tools/receipts",
        {"tool_id": 7, "page": 2},
        None,
        id="tools.top_level_receipts_index",
    ),
    pytest.param(
        lambda c: c.tools.top_level_receipts_show("r1"),
        "GET",
        "/tools/receipts/r1",
        {},
        None,
        id="tools.top_level_receipts_show",
    ),
    pytest.param(
        lambda c: c.tools.tool_definition("t1"),
        "GET",
        "/tools/t1/definition",
        {},
        None,
        id="tools.tool_definition",
    ),
    pytest.param(
        lambda c: c.tools.tool_receipts_index("t1", per_page=50),
        "GET",
        "/tools/t1/receipts",
        {"per_page": 50},
        None,
        id="tools.tool_receipts_index",
    ),
    pytest.param(
        lambda c: c.tools.tool_receipts_show("t1", "r1"),
        "GET",
        "/tools/t1/receipts/r1",
        {},
        None,
        id="tools.tool_receipts_show",
    ),
    pytest.param(
        lambda c: c.tools.index_versions("t1", page=1, per_page=10),
        "GET",
        "/tools/t1/versions",
        {"page": 1, "per_page": 10},
        None,
        id="tools.index_versions",
    ),
    pytest.param(
        lambda c: c.tools.create_version("t1", {"version": "1.0.0"}),
        "POST",
        "/tools/t1/versions",
        {},
        {"version": "1.0.0"},
        id="tools.create_version",
    ),
    pytest.param(
        lambda c: c.tools.delete_version("t1", "v1"),
        "DELETE",
        "/tools/t1/versions/v1",
        {},
        None,
        id="tools.delete_version",
    ),
    pytest.param(
        lambda c: c.tools.show_version("t1", "v1"),
        "GET",
        "/tools/t1/versions/v1",
        {},
        None,
        id="tools.show_version",
    ),
    pytest.param(
        lambda c: c.tools.version_definition("t1", "v1"),
        "GET",
        "/tools/t1/versions/v1/definition",
        {},
        None,
        id="tools.version_definition",
    ),
    pytest.param(
        lambda c: c.tools.deprecate_version("t1", "v1"),
        "PUT",
        "/tools/t1/versions/v1/deprecate",
        {},
        None,
        id="tools.deprecate_version",
    ),
    pytest.param(
        lambda c: c.tools.draft_version("t1", "v1"),
        "PUT",
        "/tools/t1/versions/v1/draft",
        {},
        None,
        id="tools.draft_version",
    ),
    pytest.param(
        lambda c: c.tools.publish_version("t1", "v1"),
        "PUT",
        "/tools/t1/versions/v1/publish",
        {},
        None,
        id="tools.publish_version",
    ),
    pytest.param(
        lambda c: c.tools.retire_version("t1", "v1"),
        "PUT",
        "/tools/t1/versions/v1/retire",
        {},
        None,
        id="tools.retire_version",
    ),
    pytest.param(
        lambda c: c.tools.version_receipts_index("t1", "v1", page=3),
        "GET",
        "/tools/t1/versions/v1/receipts",
        {"page": 3},
        None,
        id="tools.version_receipts_index",
    ),
    pytest.param(
        lambda c: c.tools.version_receipts_create("t1", "v1", {"status": "ok"}),
        "POST",
        "/tools/t1/versions/v1/receipts",
        {},
        {"status": "ok"},
        id="tools.version_receipts_create",
    ),
    pytest.param(
        lambda c: c.tools.version_receipts_show("t1", "v1", "r1"),
        "GET",
        "/tools/t1/versions/v1/receipts/r1",
        {},
        None,
        id="tools.version_receipts_show",
    ),
]


@pytest.mark.parametrize("call, method, path, params, json_body", TOOLS_ROUTE_CALLS)
def test_tools_route_sends_expected_request(
    mock_client, mock_http_client, call, method, path, params, json_body
):
    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    assert last["params"] == params
    if json_body is not None:
        assert last["json"] == json_body
