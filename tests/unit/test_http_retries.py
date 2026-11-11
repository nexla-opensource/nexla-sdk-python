"""Retry and timeout behavior of RequestsHttpClient (spec sections 3-4).

Scripted wire: urllib3's socket-level request is replaced, so urllib3's Retry
and requests still run. time.sleep is recorded, not slept.
"""

import io
import json
import time
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import pytest
import requests
from urllib3.connectionpool import HTTPConnectionPool
from urllib3.exceptions import NewConnectionError, ReadTimeoutError
from urllib3.response import HTTPResponse

from nexla_sdk import (
    NexlaClient,
    NexlaTimeoutError,
    RateLimitError,
    ServerError,
)
from nexla_sdk.exceptions import AuthenticationError

pytestmark = pytest.mark.unit

BASE = "https://api.test/nexla-api"


class ScriptedWire:
    """Serves scripted responses at the urllib3 connection layer and records sleeps."""

    def __init__(self, monkeypatch, steps):
        self.steps = list(steps)
        self.calls = []
        self.sleeps = []
        monkeypatch.setattr(HTTPConnectionPool, "_make_request", self._make_request)
        monkeypatch.setattr(time, "sleep", self.sleeps.append)

    def _make_request(self, conn, method, url, body=None, headers=None, **kwargs):
        self.calls.append({"method": method, "url": url, "body": body})
        step = self.steps.pop(0)
        if isinstance(step, BaseException):
            raise step
        status, hdrs, payload = step
        if payload is None:
            data = b""
        elif isinstance(payload, str):
            data = payload.encode()
        else:
            data = json.dumps(payload).encode()
        return HTTPResponse(
            body=io.BytesIO(data),
            headers=hdrs,
            status=status,
            preload_content=False,
            decode_content=False,
            original_response=None,
            request_method=method,
            request_url=url,
        )


def _client(**kwargs):
    kwargs.setdefault("max_retries", 3)
    return NexlaClient(access_token="tok-1", base_url=BASE, **kwargs)


def _json_ok(body=None):
    return (200, {"Content-Type": "application/json"}, body or {"id": 1})


def _backoff_ok(sleep_value, attempt):
    """Spec backoff before attempt n: min(8, 0.5 * 2^(n-1)) + 0-100 ms."""
    base = min(8.0, 0.5 * 2 ** (attempt - 1))
    assert base <= sleep_value < base + 0.1 + 1e-9


def test_get_503_is_retried_then_succeeds(monkeypatch):
    wire = ScriptedWire(
        monkeypatch, [(503, {}, {"message": "unavailable"}), _json_ok()]
    )
    client = _client()

    assert client.request("GET", "/data_sources/1") == {"id": 1}
    assert len(wire.calls) == 2
    _backoff_ok(wire.sleeps[0], 1)


def test_post_503_is_not_retried(monkeypatch):
    wire = ScriptedWire(monkeypatch, [(503, {}, {"message": "unavailable"})])

    with pytest.raises(ServerError) as exc_info:
        _client().request("POST", "/data_sources", json={"name": "s"})

    assert exc_info.value.message == "unavailable"
    assert len(wire.calls) == 1
    assert wire.sleeps == []


def test_post_connect_error_is_retried(monkeypatch):
    """Connect errors happen before the request is sent, so every method may retry."""
    wire = ScriptedWire(
        monkeypatch,
        [NewConnectionError(None, "refused"), (201, {}, {"id": 9})],
    )

    result = _client().request("POST", "/data_sources", json={"name": "s"})

    assert result == {"id": 9}
    assert len(wire.calls) == 2


def test_post_read_timeout_is_not_retried(monkeypatch):
    wire = ScriptedWire(monkeypatch, [ReadTimeoutError(None, BASE, "read timed out")])

    with pytest.raises(NexlaTimeoutError):
        _client().request("POST", "/data_sources", json={"name": "s"})

    assert len(wire.calls) == 1


def test_get_read_timeout_is_retried(monkeypatch):
    wire = ScriptedWire(
        monkeypatch, [ReadTimeoutError(None, BASE, "read timed out"), _json_ok()]
    )

    assert _client().request("GET", "/data_sources/1") == {"id": 1}
    assert len(wire.calls) == 2


def test_get_read_timeouts_exhausted_raise_nexla_timeout(monkeypatch):
    ScriptedWire(
        monkeypatch,
        [ReadTimeoutError(None, BASE, "t")] * 2,
    )

    with pytest.raises(NexlaTimeoutError):
        _client(max_retries=1).request("GET", "/data_sources/1")


def test_429_post_retried_with_body_retry_after_and_same_body(monkeypatch):
    wire = ScriptedWire(
        monkeypatch,
        [
            (
                429,
                {},
                {
                    "error": {
                        "type": "RateLimitExceeded",
                        "detail": "slow",
                        "retry_after": 1,
                    }
                },
            ),
            (201, {}, {"id": 9}),
        ],
    )

    result = _client().request("POST", "/data_sources", json={"name": "s"})

    assert result == {"id": 9}
    assert wire.sleeps == [1.0]
    assert len(wire.calls) == 2
    assert wire.calls[0]["body"] == wire.calls[1]["body"]


