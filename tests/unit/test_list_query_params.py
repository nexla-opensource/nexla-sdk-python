"""Typed common list parameters and the AccessRole set (spec section 7)."""

import pytest

from nexla_sdk.models.enums import AccessRole, ResourceStatus
from tests.utils.mock_builders import MockResponseBuilder

pytestmark = pytest.mark.unit

# Backend AccessRoleQuery, lower-case form (app/api/v1/shared/schemas.py:45-72).
BACKEND_ACCESS_ROLES = {
    "admin",
    "admin_only",
    "all",
    "collaborator",
    "collaborator_only",
    "member",
    "operator",
    "owner",
    "owner_only",
    "sharer",
    "sharer_only",
}


def test_access_role_has_full_backend_set_and_keeps_existing_members():
    assert {role.value for role in AccessRole} == BACKEND_ACCESS_ROLES
    assert AccessRole.OWNER.value == "owner"
    assert AccessRole.ADMIN.value == "admin"
    assert AccessRole.OPERATOR.value == "operator"
    assert AccessRole.COLLABORATOR.value == "collaborator"


def test_list_sends_typed_params_with_wire_names(mock_client, mock_http_client):
    mock_http_client.add_response("/data_sources", [MockResponseBuilder.source()])

    mock_client.sources.list(
        expand=True,
        sort_by="created_at",
        sort_order="desc",
        status=ResourceStatus.ACTIVE,
        tags=["alpha", "beta"],
        name="orders",
        access_role=AccessRole.OWNER,
        from_date="2026-01-01",
        to_date="2026-02-01",
        org_id=3,
    )

    params = mock_http_client.get_last_request()["params"]
    assert params == {
        "expand": 1,
        "sort_by": "created_at",
        "sort_order": "desc",
        "status": "ACTIVE",
        "tags": "alpha,beta",
        "name": "orders",
        "access_role": "owner",
        "from": "2026-01-01",
        "to": "2026-02-01",
        "org_id": 3,
    }
    # The Python keyword names must not reach the wire.
    assert "from_date" not in params and "to_date" not in params


def test_access_role_enum_is_sent_as_plain_value(mock_client, mock_http_client):
    mock_http_client.add_response("/data_sources", [])

    mock_client.sources.list(access_role=AccessRole.SHARER_ONLY)

    value = mock_http_client.get_last_request()["params"]["access_role"]
    assert value == "sharer_only"
    assert type(value) is str


def test_unset_typed_params_are_not_sent(mock_client, mock_http_client):
    mock_http_client.add_response("/data_sources", [])

    mock_client.sources.list(page=2, per_page=5, expand=False)

    assert mock_http_client.get_last_request()["params"] == {"page": 2, "per_page": 5}


def test_tags_string_is_passed_through(mock_client, mock_http_client):
    mock_http_client.add_response("/data_sources", [])

    mock_client.sources.list(tags="alpha,beta")

    assert mock_http_client.get_last_request()["params"]["tags"] == "alpha,beta"


def test_unknown_kwargs_still_pass_through(mock_client, mock_http_client):
    mock_http_client.add_response("/data_sources", [])

    mock_client.sources.list(credentials_type="s3")

    assert mock_http_client.get_last_request()["params"] == {"credentials_type": "s3"}


def test_paginate_forwards_typed_params(mock_client, mock_http_client):
    mock_http_client.add_response("/data_sources", [])

    list(mock_client.sources.paginate(per_page=5, status="ACTIVE"))

    params = mock_http_client.get_last_request()["params"]
    assert params["status"] == "ACTIVE"
    assert params["per_page"] == 5
