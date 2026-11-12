"""Route tests for flow methods added for missing routes.

Each row calls one method and checks the HTTP method, the path, and the
query params or JSON body it sends.
"""

import pytest

pytestmark = pytest.mark.unit

FLOW_ROUTE_CALLS = [
    pytest.param(
        lambda c: c.flows.get_document_schema(),
        "GET",
        "/flows/document/schema",
        {},
        id="flows.get_document_schema",
    ),
    pytest.param(
        lambda c: c.flows.get_document(5),
        "GET",
        "/flows/5/document",
        {},
        id="flows.get_document",
    ),
    pytest.param(
        lambda c: c.flows.plan_flow({"document": {"name": "x"}}),
        "POST",
        "/flows/plan",
        {"json": {"document": {"name": "x"}}},
        id="flows.plan_flow",
    ),
    pytest.param(
        lambda c: c.flows.get_daily_metrics(
            7, start_time="2026-01-01", end_time="2026-02-01"
        ),
        "GET",
        "/flows/7/metrics/daily",
        {"params": {"from": "2026-01-01", "to": "2026-02-01"}},
        id="flows.get_daily_metrics",
    ),
    pytest.param(
        lambda c: c.flows.list_runs(5, limit=10, offset=20),
        "GET",
        "/flows/5/runs",
        {"params": {"limit": 10, "offset": 20}},
        id="flows.list_runs",
    ),
    pytest.param(
        lambda c: c.flows.get_run(5, 9),
        "GET",
        "/flows/5/runs/9",
        {},
        id="flows.get_run",
    ),
    pytest.param(
        lambda c: c.flows.cancel_run(5, "abc", force=True),
        "POST",
        "/flows/5/runs/abc/cancel",
        {"params": {"force": True}},
        id="flows.cancel_run_forced",
    ),
    pytest.param(
        lambda c: c.flows.cancel_run(5, 9),
        "POST",
        "/flows/5/runs/9/cancel",
        {"params": {}},
        id="flows.cancel_run",
    ),
    pytest.param(
        lambda c: c.flows.retry_run(5, 9, {"max_attempts": 2}),
        "POST",
        "/flows/5/runs/9/retry",
        {"json": {"max_attempts": 2}},
        id="flows.retry_run",
    ),
    pytest.param(
        lambda c: c.flows.retry_run(5, 9),
        "POST",
        "/flows/5/runs/9/retry",
        {},
        id="flows.retry_run_without_config",
    ),
]


@pytest.mark.parametrize("call, method, path, expected", FLOW_ROUTE_CALLS)
def test_flow_route_sends_method_path_and_payload(
    mock_client, mock_http_client, call, method, path, expected
):
    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    for key, value in expected.items():
        assert last[key] == value
