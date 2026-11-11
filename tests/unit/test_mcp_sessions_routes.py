"""Request shape for the mcp_sessions resource methods.

Each row names the method, the HTTP verb and path the call must send, the
expected query params, and the expected JSON body (None means not checked).
"""

import pytest

pytestmark = pytest.mark.unit

MCP_SESSIONS_ROUTE_CALLS = [
    pytest.param(
        lambda c: c.mcp_sessions.index_mcp_sessions(
            org_id=5,
            tool_set_revision_id=7,
            mcp_session_id="abc",
            initialized=True,
            terminated=False,
            page=2,
            per_page=10,
        ),
        "GET",
        "/mcp_sessions",
        {
            "org_id": 5,
            "tool_set_revision_id": 7,
            "mcp_session_id": "abc",
            "initialized": "true",
            "terminated": "false",
            "page": 2,
            "per_page": 10,
        },
        None,
        id="mcp_sessions.index_mcp_sessions",
    ),
    pytest.param(
        lambda c: c.mcp_sessions.index_mcp_sessions(),
        "GET",
        "/mcp_sessions",
        {},
        None,
        id="mcp_sessions.index_mcp_sessions_no_filters",
    ),
    pytest.param(
        lambda c: c.mcp_sessions.create_mcp_session({"tool_set_revision_id": 7}),
        "POST",
        "/mcp_sessions",
        {},
        {"tool_set_revision_id": 7},
        id="mcp_sessions.create_mcp_session",
    ),
    pytest.param(
        lambda c: c.mcp_sessions.show_mcp_session("s1"),
        "GET",
        "/mcp_sessions/s1",
        {},
        None,
        id="mcp_sessions.show_mcp_session",
    ),
    pytest.param(
        lambda c: c.mcp_sessions.mcp_sessions_update_mcp_session(
            "s1", {"initialized": True}
        ),
        "PATCH",
        "/mcp_sessions/s1",
        {},
        {"initialized": True},
        id="mcp_sessions.mcp_sessions_update_mcp_session",
    ),
    pytest.param(
        lambda c: c.mcp_sessions.mcp_sessions_update_mcp_session_put(
            "s1", {"initialized": True}
        ),
        "PUT",
        "/mcp_sessions/s1",
        {},
        {"initialized": True},
        id="mcp_sessions.mcp_sessions_update_mcp_session_put",
    ),
    pytest.param(
        lambda c: c.mcp_sessions.delete_mcp_session("s1"),
        "DELETE",
        "/mcp_sessions/s1",
        {},
        None,
        id="mcp_sessions.delete_mcp_session",
    ),
]


@pytest.mark.parametrize(
    "call, method, path, params, json_body", MCP_SESSIONS_ROUTE_CALLS
)
def test_mcp_sessions_route_sends_expected_request(
    mock_client, mock_http_client, call, method, path, params, json_body
):
    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    assert last["params"] == params
    if json_body is not None:
        assert last["json"] == json_body