def test_429_retry_after_over_60_seconds_is_not_retried(monkeypatch):
    wire = ScriptedWire(
        monkeypatch,
        [
            (
                429,
                {},
                {
                    "error": {
                        "type": "RateLimitExceeded",
                        "detail": "Rate limit exceeded.",
                        "retry_after": 120,
                    }
                },
            )
        ],
    )

    with pytest.raises(RateLimitError) as exc_info:
        _client().request("GET", "/data_sources/1")

    assert exc_info.value.retry_after == 120
    assert len(wire.calls) == 1
    assert wire.sleeps == []


def test_429_retry_after_header_seconds_is_used(monkeypatch):
    wire = ScriptedWire(monkeypatch, [(429, {"Retry-After": "2"}, None), _json_ok()])

    _client().request("GET", "/data_sources/1")

    assert wire.sleeps == [2.0]


def test_429_retry_after_http_date_is_used(monkeypatch):
    when = datetime.now(timezone.utc) + timedelta(seconds=30)
    wire = ScriptedWire(
        monkeypatch,
        [(429, {"Retry-After": format_datetime(when, usegmt=True)}, None), _json_ok()],
    )

    _client().request("GET", "/data_sources/1")

    assert len(wire.sleeps) == 1
    assert 25 < wire.sleeps[0] <= 30


def test_429_without_hint_uses_backoff(monkeypatch):
    wire = ScriptedWire(monkeypatch, [(429, {}, None), _json_ok()])

    _client().request("GET", "/data_sources/1")

    assert len(wire.sleeps) == 1
    _backoff_ok(wire.sleeps[0], 1)


def test_429_text_body_with_max_retries_zero_raises_without_retry(monkeypatch):
    wire = ScriptedWire(
        monkeypatch, [(429, {"Content-Type": "text/plain"}, "Retry later\n")]
    )

    with pytest.raises(RateLimitError) as exc_info:
        _client(max_retries=0).request("GET", "/data_sources/1")

    assert exc_info.value.message == "Retry later"
    assert len(wire.calls) == 1


def test_exhausted_503_retries_raise_after_max_retries(monkeypatch):
    wire = ScriptedWire(monkeypatch, [(503, {}, {"message": "down"})] * 3)

    with pytest.raises(ServerError):
        _client(max_retries=2).request("GET", "/data_sources/1")

    assert len(wire.calls) == 3
    _backoff_ok(wire.sleeps[0], 1)
    _backoff_ok(wire.sleeps[1], 2)


def test_backoff_is_capped_at_8_seconds(monkeypatch):
    wire = ScriptedWire(monkeypatch, [(503, {}, {"message": "down"})] * 9)

    with pytest.raises(ServerError):
        _client(max_retries=8).request("GET", "/data_sources/1")

    assert len(wire.sleeps) == 8
    for n, value in enumerate(wire.sleeps, start=1):
        _backoff_ok(value, n)
    assert wire.sleeps[-1] >= 8.0


def test_default_timeout_is_connect_10_read_60(monkeypatch):
    client = _client()
    assert client.http_client.timeout == (10.0, 60.0)

    seen = {}

    def fake_request(method, url, **kwargs):
        seen.update(kwargs)
        resp = requests.Response()
        resp.status_code = 200
        resp.headers["Content-Type"] = "application/json"
        resp._content = b'{"id": 1}'
        return resp

    monkeypatch.setattr(client.http_client.session, "request", fake_request)
    client.request("GET", "/data_sources/1")
    assert seen["timeout"] == (10.0, 60.0)


def test_float_timeout_sets_connect_and_read():
    assert _client(timeout=5).http_client.timeout == (5.0, 5.0)
    assert _client(timeout=(3, 30)).http_client.timeout == (3, 30)


def test_retry_methods_option_allows_post_status_retry(monkeypatch):
    wire = ScriptedWire(
        monkeypatch, [(503, {}, {"message": "x"}), (201, {}, {"id": 2})]
    )

    result = _client(retry_methods=["GET", "POST"]).request(
        "POST", "/data_sources", json={"name": "s"}
    )

    assert result == {"id": 2}
    assert len(wire.calls) == 2


def test_token_post_is_retried_on_429(monkeypatch):
    wire = ScriptedWire(
        monkeypatch,
        [
            (
                429,
                {},
                {
                    "error": {
                        "type": "RateLimitExceeded",
                        "detail": "x",
                        "retry_after": 0,
                    }
                },
            ),
            (200, {}, {"access_token": "tok-2", "expires_in": 86400}),
            _json_ok(),
        ],
    )
    client = NexlaClient(service_key="svc", base_url=BASE, max_retries=3)

    assert client.request("GET", "/data_sources/1") == {"id": 1}
    assert [c["url"].split("/nexla-api")[1] for c in wire.calls] == [
        "/token",
        "/token",
        "/data_sources/1",
    ]


def test_token_post_is_not_retried_on_503(monkeypatch):
    wire = ScriptedWire(monkeypatch, [(503, {}, {"message": "down"})])
    client = NexlaClient(service_key="svc", base_url=BASE, max_retries=3)

    with pytest.raises(ServerError):
        client.request("GET", "/data_sources/1")

    assert len(wire.calls) == 1
    assert wire.calls[0]["url"].endswith("/token")


def test_auth_error_is_not_retried_on_401(monkeypatch):
    wire = ScriptedWire(monkeypatch, [(401, {}, None)])

    with pytest.raises(AuthenticationError):
        _client().request("GET", "/data_sources/1")

    assert len(wire.calls) == 1
