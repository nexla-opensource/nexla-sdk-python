"""Route tests for data set methods on client.nexsets.

Each row calls one method and checks the HTTP method, the path, and the
query params or JSON body it sends. Rows with "response" give the mock a
body for methods that parse the response into a model.
"""

import pytest

from tests.utils import MockResponseBuilder

pytestmark = pytest.mark.unit

NEXSET_BODY = MockResponseBuilder.nexset()

NEXSETS_ROUTE_CALLS = [
    # Routes served by inherited BaseResource methods or existing nexsets methods.
    pytest.param(
        lambda c: c.nexsets.list(page=1, per_page=50),
        "GET",
        "/data_sets",
        {"params": {"page": 1, "per_page": 50}, "response": []},
        id="nexsets.list",
    ),
    # Served by create. It does not forward the spec query params (activate_now, expand, ...).
    pytest.param(
        lambda c: c.nexsets.create({"name": "x"}),
        "POST",
        "/data_sets",
        {"json": {"name": "x"}, "response": NEXSET_BODY},
        id="nexsets.create",
    ),
    pytest.param(
        lambda c: c.nexsets.search({"filters": []}, page=1),
        "POST",
        "/data_sets/search",
        {"json": {"filters": []}, "params": {"page": 1}, "response": []},
        id="nexsets.search",
    ),
    # Method and path only. The backend reads {"tags": [...]}, but the shared
    # search_tags sends a bare list. Pinning the body would enshrine that mismatch.
    pytest.param(
        lambda c: c.nexsets.search_tags(["a"]),
        "POST",
        "/data_sets/search_tags",
        {"response": []},
        id="nexsets.search_tags",
    ),
    pytest.param(
        lambda c: c.nexsets.delete(1),
        "DELETE",
        "/data_sets/1",
        {},
        id="nexsets.delete",
    ),
    pytest.param(
        lambda c: c.nexsets.get(1, expand=True),
        "GET",
        "/data_sets/1",
        {"params": {"expand": 1}, "response": NEXSET_BODY},
        id="nexsets.get",
    ),
    pytest.param(
        lambda c: c.nexsets.update(1, {"name": "x"}),
        "PUT",
        "/data_sets/1",
        {"json": {"name": "x"}, "response": NEXSET_BODY},
        id="nexsets.update",
    ),
    pytest.param(
        lambda c: c.nexsets.copy(1),
        "POST",
        "/data_sets/1/copy",
        {"json": {}, "response": NEXSET_BODY},
        id="nexsets.copy",
    ),
    # Served by get_metrics(set_id, metrics_name), which builds /metrics/{name}.
    pytest.param(
        lambda c: c.nexsets.get_metrics(1, "files"),
        "GET",
        "/data_sets/1/metrics/files",
        {"params": {}},
        id="nexsets.get_metrics.files",
    ),
    pytest.param(
        lambda c: c.nexsets.get_metrics(1, "files_details"),
        "GET",
        "/data_sets/1/metrics/files_details",
        {"params": {}},
        id="nexsets.get_metrics.files_details",
    ),
    pytest.param(
        lambda c: c.nexsets.get_metrics(1, "files_stats"),
        "GET",
        "/data_sets/1/metrics/files_stats",
        {"params": {}},
        id="nexsets.get_metrics.files_stats",
    ),
    pytest.param(
        lambda c: c.nexsets.get_metrics(1, "quarantine_files"),
        "GET",
        "/data_sets/1/metrics/quarantine_files",
        {"params": {}},
        id="nexsets.get_metrics.quarantine_files",
    ),
    # New methods.
    pytest.param(
        lambda c: c.nexsets.data_sets_update_data_set(1, {"name": "x"}, expand=True),
        "PATCH",
        "/data_sets/1",
        {"json": {"name": "x"}, "params": {"expand": 1}},
        id="nexsets.data_sets_update_data_set",
    ),
    pytest.param(
        lambda c: c.nexsets.list_sync_api_compatible(status="all", page=2),
        "GET",
        "/data_sets/sync_api_compatible",
        {"params": {"status": "all", "page": 2}},
        id="nexsets.list_sync_api_compatible",
    ),
    pytest.param(
        lambda c: c.nexsets.data_sets_update_catalog_ref_collection(5, {"x": 1}),
        "PATCH",
        "/data_sets/catalog_refs/5",
        {"json": {"x": 1}},
        id="nexsets.data_sets_update_catalog_ref_collection",
    ),
    pytest.param(
        lambda c: c.nexsets.list_catalog_refs_for_set(1, page=2, per_page=10),
        "GET",
        "/data_sets/1/catalog_refs",
        {"params": {"page": 2, "per_page": 10}},
        id="nexsets.list_catalog_refs_for_set",
    ),
    pytest.param(
        lambda c: c.nexsets.get_catalog_ref_for_set(1, 5),
        "GET",
        "/data_sets/1/catalog_refs/5",
        {},
        id="nexsets.get_catalog_ref_for_set",
    ),
    pytest.param(
        lambda c: c.nexsets.data_sets_update_catalog_ref(1, 5, {"x": 1}),
        "PATCH",
        "/data_sets/1/catalog_refs/5",
        {"json": {"x": 1}},
        id="nexsets.data_sets_update_catalog_ref",
    ),
    pytest.param(
        lambda c: c.nexsets.data_sets_update_catalog_ref_put(1, 5, {"x": 1}),
        "PUT",
        "/data_sets/1/catalog_refs/5",
        {"json": {"x": 1}},
        id="nexsets.data_sets_update_catalog_ref_put",
    ),
    pytest.param(
        lambda c: c.nexsets.delete_catalog_ref_for_set(1, 5, hard_delete=True),
        "DELETE",
        "/data_sets/1/catalog_refs/5",
        {"params": {"hard_delete": 1}},
        id="nexsets.delete_catalog_ref_for_set",
    ),
    pytest.param(
        lambda c: c.nexsets.list_flow_accessors_via_data_set(1),
        "GET",
        "/data_sets/1/flow/accessors",
        {},
        id="nexsets.list_flow_accessors_via_data_set",
    ),
    pytest.param(
        lambda c: c.nexsets.reset_flow_accessors_via_data_set(1, {"accessors": []}),
        "POST",
        "/data_sets/1/flow/accessors",
        {"json": {"accessors": []}},
        id="nexsets.reset_flow_accessors_via_data_set",
    ),
    pytest.param(
        lambda c: c.nexsets.add_flow_accessors_via_data_set(1, {"accessors": []}),
        "PUT",
        "/data_sets/1/flow/accessors",
        {"json": {"accessors": []}},
        id="nexsets.add_flow_accessors_via_data_set",
    ),
    pytest.param(
        lambda c: c.nexsets.remove_flow_accessors_via_data_set(1, {"accessors": []}),
        "DELETE",
        "/data_sets/1/flow/accessors",
        {"json": {"accessors": []}},
        id="nexsets.remove_flow_accessors_via_data_set",
    ),
    pytest.param(
        lambda c: c.nexsets.activate_flow_via_data_set(1, all=True, run_now="x"),
        "PUT",
        "/data_sets/1/flow/activate",
        {"params": {"all": 1, "run_now": "x"}},
        id="nexsets.activate_flow_via_data_set",
    ),
    pytest.param(
        lambda c: c.nexsets.pause_flow_via_data_set(1, full_tree=True),
        "PUT",
        "/data_sets/1/flow/pause",
        {"params": {"full_tree": 1}},
        id="nexsets.pause_flow_via_data_set",
    ),
    pytest.param(
        lambda c: c.nexsets.data_sets_flow_audit_log(
            1, from_date="2026-01-01", page="2"
        ),
        "GET",
        "/data_sets/1/flow/audit_log",
        {"params": {"from": "2026-01-01", "page": "2"}},
        id="nexsets.data_sets_flow_audit_log",
    ),
    pytest.param(
        lambda c: c.nexsets.list_flow_docs_via_data_set(1),
        "GET",
        "/data_sets/1/flow/docs",
        {},
        id="nexsets.list_flow_docs_via_data_set",
    ),
    pytest.param(
        lambda c: c.nexsets.reset_flow_docs_via_data_set(1, {"docs": []}),
        "POST",
        "/data_sets/1/flow/docs",
        {"json": {"docs": []}},
        id="nexsets.reset_flow_docs_via_data_set",
    ),
    pytest.param(
        lambda c: c.nexsets.add_flow_docs_via_data_set(1, {"docs": []}),
        "PUT",
        "/data_sets/1/flow/docs",
        {"json": {"docs": []}},
        id="nexsets.add_flow_docs_via_data_set",
    ),
    pytest.param(
        lambda c: c.nexsets.remove_flow_docs_via_data_set(1, {"docs": [3]}),
        "DELETE",
        "/data_sets/1/flow/docs",
        {"json": {"docs": [3]}},
        id="nexsets.remove_flow_docs_via_data_set",
    ),
    pytest.param(
        lambda c: c.nexsets.data_sets_probe_read_quarantine_data_set(1, {"x": 1}),
        "PUT",
        "/data_sets/1/probe/quarantine/sample",
        {"json": {"x": 1}},
        id="nexsets.data_sets_probe_read_quarantine_data_set",
    ),
    pytest.param(
        lambda c: c.nexsets.data_sets_apply_transformation(
            1, transform_id=5, extract_schemas=True
        ),
        "PUT",
        "/data_sets/1/transform",
        {"params": {"transform_id": 5, "extract_schemas": 1}},
        id="nexsets.data_sets_apply_transformation",
    ),
    pytest.param(
        lambda c: c.nexsets.create_catalog_ref_for_set(4, {"name": "ref"}),
        "POST",
        "/data_sets/4/catalog_refs",
        {"json": {"name": "ref"}},
        id="nexsets.create_catalog_ref_for_set",
    ),
]


@pytest.mark.parametrize("call, method, path, expected", NEXSETS_ROUTE_CALLS)
def test_nexsets_route_sends_method_path_and_payload(
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
