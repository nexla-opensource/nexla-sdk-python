"""Request shape for the sdk_applications resource routes.

The resource adds no methods. Each row calls an inherited BaseResource method
and checks the HTTP verb and path it sends. The expected query params and JSON
body are checked where given (None means not checked).
"""

import pytest

pytestmark = pytest.mark.unit

SDK_APPLICATIONS_ROUTE_CALLS = [
    pytest.param(
        lambda c: c.sdk_applications.list(page=1, per_page=10),
        "GET",
        "/sdk_applications",
        {"page": 1, "per_page": 10},
        None,
        id="sdk_applications.list",
    ),
    pytest.param(
        lambda c: c.sdk_applications.create({"name": "app"}),
        "POST",
        "/sdk_applications",
        {},
        {"name": "app"},
        id="sdk_applications.create",
    ),
    pytest.param(
        lambda c: c.sdk_applications.get(1),
        "GET",
        "/sdk_applications/1",
        {},
        None,
        id="sdk_applications.get",
    ),
    pytest.param(
        lambda c: c.sdk_applications.update(1, {"name": "x"}),
        "PUT",
        "/sdk_applications/1",
        {},
        {"name": "x"},
        id="sdk_applications.update",
    ),
    pytest.param(
        lambda c: c.sdk_applications.delete(1),
        "DELETE",
        "/sdk_applications/1",
        {},
        None,
        id="sdk_applications.delete",
    ),
    pytest.param(
        lambda c: c.sdk_applications.activate(1),
        "PUT",
        "/sdk_applications/1/activate",
        {},
        None,
        id="sdk_applications.activate",
    ),
    pytest.param(
        lambda c: c.sdk_applications.pause(1),
        "PUT",
        "/sdk_applications/1/pause",
        {},
        None,
        id="sdk_applications.pause",
    ),
]


@pytest.mark.parametrize(
    "call, method, path, params, json_body", SDK_APPLICATIONS_ROUTE_CALLS
)
def test_sdk_applications_route_sends_expected_request(
    mock_client, mock_http_client, call, method, path, params, json_body
):
    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    assert last["params"] == params
    if json_body is not None:
        assert last["json"] == json_body
