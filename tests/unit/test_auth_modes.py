"""Authentication modes, org switch, and token sharing (spec section 2).

Uses the mock HTTP client. The concurrency test uses a thread-safe fake.
"""

import base64
import threading
import time

import pytest

from nexla_sdk import NexlaClient
from nexla_sdk.auth import TokenAuthHandler
from nexla_sdk.exceptions import NexlaError, ValidationError
from nexla_sdk.http_client import HttpClientInterface
from nexla_sdk.models.tokens.responses import TokenResponse
from tests.utils.fixtures import (
    MockHTTPClient,
    create_auth_token_response,
    create_http_error,
)

pytestmark = pytest.mark.unit

BASE = "https://api.test/nexla-api"


@pytest.fixture(autouse=True)
def _clear_credential_env(monkeypatch):
    for name in ("NEXLA_SERVICE_KEY", "NEXLA_API_KEY", "NEXLA_ACCESS_TOKEN"):
        monkeypatch.delenv(name, raising=False)


def _client(http, **kwargs):
    return NexlaClient(base_url=BASE, http_client=http, **kwargs)


def _token_requests(http):
    return [r for r in http.requests if r["url"].endswith("/token")]


def test_api_key_option_sends_basic_as_is():
    http = MockHTTPClient()
    http.add_response("/token", create_auth_token_response(access_token="tk-1"))
    client = _client(http, api_key="key-1")

    client.request("GET", "/data_sources/1")

    token_req = _token_requests(http)[0]
    assert token_req["method"] == "POST"
    assert token_req["headers"]["Authorization"] == "Basic key-1"


def test_api_key_from_env(monkeypatch):
    monkeypatch.setenv("NEXLA_API_KEY", "env-key")
    http = MockHTTPClient()
    http.add_response("/token", create_auth_token_response(access_token="tk-1"))

    _client(http).request("GET", "/data_sources/1")

    assert _token_requests(http)[0]["headers"]["Authorization"] == "Basic env-key"


def test_explicit_option_wins_over_env(monkeypatch):
    monkeypatch.setenv("NEXLA_SERVICE_KEY", "svc-env")
    http = MockHTTPClient()
    http.add_response("/token", create_auth_token_response(access_token="tk-1"))

    _client(http, api_key="key-1").request("GET", "/data_sources/1")

    assert _token_requests(http)[0]["headers"]["Authorization"] == "Basic key-1"


def test_password_login_sends_basic_email_password_org():
    http = MockHTTPClient()
    http.add_response("/token", create_auth_token_response(access_token="tk-1"))

    _client(http, email="dev@example.com", password="pw", org_id=3).request(
        "GET", "/data_sources/1"
    )

    expected = base64.b64encode(b"dev@example.com:pw:3").decode()
    assert expected == "ZGV2QGV4YW1wbGUuY29tOnB3OjM="
    assert _token_requests(http)[0]["headers"]["Authorization"] == f"Basic {expected}"


def test_password_login_without_org_omits_org_segment():
    http = MockHTTPClient()
    http.add_response("/token", create_auth_token_response(access_token="tk-1"))

    _client(http, email="dev@example.com", password="pw").request(
        "GET", "/data_sources/1"
    )

    expected = base64.b64encode(b"dev@example.com:pw").decode()
    assert _token_requests(http)[0]["headers"]["Authorization"] == f"Basic {expected}"


def test_more_than_one_credential_source_is_rejected():
    http = MockHTTPClient()
    with pytest.raises(NexlaError):
        NexlaClient(base_url=BASE, service_key="a", api_key="b", http_client=http)


def test_password_requires_email_and_password():
    http = MockHTTPClient()
    with pytest.raises(NexlaError):
        NexlaClient(base_url=BASE, email="dev@example.com", http_client=http)


def test_dataplane_header_is_sent_on_token_calls_only():
    http = MockHTTPClient()
    http.add_response("/token", create_auth_token_response(access_token="tk-1"))
    http.add_response("/data_sources/1", {"id": 1})

    _client(http, service_key="svc", dataplane="uid-1").request(
        "GET", "/data_sources/1"
    )

    assert _token_requests(http)[0]["headers"]["X-Nexla-Dataplane"] == "uid-1"
    assert "X-Nexla-Dataplane" not in http.get_last_request()["headers"]


def test_token_response_is_typed_and_keeps_unknown_fields():
    http = MockHTTPClient()
    http.add_response(
        "/token",
        {
            "access_token": "tk-1",
            "expires_in": 100,
            "user": {"id": 7},
            "org": {"id": 3, "name": "Acme"},
            "custom_field": "kept",
        },
    )
    client = _client(http, service_key="svc")

    client.get_access_token()

    tr = client.auth_handler.token_response
    assert isinstance(tr, TokenResponse)
    assert tr.access_token == "tk-1"
    assert tr.token_type == "Bearer"
    assert tr.expires_in == 100
    assert tr.org["id"] == 3
    assert tr.model_extra["custom_field"] == "kept"


def test_accept_header_is_application_json():
    http = MockHTTPClient()
    http.add_response("/token", create_auth_token_response(access_token="tk-1"))
    http.add_response("/data_sources/1", {"id": 1})
    client = _client(http, service_key="svc")

    client.request("GET", "/data_sources/1")

    for req in http.requests:
        assert req["headers"]["Accept"] == "application/json"


def test_switch_org_calls_refresh_with_org_id_and_replaces_token():
    http = MockHTTPClient()
    # /token/refresh must be registered before /token: the mock matches substrings.
    http.add_response("/token/refresh", create_auth_token_response(access_token="tk-2"))
    http.add_response("/token", create_auth_token_response(access_token="tk-1"))
    client = _client(http, service_key="svc")
    client.get_access_token()

    resp = client.switch_org(9)

    refresh = http.get_last_request()
    assert refresh["method"] == "POST"
    assert refresh["url"].endswith("/token/refresh")
    assert refresh["params"] == {"org_id": 9}
    assert refresh["headers"]["Authorization"] == "Bearer tk-1"
    assert resp.access_token == "tk-2"

    http.add_response("/data_sources/1", {"id": 1})
    client.request("GET", "/data_sources/1")
    assert http.get_last_request()["headers"]["Authorization"] == "Bearer tk-2"


def test_switch_org_maps_org_context_error():
    http = MockHTTPClient()
    # Register /token/refresh first: the mock matches substrings in insertion order.
    http.add_error("/token/refresh", create_http_error(400, "Org context is not set"))
    http.add_response("/token", create_auth_token_response(access_token="tk-1"))
    client = _client(http, service_key="svc")

    with pytest.raises(ValidationError) as exc_info:
        client.switch_org(9)
    assert exc_info.value.message == "Org context is not set"


class _SlowTokenHttp(HttpClientInterface):
    """Thread-safe fake. /token takes 0.2 s and counts calls."""

    def __init__(self):
        self.token_calls = 0
        self._lock = threading.Lock()

    def request(self, method, url, headers, **kwargs):
        assert url.endswith("/token")
        with self._lock:
            self.token_calls += 1
        time.sleep(0.2)
        return create_auth_token_response(access_token="tk-1")


def test_concurrent_callers_share_one_token_request():
    http = _SlowTokenHttp()
    auth = TokenAuthHandler(service_key="svc", base_url=BASE, http_client=http)
    barrier = threading.Barrier(8)
    results = []

    def worker():
        barrier.wait()
        results.append(auth.ensure_valid_token())

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert http.token_calls == 1
    assert results == ["tk-1"] * 8
