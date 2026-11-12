"""Unit tests for resources that had no dedicated test module.

Covers every public method of dashboard_transforms, org_tiers, user_tiers,
resource_parameters, flow_nodes, catalog_configs and search_health. Also covers
the data_credentials_groups and custom_data_flows methods that the existing
route tests do not reach.
"""

import pytest

from nexla_sdk.models.catalog_configs.responses import CatalogConfig
from nexla_sdk.models.common import FlowNode
from nexla_sdk.models.credentials.responses import Credential
from nexla_sdk.models.custom_data_flows.responses import CustomDataFlow
from nexla_sdk.models.dashboard_transforms.responses import DashboardTransform
from nexla_sdk.models.org_tiers.responses import OrgTier
from nexla_sdk.models.user_tiers.responses import UserTier

# (call, method, path, expected request fields, response body)
ROUTE_CASES = [
    # dashboard_transforms
    pytest.param(
        lambda c: c.dashboard_transforms.list(),
        "GET",
        "/dashboard_transforms",
        {},
        [{"id": 1}],
        id="dashboard_transforms.list",
    ),
    pytest.param(
        lambda c: c.dashboard_transforms.list_all(page=2),
        "GET",
        "/dashboard_transforms/all",
        {"params": {"page": 2}},
        [{"id": 1}],
        id="dashboard_transforms.list_all",
    ),
    pytest.param(
        lambda c: c.dashboard_transforms.get(5),
        "GET",
        "/dashboard_transforms/5",
        {},
        {"id": 5},
        id="dashboard_transforms.get",
    ),
    pytest.param(
        lambda c: c.dashboard_transforms.create({"code_container_id": 3}),
        "POST",
        "/dashboard_transforms",
        {"json": {"code_container_id": 3}},
        {"id": 6},
        id="dashboard_transforms.create",
    ),
    pytest.param(
        lambda c: c.dashboard_transforms.update(5, {"code_container_id": 4}),
        "PUT",
        "/dashboard_transforms/5",
        {"json": {"code_container_id": 4}},
        {"id": 5},
        id="dashboard_transforms.update",
    ),
    pytest.param(
        lambda c: c.dashboard_transforms.delete(5),
        "DELETE",
        "/dashboard_transforms/5",
        {},
        {"status": "ok"},
        id="dashboard_transforms.delete",
    ),
    # org_tiers
    pytest.param(
        lambda c: c.org_tiers.list(),
        "GET",
        "/org_tiers",
        {},
        [{"id": 1}],
        id="org_tiers.list",
    ),
    pytest.param(
        lambda c: c.org_tiers.get(2),
        "GET",
        "/org_tiers/2",
        {},
        {"id": 2},
        id="org_tiers.get",
    ),
    pytest.param(
        lambda c: c.org_tiers.create({"name": "gold"}),
        "POST",
        "/org_tiers",
        {"json": {"name": "gold"}},
        {"id": 3},
        id="org_tiers.create",
    ),
    pytest.param(
        lambda c: c.org_tiers.update(2, {"name": "silver"}),
        "PUT",
        "/org_tiers/2",
        {"json": {"name": "silver"}},
        {"id": 2},
        id="org_tiers.update",
    ),
    pytest.param(
        lambda c: c.org_tiers.delete(2),
        "DELETE",
        "/org_tiers/2",
        {},
        {"status": "ok"},
        id="org_tiers.delete",
    ),
    # user_tiers
    pytest.param(
        lambda c: c.user_tiers.list(),
        "GET",
        "/user_tiers",
        {},
        [{"id": 1}],
        id="user_tiers.list",
    ),
    pytest.param(
        lambda c: c.user_tiers.get(4),
        "GET",
        "/user_tiers/4",
        {},
        {"id": 4},
        id="user_tiers.get",
    ),
    pytest.param(
        lambda c: c.user_tiers.create({"name": "pro"}),
        "POST",
        "/user_tiers",
        {"json": {"name": "pro"}},
        {"id": 5},
        id="user_tiers.create",
    ),
    pytest.param(
        lambda c: c.user_tiers.update(4, {"name": "basic"}),
        "PUT",
        "/user_tiers/4",
        {"json": {"name": "basic"}},
        {"id": 4},
        id="user_tiers.update",
    ),
    pytest.param(
        lambda c: c.user_tiers.delete(4),
        "DELETE",
        "/user_tiers/4",
        {},
        {"status": "ok"},
        id="user_tiers.delete",
    ),
    # resource_parameters
    pytest.param(
        lambda c: c.resource_parameters.list(),
        "GET",
        "/resource_parameters",
        {},
        [{"id": 1}],
        id="resource_parameters.list",
    ),
    pytest.param(
        lambda c: c.resource_parameters.get(3),
        "GET",
        "/resource_parameters/3",
        {},
        {"id": 3},
        id="resource_parameters.get",
    ),
    pytest.param(
        lambda c: c.resource_parameters.create({"name": "region"}),
        "POST",
        "/resource_parameters",
        {"json": {"name": "region"}},
        {"id": 8},
        id="resource_parameters.create",
    ),
    pytest.param(
        lambda c: c.resource_parameters.update(3, {"display_name": "Region"}),
        "PUT",
        "/resource_parameters/3",
        {"json": {"display_name": "Region"}},
        {"id": 3},
        id="resource_parameters.update",
    ),
    pytest.param(
        lambda c: c.resource_parameters.delete(3),
        "DELETE",
        "/resource_parameters/3",
        {},
        {"status": "ok"},
        id="resource_parameters.delete",
    ),
    # flow_nodes
    pytest.param(
        lambda c: c.flow_nodes.get(7),
        "GET",
        "/flow_nodes/7",
        {},
        {"id": 7, "origin_node_id": 1},
        id="flow_nodes.get",
    ),
    pytest.param(
        lambda c: c.flow_nodes.update(7, {"name": "renamed"}),
        "PUT",
        "/flow_nodes/7",
        {"json": {"name": "renamed"}},
        {"id": 7, "origin_node_id": 1},
        id="flow_nodes.update",
    ),
    pytest.param(
        lambda c: c.flow_nodes.list_origin_nodes_condensed(page=1),
        "GET",
        "/flows/all/condensed",
        {"params": {"page": 1}},
        {"nodes": []},
        id="flow_nodes.list_origin_nodes_condensed",
    ),
    pytest.param(
        lambda c: c.flow_nodes.list_flows_minimal(),
        "GET",
        "/flows/all/minimal",
        {},
        {"flows": []},
        id="flow_nodes.list_flows_minimal",
    ),
    pytest.param(
        lambda c: c.flow_nodes.get_access_insights(7, per_page=5),
        "GET",
        "/flows/7/access",
        {"params": {"per_page": 5}},
        {"insights": []},
        id="flow_nodes.get_access_insights",
    ),
    # catalog_configs
    pytest.param(
        lambda c: c.catalog_configs.list(),
        "GET",
        "/catalog_configs",
        {},
        [{"id": 9}],
        id="catalog_configs.list",
    ),
    pytest.param(
        lambda c: c.catalog_configs.list_all(per_page=50),
        "GET",
        "/catalog_configs/all",
        {"params": {"per_page": 50}},
        [{"id": 9}],
        id="catalog_configs.list_all",
    ),
    pytest.param(
        lambda c: c.catalog_configs.get(9),
        "GET",
        "/catalog_configs/9",
        {},
        {"id": 9},
        id="catalog_configs.get",
    ),
    pytest.param(
        lambda c: c.catalog_configs.create({"name": "c"}),
        "POST",
        "/catalog_configs",
        {"json": {"name": "c"}},
        {"id": 10},
        id="catalog_configs.create",
    ),
    pytest.param(
        lambda c: c.catalog_configs.update(9, {"name": "d"}),
        "PUT",
        "/catalog_configs/9",
        {"json": {"name": "d"}},
        {"id": 9},
        id="catalog_configs.update",
    ),
    pytest.param(
        lambda c: c.catalog_configs.delete(9),
        "DELETE",
        "/catalog_configs/9",
        {},
        {"status": "ok"},
        id="catalog_configs.delete",
    ),
    pytest.param(
        lambda c: c.catalog_configs.mock_catalog_add({"a": 1}),
        "POST",
        "/mock_catalog_add",
        {"json": {"a": 1}},
        {"status": "ok"},
        id="catalog_configs.mock_catalog_add",
    ),
    pytest.param(
        lambda c: c.catalog_configs.check_job_status(9),
        "GET",
        "/catalog_configs/9/check_job_status",
        {},
        {"status": "done"},
        id="catalog_configs.check_job_status",
    ),
    pytest.param(
        lambda c: c.catalog_configs.start_bulk_create_update(9),
        "GET",
        "/catalog_configs/9/bulk_create_update_refs",
        {},
        {"status": "started"},
        id="catalog_configs.start_bulk_create_update",
    ),
    # search_health
    pytest.param(
        lambda c: c.search_health.get(),
        "GET",
        "/search_health",
        {},
        {"healthy": True},
        id="search_health.get",
    ),
    pytest.param(
        lambda c: c.search_health.test(),
        "GET",
        "/search_health/test",
        {},
        {"healthy": True},
        id="search_health.test",
    ),
    # data_credentials_groups (routes not covered elsewhere)
    pytest.param(
        lambda c: c.data_credentials_groups.list_credentials(4, page=1),
        "GET",
        "/data_credentials_groups/4/data_credentials",
        {"params": {"page": 1}},
        [{"id": 1, "name": "c", "credentials_type": "s3"}],
        id="data_credentials_groups.list_credentials",
    ),
    pytest.param(
        lambda c: c.data_credentials_groups.remove_credentials(
            4, {"data_credentials": [1]}
        ),
        "DELETE",
        "/data_credentials_groups/4/data_credentials",
        {"json": {"data_credentials": [1]}},
        {"status": "ok"},
        id="data_credentials_groups.remove_credentials",
    ),
    pytest.param(
        lambda c: c.data_credentials_groups.get(4, expand=True),
        "GET",
        "/data_credentials_groups/4",
        {"params": {"expand": 1}},
        {"id": 4},
        id="data_credentials_groups.get",
    ),
    pytest.param(
        lambda c: c.data_credentials_groups.create({"name": "g"}),
        "POST",
        "/data_credentials_groups",
        {"json": {"name": "g"}},
        {"id": 11},
        id="data_credentials_groups.create",
    ),
    pytest.param(
        lambda c: c.data_credentials_groups.update(4, {"name": "h"}),
        "PUT",
        "/data_credentials_groups/4",
        {"json": {"name": "h"}},
        {"id": 4},
        id="data_credentials_groups.update",
    ),
    pytest.param(
        lambda c: c.data_credentials_groups.delete(4),
        "DELETE",
        "/data_credentials_groups/4",
        {},
        {"status": "ok"},
        id="data_credentials_groups.delete",
    ),
    pytest.param(
        lambda c: c.data_credentials_groups.data_credentials_groups_update_data_credentials_group(
            4, {"name": "r"}
        ),
        "PATCH",
        "/data_credentials_groups/4",
        {"json": {"name": "r"}},
        {"id": 4},
        id="data_credentials_groups.patch_group",
    ),
    # custom_data_flows (routes not covered elsewhere)
    pytest.param(
        lambda c: c.custom_data_flows.list_accessible(page=1),
        "GET",
        "/custom_data_flows/accessible",
        {"params": {"page": 1}},
        [{"id": 1}],
        id="custom_data_flows.list_accessible",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.get(3, expand=True),
        "GET",
        "/custom_data_flows/3",
        {"params": {"expand": 1}},
        {"id": 3},
        id="custom_data_flows.get",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.copy(3, {"name": "x"}),
        "POST",
        "/custom_data_flows/3/copy",
        {"json": {"name": "x"}},
        {"id": 4},
        id="custom_data_flows.copy",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.activate(3),
        "PUT",
        "/custom_data_flows/3/activate",
        {},
        {"id": 3},
        id="custom_data_flows.activate",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.activate(3, activate=False),
        "PUT",
        "/custom_data_flows/3/pause",
        {},
        {"id": 3},
        id="custom_data_flows.pause",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.get_metrics(3, period="day"),
        "GET",
        "/custom_data_flows/3/metrics",
        {"params": {"period": "day"}},
        {"rows": 1},
        id="custom_data_flows.get_metrics",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.search({"name": "x"}),
        "POST",
        "/custom_data_flows/search",
        {"json": {"name": "x"}},
        [{"id": 1}],
        id="custom_data_flows.search",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.search_tags(["a"]),
        "POST",
        "/custom_data_flows/search_tags",
        {"json": ["a"]},
        [{"id": 1}],
        id="custom_data_flows.search_tags",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.custom_data_flows_update_custom_data_flow(
            3, {"name": "y"}
        ),
        "PATCH",
        "/custom_data_flows/3",
        {"json": {"name": "y"}},
        {"id": 3},
        id="custom_data_flows.patch",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.get_custom_data_flow_metrics_by_name(
            3, "summary"
        ),
        "GET",
        "/custom_data_flows/3/metrics/summary",
        {},
        {"rows": 1},
        id="custom_data_flows.get_metrics_by_name",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.list(),
        "GET",
        "/custom_data_flows",
        {},
        [{"id": 1}],
        id="custom_data_flows.list",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.create({"name": "n"}),
        "POST",
        "/custom_data_flows",
        {"json": {"name": "n"}},
        {"id": 2},
        id="custom_data_flows.create",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.update(3, {"name": "m"}),
        "PUT",
        "/custom_data_flows/3",
        {"json": {"name": "m"}},
        {"id": 3},
        id="custom_data_flows.update",
    ),
    pytest.param(
        lambda c: c.data_credentials_groups.list(page=2),
        "GET",
        "/data_credentials_groups",
        {"params": {"page": 2}},
        [{"id": 1}],
        id="data_credentials_groups.list",
    ),
    pytest.param(
        lambda c: c.custom_data_flows.delete(3),
        "DELETE",
        "/custom_data_flows/3",
        {},
        {"status": "ok"},
        id="custom_data_flows.delete",
    ),
]


