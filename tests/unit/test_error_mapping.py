"""Error mapping: status code and body shape to typed NexlaError (spec section 5).

Transport tests patch the requests session. Nothing touches the network.
"""

import json
from unittest.mock import patch

import pytest
import requests

from nexla_sdk import (
    AccountLockedError,
    AuthenticationError,
    AuthorizationError,
    NexlaConnectionError,
    NexlaTimeoutError,
    NotFoundError,
    RateLimitError,
    ResourceConflictError,
    ServerError,
    ValidationError,
)
from nexla_sdk.client import NexlaClient
from nexla_sdk.exceptions import error_from_response
from nexla_sdk.http_client import HttpClientError, RequestsHttpClient

pytestmark = pytest.mark.unit


def _error_response(status, body=None, text=None, headers=None):
    resp = requests.Response()
    resp.status_code = status
    resp.reason = "Reason"
    resp.url = "https://api.test/nexla-api/v1/data_sources/1"
    if body is not None:
        resp._content = json.dumps(body).encode()
        resp.headers["Content-Type"] = "application/json"
    else:
        resp._content = (text or "").encode()
    resp.headers.update(headers or {})
    return resp


def _client_returning(resp):
    http = RequestsHttpClient(max_retries=0)  # no backoff sleeps in these tests
    client = NexlaClient(
        access_token="tok-1", base_url="https://api.test/nexla-api", http_client=http
    )
    return client, patch.object(http.session, "request", return_value=resp)


@pytest.mark.parametrize(
    "status, body, text, cls, message, error_code",
    [
        (
            400,
            {"message": "name is required"},
            None,
            ValidationError,
            "name is required",
            None,
        ),
        (
            422,
            {"detail": "per_page", "message": "Pagination value is out of range"},
            None,
            ValidationError,
            "Pagination value is out of range",
            None,
        ),
        (
            403,
            {"detail": "Not authorized", "message": "Forbidden"},
            None,
            AuthorizationError,
            "Forbidden",
            None,
        ),
        (404, {"detail": "Gone"}, None, NotFoundError, "Gone", None),
        (
            409,
            {"error_code": "duplicate_name", "message": "Name taken"},
            None,
            ResourceConflictError,
            "Name taken",
            "duplicate_name",
        ),
        (
            429,
            {
                "error": {
                    "type": "RateLimitExceeded",
                    "detail": "slow down",
                    "retry_after": 3,
                }
            },
            None,
            RateLimitError,
            "slow down",
            "RateLimitExceeded",
        ),
        (500, {"error": "boom text"}, None, ServerError, "boom text", None),
        (502, {"message": "bad gateway"}, None, ServerError, "bad gateway", None),
        (429, None, "Retry later\n", RateLimitError, "Retry later", None),
        (401, None, "", AuthenticationError, "401 Unauthorized", None),
        (404, None, "", NotFoundError, "404 Not Found", None),
        (400, None, "   ", ValidationError, "400 Bad Request", None),
        (503, {"unexpected": True}, None, ServerError, "503 Service Unavailable", None),
        (423, None, "", AccountLockedError, "423 Locked", None),
    ],
)
def test_status_and_body_shape_map_to_typed_error(
    status, body, text, cls, message, error_code
):
    err = error_from_response(
        status,
        body if body is not None else (text or None),
        headers={},
        method="GET",
        url="u",
    )
    assert type(err) is cls
    assert err.status_code == status
    assert err.status == status
    assert err.message == message
    assert err.error_code == error_code
    assert err.message  # never empty


def test_rate_limit_retry_after_is_read_from_error_body():
    err = error_from_response(
        429,
        {"error": {"type": "RateLimitExceeded", "detail": "x", "retry_after": 120}},
        headers={},
    )
    assert isinstance(err, RateLimitError)
    assert err.retry_after == 120


def test_account_locked_is_authentication_error():
    err = error_from_response(423, None, headers={})
    assert isinstance(err, AccountLockedError)
    assert isinstance(err, AuthenticationError)


def test_body_detail_is_kept_in_body():
    body = {"message": "Forbidden", "detail": "Not authorized to manage this Org"}
    err = error_from_response(403, body, headers={})
    assert err.body == body


def test_request_id_is_read_case_insensitively():
    err = error_from_response(404, None, headers={"x-request-id": "req-9"})
    assert err.request_id == "req-9"
    err = error_from_response(404, None, headers={"X-Request-Id": "req-10"})
    assert err.request_id == "req-10"


def test_method_and_url_are_recorded():
    err = error_from_response(
        500, {"message": "boom"}, headers={}, method="POST", url="https://x/y"
    )
    assert err.method == "POST"
    assert err.url == "https://x/y"


def test_transport_401_empty_body_raises_authentication_error_with_status():
    client, patcher = _client_returning(_error_response(401, text=""))
    with patcher, pytest.raises(AuthenticationError) as exc_info:
        client.sources.get(1)
    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "401 Unauthorized"


def test_transport_404_empty_body_keeps_request_id():
    resp = _error_response(404, text="", headers={"X-Request-Id": "req-123"})
    client, patcher = _client_returning(resp)
    with patcher, pytest.raises(NotFoundError) as exc_info:
        client.sources.get(1)
    assert exc_info.value.request_id == "req-123"
    assert exc_info.value.status_code == 404


def test_transport_text_plain_429_uses_trimmed_text():
    resp = _error_response(
        429, text="Retry later\n", headers={"Content-Type": "text/plain"}
    )
    client, patcher = _client_returning(resp)
    with patcher, pytest.raises(RateLimitError) as exc_info:
        client.sources.get(1)
    assert exc_info.value.message == "Retry later"


def test_transport_read_timeout_raises_nexla_timeout_error():
    http = RequestsHttpClient()
    client = NexlaClient(
        access_token="tok-1", base_url="https://api.test/nexla-api", http_client=http
    )
    with patch.object(
        http.session, "request", side_effect=requests.exceptions.ReadTimeout("slow")
    ):
        with pytest.raises(NexlaTimeoutError) as exc_info:
            client.sources.get(1)
    assert isinstance(exc_info.value, ServerError)


def test_transport_connect_timeout_is_timeout_not_connection_error():
    http = RequestsHttpClient()
    client = NexlaClient(
        access_token="tok-1", base_url="https://api.test/nexla-api", http_client=http
    )
    with patch.object(
        http.session, "request", side_effect=requests.exceptions.ConnectTimeout("slow")
    ):
        with pytest.raises(NexlaTimeoutError):
            client.sources.get(1)


def test_transport_connection_error_raises_nexla_connection_error():
    http = RequestsHttpClient()
    client = NexlaClient(
        access_token="tok-1", base_url="https://api.test/nexla-api", http_client=http
    )
    with patch.object(
        http.session, "request", side_effect=requests.exceptions.ConnectionError("down")
    ):
        with pytest.raises(NexlaConnectionError) as exc_info:
            client.sources.get(1)
    assert isinstance(exc_info.value, ServerError)


def test_http_client_error_carries_parsed_body_and_headers():
    err = HttpClientError("x", status_code=400, body={"message": "m"})
    assert err.body == {"message": "m"}
