"""Request shape for the tool_sets resource methods.

Each row names the method, the HTTP verb and path the call must send, the
expected query params, and the expected JSON body (None means not checked).
"""

import pytest

pytestmark = pytest.mark.unit

TOOL_SETS_ROUTE_CALLS = [
    pytest.param(
        lambda c: c.tool_sets.get("ts1"),
        "GET",
        "/tool_sets/ts1",
        {},
        None,
        id="tool_sets.get",
    ),
    pytest.param(
        lambda c: c.tool_sets.update("ts1", {"name": "x"}),
        "PUT",
        "/tool_sets/ts1",
        {},
        {"name": "x"},
        id="tool_sets.update",
    ),
    pytest.param(
        lambda c: c.tool_sets.delete("ts1"),
        "DELETE",
        "/tool_sets/ts1",
        {},
        None,
        id="tool_sets.delete",
    ),
    pytest.param(
        lambda c: c.tool_sets.tool_sets_update_tool_set("ts1", {"name": "x"}),
        "PATCH",
        "/tool_sets/ts1",
        {},
        {"name": "x"},
        id="tool_sets.tool_sets_update_tool_set",
    ),
    pytest.param(
        lambda c: c.tool_sets.tool_set_audit_log("ts1"),
        "GET",
        "/tool_sets/ts1/audit_log",
        {},
        None,
        id="tool_sets.tool_set_audit_log",
    ),
    pytest.param(
        lambda c: c.tool_sets.index_exports("ts1", tool_set_revision_id=5, page=2),
        "GET",
        "/tool_sets/ts1/exports",
        {"tool_set_revision_id": 5, "page": 2},
        None,
        id="tool_sets.index_exports",
    ),
    pytest.param(
        lambda c: c.tool_sets.create_export("ts1", {"tool_set_revision_id": 5}),
        "POST",
        "/tool_sets/ts1/exports",
        {},
        {"tool_set_revision_id": 5},
        id="tool_sets.create_export",
    ),
    pytest.param(
        lambda c: c.tool_sets.show_export("ts1", "e1"),
        "GET",
        "/tool_sets/ts1/exports/e1",
        {},
        None,
        id="tool_sets.show_export",
    ),
    pytest.param(
        lambda c: c.tool_sets.update_export("ts1", "e1", {"name": "x"}),
        "PUT",
        "/tool_sets/ts1/exports/e1",
        {},
        {"name": "x"},
        id="tool_sets.update_export",
    ),
    pytest.param(
        lambda c: c.tool_sets.delete_export("ts1", "e1"),
        "DELETE",
        "/tool_sets/ts1/exports/e1",
        {},
        None,
        id="tool_sets.delete_export",
    ),
    pytest.param(
        lambda c: c.tool_sets.activate_export("ts1", "e1"),
        "PUT",
        "/tool_sets/ts1/exports/e1/activate",
        {},
        None,
        id="tool_sets.activate_export",
    ),
    pytest.param(
        lambda c: c.tool_sets.pause_export("ts1", "e1"),
        "PUT",
        "/tool_sets/ts1/exports/e1/pause",
        {},
        None,
        id="tool_sets.pause_export",
    ),
    pytest.param(
        lambda c: c.tool_sets.retire_export("ts1", "e1"),
        "PUT",
        "/tool_sets/ts1/exports/e1/retire",
        {},
        None,
        id="tool_sets.retire_export",
    ),
    pytest.param(
        lambda c: c.tool_sets.index_revisions("ts1", page=1, per_page=10),
        "GET",
        "/tool_sets/ts1/revisions",
        {"page": 1, "per_page": 10},
        None,
        id="tool_sets.index_revisions",
    ),
    pytest.param(
        lambda c: c.tool_sets.create_revision("ts1", {"version": "1.0.0"}),
        "POST",
        "/tool_sets/ts1/revisions",
        {},
        {"version": "1.0.0"},
        id="tool_sets.create_revision",
    ),
    pytest.param(
        lambda c: c.tool_sets.show_revision("ts1", "r1"),
        "GET",
        "/tool_sets/ts1/revisions/r1",
        {},
        None,
        id="tool_sets.show_revision",
    ),
    pytest.param(
        lambda c: c.tool_sets.delete_revision("ts1", "r1"),
        "DELETE",
        "/tool_sets/ts1/revisions/r1",
        {},
        None,
        id="tool_sets.delete_revision",
    ),
    pytest.param(
        lambda c: c.tool_sets.publish_revision("ts1", "r1"),
        "PUT",
        "/tool_sets/ts1/revisions/r1/publish",
        {},
        None,
        id="tool_sets.publish_revision",
    ),
    pytest.param(
        lambda c: c.tool_sets.draft_revision("ts1", "r1"),
        "PUT",
        "/tool_sets/ts1/revisions/r1/draft",
        {},
        None,
        id="tool_sets.draft_revision",
    ),
    pytest.param(
        lambda c: c.tool_sets.deprecate_revision("ts1", "r1"),
        "PUT",
        "/tool_sets/ts1/revisions/r1/deprecate",
        {},
        None,
        id="tool_sets.deprecate_revision",
    ),
    pytest.param(
        lambda c: c.tool_sets.retire_revision("ts1", "r1"),
        "PUT",
        "/tool_sets/ts1/revisions/r1/retire",
        {},
        None,
        id="tool_sets.retire_revision",
    ),
    pytest.param(
        lambda c: c.tool_sets.tool_sets_index_tools("ts1"),
        "GET",
        "/tool_sets/ts1/tools",
        {},
        None,
        id="tool_sets.tool_sets_index_tools",
    ),
    pytest.param(
        lambda c: c.tool_sets.add_tools("ts1", {"tools": [{"id": 1}]}),
        "PUT",
        "/tool_sets/ts1/tools",
        {},
        {"tools": [{"id": 1}]},
        id="tool_sets.add_tools",
    ),
    pytest.param(
        lambda c: c.tool_sets.reset_tools("ts1", {"tools": [{"id": 1}]}),
        "POST",
        "/tool_sets/ts1/tools",
        {},
        {"tools": [{"id": 1}]},
        id="tool_sets.reset_tools",
    ),
    pytest.param(
        lambda c: c.tool_sets.remove_tools("ts1", {"tools": [{"id": 1}]}),
        "DELETE",
        "/tool_sets/ts1/tools",
        {},
        {"tools": [{"id": 1}]},
        id="tool_sets.remove_tools",
    ),
]


@pytest.mark.parametrize("call, method, path, params, json_body", TOOL_SETS_ROUTE_CALLS)
def test_tool_sets_route_sends_expected_request(
    mock_client, mock_http_client, call, method, path, params, json_body
):
    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    assert last["params"] == params
    if json_body is not None:
        assert last["json"] == json_body