@pytest.mark.parametrize("call, method, path, expected, response", ROUTE_CASES)
def test_route_sends_expected_request(
    mock_client, mock_http_client, call, method, path, expected, response
):
    mock_http_client.add_response(path, response)

    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    for key, value in expected.items():
        assert last[key] == value


@pytest.mark.parametrize(
    "mode, method",
    [
        ("list", "GET"),
        ("reset", "POST"),
        ("add", "PUT"),
        ("remove", "DELETE"),
        ("unknown", "GET"),
    ],
)
@pytest.mark.parametrize(
    "resource_call, path",
    [
        ("edit_code_containers", "/custom_data_flows/3/code_containers"),
        ("edit_data_credentials", "/custom_data_flows/3/data_credentials"),
    ],
)
def test_edit_modes_map_to_http_methods(
    mock_client, mock_http_client, resource_call, path, mode, method
):
    mock_http_client.add_response(path, {"status": "ok"})

    getattr(mock_client.custom_data_flows, resource_call)(3, {"ids": [1]}, mode)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    assert last["json"] == {"ids": [1]}


def test_dashboard_transform_get_returns_model(mock_client, mock_http_client):
    mock_http_client.add_response("/dashboard_transforms/5", {"id": 5})

    result = mock_client.dashboard_transforms.get(5)

    assert isinstance(result, DashboardTransform)
    assert result.id == 5


