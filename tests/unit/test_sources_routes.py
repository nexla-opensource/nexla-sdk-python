"""Route tests for data source methods on client.sources.

Each row calls one method and checks the HTTP method, the path, and the
query params or JSON body it sends. Rows marked "response" give the mock a
body for methods that parse the response into a model.
"""

import pytest

from tests.utils import MockResponseBuilder

pytestmark = pytest.mark.unit

SOURCE_BODY = MockResponseBuilder.source()

SOURCES_ROUTE_CALLS = [
    # Routes served by inherited BaseResource methods or existing sources methods.
    pytest.param(
        lambda c: c.sources.list(page=1, per_page=20),
        "GET",
        "/data_sources",
        {"params": {"page": 1, "per_page": 20}, "response": [SOURCE_BODY]},
        id="sources.list",
    ),
    pytest.param(
        lambda c: c.sources.create({"name": "x"}),
        "POST",
        "/data_sources",
        {"json": {"name": "x"}, "response": SOURCE_BODY},
        id="sources.create",
    ),
    pytest.param(
        lambda c: c.sources.search({"filters": []}, page=1),
        "POST",
        "/data_sources/search",
        {"json": {"filters": []}, "params": {"page": 1}, "response": [SOURCE_BODY]},
        id="sources.search",
    ),
    pytest.param(
        lambda c: c.sources.search_tags(["a"]),
        "POST",
        "/data_sources/search_tags",
        {"json": ["a"], "params": {}, "response": [SOURCE_BODY]},
        id="sources.search_tags",
    ),
    pytest.param(
        lambda c: c.sources.delete(1),
        "DELETE",
        "/data_sources/1",
        {},
        id="sources.delete",
    ),
    pytest.param(
        lambda c: c.sources.get(1, expand=True),
        "GET",
        "/data_sources/1",
        {"params": {"expand": 1}, "response": SOURCE_BODY},
        id="sources.get",
    ),
    pytest.param(
        lambda c: c.sources.update(1, {"name": "x"}),
        "PUT",
        "/data_sources/1",
        {"json": {"name": "x"}, "response": SOURCE_BODY},
        id="sources.update",
    ),
    pytest.param(
        lambda c: c.sources.copy(1),
        "POST",
        "/data_sources/1/copy",
        {"json": {}, "response": SOURCE_BODY},
        id="sources.copy",
    ),
    pytest.param(
        lambda c: c.sources.run_now(1),
        "POST",
        "/data_sources/1/run_now",
        {},
        id="sources.run_now_post",
    ),
    pytest.param(
        lambda c: c.sources.run_now(1, "PUT"),
        "PUT",
        "/data_sources/1/run_now",
        {},
        id="sources.run_now_put",
    ),
    pytest.param(
        lambda c: c.sources.get_metrics(1, "files"),
        "GET",
        "/data_sources/1/metrics/files",
        {"params": {}},
        id="sources.get_metrics_files",
    ),
    pytest.param(
        lambda c: c.sources.get_metrics(1, "files_stats"),
        "GET",
        "/data_sources/1/metrics/files_stats",
        {"params": {}},
        id="sources.get_metrics_files_stats",
    ),
    pytest.param(
        lambda c: c.sources.get_metrics(1, "files_details"),
        "GET",
        "/data_sources/1/metrics/files_details",
        {"params": {}},
        id="sources.get_metrics_files_details",
    ),
    pytest.param(
        lambda c: c.sources.get_metrics(1, "quarantine_files"),
        "GET",
        "/data_sources/1/metrics/quarantine_files",
        {"params": {}},
        id="sources.get_metrics_quarantine_files",
    ),
    pytest.param(
        lambda c: c.sources.edit_flow_triggers(1, {"x": 1}, "add"),
        "PUT",
        "/data_sources/1/flow_triggers",
        {"json": {"x": 1}},
        id="sources.edit_flow_triggers_add",
    ),
    pytest.param(
        lambda c: c.sources.edit_flow_triggers(1, {"x": 1}, "reset"),
        "POST",
        "/data_sources/1/flow_triggers",
        {"json": {"x": 1}},
        id="sources.edit_flow_triggers_reset",
    ),
    pytest.param(
        lambda c: c.sources.edit_flow_triggers(1, {"x": 1}, "remove"),
        "DELETE",
        "/data_sources/1/flow_triggers",
        {"json": {"x": 1}},
        id="sources.edit_flow_triggers_remove",
    ),
    pytest.param(
        lambda c: c.sources.edit_flow_triggers(1, {"x": 1}, "pause"),
        "PUT",
        "/data_sources/1/flow_triggers/pause",
        {"json": {"x": 1}},
        id="sources.edit_flow_triggers_pause",
    ),
    pytest.param(
        lambda c: c.sources.edit_flow_triggers(1, {"x": 1}, "pause", all_triggers=True),
        "PUT",
        "/data_sources/1/flow_triggers/pause/all",
        {"json": {"x": 1}},
        id="sources.edit_flow_triggers_pause_all",
    ),
    pytest.param(
        lambda c: c.sources.edit_flow_triggers(1, {"x": 1}, "activate"),
        "PUT",
        "/data_sources/1/flow_triggers/activate",
        {"json": {"x": 1}},
        id="sources.edit_flow_triggers_activate",
    ),
    pytest.param(
        lambda c: c.sources.edit_flow_triggers(
            1, {"x": 1}, "activate", all_triggers=True
        ),
        "PUT",
        "/data_sources/1/flow_triggers/activate/all",
        {"json": {"x": 1}},
        id="sources.edit_flow_triggers_activate_all",
    ),
    pytest.param(
        lambda c: c.sources.edit_flow_triggers(
            1, {"x": 1}, "remove", all_triggers=True
        ),
        "DELETE",
        "/data_sources/1/flow_triggers/all",
        {"json": {"x": 1}},
        id="sources.edit_flow_triggers_remove_all",
    ),
    pytest.param(
        lambda c: c.flows.accessors_by_resource("data_sources", 1, mode="list"),
        "GET",
        "/data_sources/1/flow/accessors",
        {},
        id="flows.accessors_by_resource_list",
    ),
    pytest.param(
        lambda c: c.flows.accessors_by_resource(
            "data_sources", 1, mode="reset", payload={"accessors": []}
        ),
        "POST",
        "/data_sources/1/flow/accessors",
        {"json": {"accessors": []}},
        id="flows.accessors_by_resource_reset",
    ),
    pytest.param(
        lambda c: c.flows.accessors_by_resource(
            "data_sources", 1, mode="add", payload={"accessors": []}
        ),
        "PUT",
        "/data_sources/1/flow/accessors",
        {"json": {"accessors": []}},
        id="flows.accessors_by_resource_add",
    ),
    pytest.param(
        lambda c: c.flows.accessors_by_resource(
            "data_sources", 1, mode="remove", payload={"accessors": []}
        ),
        "DELETE",
        "/data_sources/1/flow/accessors",
        {"json": {"accessors": []}},
        id="flows.accessors_by_resource_remove",
    ),
    pytest.param(
        lambda c: c.flows.docs_by_resource("data_sources", 1, mode="list"),
        "GET",
        "/data_sources/1/flow/docs",
        {},
        id="flows.docs_by_resource_list",
    ),
    pytest.param(
        lambda c: c.flows.docs_by_resource(
            "data_sources", 1, mode="reset", payload=[{"id": 1}]
        ),
        "POST",
        "/data_sources/1/flow/docs",
        {"json": [{"id": 1}]},
        id="flows.docs_by_resource_reset",
    ),
    pytest.param(
        lambda c: c.flows.docs_by_resource(
            "data_sources", 1, mode="add", payload=[{"id": 1}]
        ),
        "PUT",
        "/data_sources/1/flow/docs",
        {"json": [{"id": 1}]},
        id="flows.docs_by_resource_add",
    ),
    pytest.param(
        lambda c: c.flows.docs_by_resource(
            "data_sources", 1, mode="remove", payload=[{"id": 1}]
        ),
        "DELETE",
        "/data_sources/1/flow/docs",
        {"json": [{"id": 1}]},
        id="flows.docs_by_resource_remove",
    ),
    # New methods.
    pytest.param(
        lambda c: c.sources.data_sources_update_data_source(
            1, {"name": "x"}, force=True, run_now=False
        ),
        "PATCH",
        "/data_sources/1",
        {"params": {"force": True, "run_now": False}, "json": {"name": "x"}},
        id="sources.data_sources_update_data_source",
    ),
    pytest.param(
        lambda c: c.sources.validate_data_source_config(1, {"name": "x"}),
        "POST",
        "/data_sources/1/config/validate",
        {"json": {"name": "x"}},
        id="sources.validate_data_source_config",
    ),
    pytest.param(
        lambda c: c.sources.get_external_file_status_alias(1, status="done", page=2),
        "GET",
        "/data_sources/1/file/external/status",
        {"params": {"status": "done", "page": 2}},
        id="sources.get_external_file_status_alias",
    ),
    pytest.param(
        lambda c: c.sources.get_external_file_status(1, sortBy="name"),
        "GET",
        "/data_sources/1/file/status",
        {"params": {"sortBy": "name"}},
        id="sources.get_external_file_status",
    ),
    pytest.param(
        lambda c: c.sources.dequeue_external_file(1, "abc", filePath="/x"),
        "DELETE",
        "/data_sources/1/file/external/abc",
        {"params": {"filePath": "/x"}},
        id="sources.dequeue_external_file",
    ),
    pytest.param(
        lambda c: c.sources.data_sources_flow_audit_log(
            1, from_date="2026-01-01", to_date="2026-02-01", page="1"
        ),
        "GET",
        "/data_sources/1/flow/audit_log",
        {"params": {"from": "2026-01-01", "to": "2026-02-01", "page": "1"}},
        id="sources.data_sources_flow_audit_log",
    ),
    pytest.param(
        lambda c: c.sources.activate_flow_via_data_source(1, all=True, full_tree=True),
        "PUT",
        "/data_sources/1/flow/activate",
        {"params": {"all": True, "full_tree": True}},
        id="sources.activate_flow_via_data_source",
    ),
    pytest.param(
        lambda c: c.sources.pause_flow_via_data_source(1, all=True),
        "PUT",
        "/data_sources/1/flow/pause",
        {"params": {"all": True}},
        id="sources.pause_flow_via_data_source",
    ),
    pytest.param(
        lambda c: c.sources.auto_create_nexset(1, include_samples=True),
        "POST",
        "/data_sources/1/nexset",
        {"params": {"include_samples": True}},
        id="sources.auto_create_nexset",
    ),
    pytest.param(
        lambda c: c.sources.data_sources_get_data_source_offset(1, data_set_id=5),
        "GET",
        "/data_sources/1/offset",
        {"params": {"data_set_id": 5}},
        id="sources.data_sources_get_data_source_offset",
    ),
    pytest.param(
        lambda c: c.sources.data_sources_get_data_source_quarantine_offset(
            1, data_set_id=5
        ),
        "GET",
        "/data_sources/1/quarantine/offset",
        {"params": {"data_set_id": 5}},
        id="sources.data_sources_get_data_source_quarantine_offset",
    ),
    pytest.param(
        lambda c: c.sources.data_sources_probe_list_files_data_source(1, {"x": 1}),
        "PUT",
        "/data_sources/1/probe/buckets",
        {"json": {"x": 1}},
        id="sources.data_sources_probe_list_files_data_source",
    ),
    pytest.param(
        lambda c: c.sources.data_sources_probe_read_file_data_source(1, {"x": 1}),
        "PUT",
        "/data_sources/1/probe/files",
        {"json": {"x": 1}},
        id="sources.data_sources_probe_read_file_data_source",
    ),
    pytest.param(
        lambda c: c.sources.data_sources_probe_read_quarantine_data_source(1, {"x": 1}),
        "PUT",
        "/data_sources/1/probe/quarantine/sample",
        {"json": {"x": 1}},
        id="sources.data_sources_probe_read_quarantine_data_source",
    ),
    pytest.param(
        lambda c: c.sources.data_sources_probe_read_sample_data_source(
            1,
            {"x": 1},
            return_original_response_status=True,
            page=1,
            per_page=10,
        ),
        "PUT",
        "/data_sources/1/probe/sample",
        {
            "json": {"x": 1},
            "params": {
                "return_original_response_status": True,
                "page": 1,
                "per_page": 10,
            },
        },
        id="sources.data_sources_probe_read_sample_data_source",
    ),
    pytest.param(
        lambda c: c.sources.data_sources_probe_detect_schemas_data_source(1, {"x": 1}),
        "PUT",
        "/data_sources/1/probe/schemas",
        {"json": {"x": 1}},
        id="sources.data_sources_probe_detect_schemas_data_source",
    ),
    pytest.param(
        lambda c: c.sources.data_sources_probe_list_tree_data_source(1, {"x": 1}),
        "PUT",
        "/data_sources/1/probe/tree",
        {"json": {"x": 1}},
        id="sources.data_sources_probe_list_tree_data_source",
    ),
]


@pytest.mark.parametrize("call, method, path, expected", SOURCES_ROUTE_CALLS)
def test_sources_route_sends_method_path_and_payload(
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
