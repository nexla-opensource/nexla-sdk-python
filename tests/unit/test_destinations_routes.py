"""Route tests for data sink methods on client.destinations.

Each row calls one method and checks the HTTP method, the path, and the
query params or JSON body it sends. Rows with "response" give the mock a
body for methods that parse the response into a model.
"""

import pytest

from tests.utils import MockResponseBuilder

pytestmark = pytest.mark.unit

DESTINATION_BODY = MockResponseBuilder.destination()

DESTINATIONS_ROUTE_CALLS = [
    # Routes served by inherited BaseResource methods or existing destinations methods.
    pytest.param(
        lambda c: c.destinations.list(page=1, per_page=20),
        "GET",
        "/data_sinks",
        {"params": {"page": 1, "per_page": 20}, "response": [DESTINATION_BODY]},
        id="destinations.list",
    ),
    pytest.param(
        lambda c: c.destinations.create({"name": "x"}),
        "POST",
        "/data_sinks",
        {"json": {"name": "x"}, "response": DESTINATION_BODY},
        id="destinations.create",
    ),
    pytest.param(
        lambda c: c.destinations.search({"filters": []}, page=1),
        "POST",
        "/data_sinks/search",
        {
            "json": {"filters": []},
            "params": {"page": 1},
            "response": [DESTINATION_BODY],
        },
        id="destinations.search",
    ),
    # Method and path only. The backend reads {"tags": [...]}, but the shared
    # search_tags sends a bare list. Pinning the body would enshrine that mismatch.
    pytest.param(
        lambda c: c.destinations.search_tags(["a"]),
        "POST",
        "/data_sinks/search_tags",
        {"response": [DESTINATION_BODY]},
        id="destinations.search_tags",
    ),
    pytest.param(
        lambda c: c.destinations.delete(1),
        "DELETE",
        "/data_sinks/1",
        {},
        id="destinations.delete",
    ),
    pytest.param(
        lambda c: c.destinations.get(1, expand=True),
        "GET",
        "/data_sinks/1",
        {"params": {"expand": 1}, "response": DESTINATION_BODY},
        id="destinations.get",
    ),
    pytest.param(
        lambda c: c.destinations.update(1, {"name": "x"}),
        "PUT",
        "/data_sinks/1",
        {"json": {"name": "x"}, "response": DESTINATION_BODY},
        id="destinations.update",
    ),
    pytest.param(
        lambda c: c.destinations.copy(1),
        "POST",
        "/data_sinks/1/copy",
        {"json": {}, "response": DESTINATION_BODY},
        id="destinations.copy",
    ),
    pytest.param(
        lambda c: c.destinations.get_metrics(1, "files"),
        "GET",
        "/data_sinks/1/metrics/files",
        {},
        id="destinations.get_metrics_files",
    ),
    pytest.param(
        lambda c: c.destinations.get_metrics(1, "files_stats"),
        "GET",
        "/data_sinks/1/metrics/files_stats",
        {},
        id="destinations.get_metrics_files_stats",
    ),
    pytest.param(
        lambda c: c.destinations.get_metrics(1, "files_details"),
        "GET",
        "/data_sinks/1/metrics/files_details",
        {},
        id="destinations.get_metrics_files_details",
    ),
    pytest.param(
        lambda c: c.destinations.get_metrics(1, "quarantine_files"),
        "GET",
        "/data_sinks/1/metrics/quarantine_files",
        {},
        id="destinations.get_metrics_quarantine_files",
    ),
    pytest.param(
        lambda c: c.destinations.edit_flow_triggers(1, {"x": 1}, "add"),
        "PUT",
        "/data_sinks/1/flow_triggers",
        {"json": {"x": 1}},
        id="destinations.edit_flow_triggers_add",
    ),
    pytest.param(
        lambda c: c.destinations.edit_flow_triggers(1, {"x": 1}, "create"),
        "POST",
        "/data_sinks/1/flow_triggers",
        {"json": {"x": 1}},
        id="destinations.edit_flow_triggers_create",
    ),
    pytest.param(
        lambda c: c.destinations.edit_flow_triggers(1, {"x": 1}, "remove"),
        "DELETE",
        "/data_sinks/1/flow_triggers",
        {"json": {"x": 1}},
        id="destinations.edit_flow_triggers_remove",
    ),
    pytest.param(
        lambda c: c.destinations.edit_flow_triggers(
            1, {"x": 1}, "remove", all_triggers=True
        ),
        "DELETE",
        "/data_sinks/1/flow_triggers/all",
        {"json": {"x": 1}},
        id="destinations.edit_flow_triggers_remove_all",
    ),
    pytest.param(
        lambda c: c.destinations.edit_flow_triggers(1, {"x": 1}, "activate"),
        "PUT",
        "/data_sinks/1/flow_triggers/activate",
        {"json": {"x": 1}},
        id="destinations.edit_flow_triggers_activate",
    ),
    pytest.param(
        lambda c: c.destinations.edit_flow_triggers(
            1, {"x": 1}, "activate", all_triggers=True
        ),
        "PUT",
        "/data_sinks/1/flow_triggers/activate/all",
        {"json": {"x": 1}},
        id="destinations.edit_flow_triggers_activate_all",
    ),
    pytest.param(
        lambda c: c.destinations.edit_flow_triggers(1, {"x": 1}, "pause"),
        "PUT",
        "/data_sinks/1/flow_triggers/pause",
        {"json": {"x": 1}},
        id="destinations.edit_flow_triggers_pause",
    ),
    pytest.param(
        lambda c: c.destinations.edit_flow_triggers(
            1, {"x": 1}, "pause", all_triggers=True
        ),
        "PUT",
        "/data_sinks/1/flow_triggers/pause/all",
        {"json": {"x": 1}},
        id="destinations.edit_flow_triggers_pause_all",
    ),
    # New methods for routes that no existing method serves.
    pytest.param(
        lambda c: c.destinations.data_sinks_update_data_sink(
            1, {"name": "x"}, expand=True
        ),
        "PATCH",
        "/data_sinks/1",
        {"params": {"expand": True}, "json": {"name": "x"}},
        id="destinations.data_sinks_update_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.validate_data_sink_config(1, {"x": 1}),
        "POST",
        "/data_sinks/1/config/validate",
        {"json": {"x": 1}},
        id="destinations.validate_data_sink_config",
    ),
    pytest.param(
        lambda c: c.destinations.list_flow_accessors_via_data_sink(1),
        "GET",
        "/data_sinks/1/flow/accessors",
        {},
        id="destinations.list_flow_accessors_via_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.reset_flow_accessors_via_data_sink(
            1, {"accessors": []}
        ),
        "POST",
        "/data_sinks/1/flow/accessors",
        {"json": {"accessors": []}},
        id="destinations.reset_flow_accessors_via_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.add_flow_accessors_via_data_sink(1, {"accessors": []}),
        "PUT",
        "/data_sinks/1/flow/accessors",
        {"json": {"accessors": []}},
        id="destinations.add_flow_accessors_via_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.remove_flow_accessors_via_data_sink(
            1, {"accessors": []}
        ),
        "DELETE",
        "/data_sinks/1/flow/accessors",
        {"json": {"accessors": []}},
        id="destinations.remove_flow_accessors_via_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.list_flow_docs_via_data_sink(1),
        "GET",
        "/data_sinks/1/flow/docs",
        {},
        id="destinations.list_flow_docs_via_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.reset_flow_docs_via_data_sink(1, {"docs": []}),
        "POST",
        "/data_sinks/1/flow/docs",
        {"json": {"docs": []}},
        id="destinations.reset_flow_docs_via_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.add_flow_docs_via_data_sink(1, {"docs": []}),
        "PUT",
        "/data_sinks/1/flow/docs",
        {"json": {"docs": []}},
        id="destinations.add_flow_docs_via_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.remove_flow_docs_via_data_sink(1, {"docs": []}),
        "DELETE",
        "/data_sinks/1/flow/docs",
        {"json": {"docs": []}},
        id="destinations.remove_flow_docs_via_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.activate_flow_via_data_sink(
            1, all=True, full_tree=False, run_now="now"
        ),
        "PUT",
        "/data_sinks/1/flow/activate",
        {"params": {"all": True, "full_tree": False, "run_now": "now"}},
        id="destinations.activate_flow_via_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.pause_flow_via_data_sink(1, all=True),
        "PUT",
        "/data_sinks/1/flow/pause",
        {"params": {"all": True}},
        id="destinations.pause_flow_via_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.data_sinks_flow_audit_log(
            1, from_date="2026-01-01", to_date="2026-01-31", page="2"
        ),
        "GET",
        "/data_sinks/1/flow/audit_log",
        {"params": {"from": "2026-01-01", "to": "2026-01-31", "page": "2"}},
        id="destinations.data_sinks_flow_audit_log",
    ),
    pytest.param(
        lambda c: c.destinations.data_sinks_get_data_sink_offset(1, data_set_id=5),
        "GET",
        "/data_sinks/1/offset",
        {"params": {"data_set_id": 5}},
        id="destinations.data_sinks_get_data_sink_offset",
    ),
    pytest.param(
        lambda c: c.destinations.data_sinks_get_data_sink_quarantine_offset(
            1, data_set_id=5
        ),
        "GET",
        "/data_sinks/1/quarantine/offset",
        {"params": {"data_set_id": 5}},
        id="destinations.data_sinks_get_data_sink_quarantine_offset",
    ),
    pytest.param(
        lambda c: c.destinations.data_sinks_get_data_sink_run_status(1, run_id="r1"),
        "GET",
        "/data_sinks/1/run_status",
        {"params": {"run_id": "r1"}},
        id="destinations.data_sinks_get_data_sink_run_status",
    ),
    pytest.param(
        lambda c: c.destinations.data_sinks_probe_list_files_in_bucket_data_sink(
            1, {"x": 1}
        ),
        "PUT",
        "/data_sinks/1/probe/buckets",
        {"json": {"x": 1}},
        id="destinations.data_sinks_probe_list_files_in_bucket_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.data_sinks_probe_read_file_data_sink(1, {"x": 1}),
        "PUT",
        "/data_sinks/1/probe/files",
        {"json": {"x": 1}},
        id="destinations.data_sinks_probe_read_file_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.data_sinks_probe_read_quarantine_data_sink(
            1, {"x": 1}
        ),
        "PUT",
        "/data_sinks/1/probe/quarantine/sample",
        {"json": {"x": 1}},
        id="destinations.data_sinks_probe_read_quarantine_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.data_sinks_probe_detect_schemas_data_sink(1, {"x": 1}),
        "PUT",
        "/data_sinks/1/probe/schemas",
        {"json": {"x": 1}},
        id="destinations.data_sinks_probe_detect_schemas_data_sink",
    ),
    pytest.param(
        lambda c: c.destinations.data_sinks_probe_list_tree_data_sink(1, {"x": 1}),
        "PUT",
        "/data_sinks/1/probe/tree",
        {"json": {"x": 1}},
        id="destinations.data_sinks_probe_list_tree_data_sink",
    ),
]


@pytest.mark.parametrize("call, method, path, expected", DESTINATIONS_ROUTE_CALLS)
def test_destinations_route_sends_method_path_and_payload(
    mock_client, mock_http_client, call, method, path, expected
):
    expected = dict(expected)
    if "response" in expected:
        mock_http_client.add_response(path, expected.pop("response"))

    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    for key, value in expected.items():
        assert last[key] == value