def test_org_tiers_list_returns_models(mock_client, mock_http_client):
    mock_http_client.add_response("/org_tiers", [{"id": 1}, {"id": 2}])

    result = mock_client.org_tiers.list()

    assert [type(t) for t in result] == [OrgTier, OrgTier]


def test_user_tiers_get_returns_model(mock_client, mock_http_client):
    mock_http_client.add_response("/user_tiers/4", {"id": 4})

    result = mock_client.user_tiers.get(4)

    assert isinstance(result, UserTier)


def test_flow_node_get_returns_model(mock_client, mock_http_client):
    mock_http_client.add_response("/flow_nodes/7", {"id": 7, "origin_node_id": 1})

    result = mock_client.flow_nodes.get(7)

    assert isinstance(result, FlowNode)
    assert result.origin_node_id == 1


def test_catalog_configs_list_all_returns_models(mock_client, mock_http_client):
    mock_http_client.add_response("/catalog_configs/all", [{"id": 9}])

    result = mock_client.catalog_configs.list_all()

    assert [type(c) for c in result] == [CatalogConfig]


def test_list_credentials_returns_credential_models(mock_client, mock_http_client):
    mock_http_client.add_response(
        "/data_credentials_groups/4/data_credentials",
        [{"id": 1, "name": "c", "credentials_type": "s3"}],
    )

    result = mock_client.data_credentials_groups.list_credentials(4)

    assert [type(c) for c in result] == [Credential]


def test_custom_data_flow_search_returns_models(mock_client, mock_http_client):
    mock_http_client.add_response("/custom_data_flows/search", [{"id": 1}])

    result = mock_client.custom_data_flows.search({"name": "x"})

    assert [type(f) for f in result] == [CustomDataFlow]


def test_search_health_get_returns_raw_body(mock_client, mock_http_client):
    mock_http_client.add_response("/search_health", {"healthy": True})

    assert mock_client.search_health.get() == {"healthy": True}
