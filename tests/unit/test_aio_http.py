"""Async transport retry and error rules (spec sections 3-5). No network.

httpx.MockTransport replaces the socket layer. asyncio.sleep is recorded, not slept.
"""

import asyncio
from types import SimpleNamespace

import httpx
import pytest

from nexla_sdk.aio import http_client as aio_http
from nexla_sdk.aio.http_client import AsyncHttpxClient
from nexla_sdk.transport_core import (
    HttpClientError,
    HttpConnectionError,
    HttpTimeoutError,
)

pytestmark = pytest.mark.unit

URL = "https://api.test/nexla-api/data_sources/1"


class Wire:
    """Serves scripted steps in order. A step is (status, headers, payload) or an exception."""

    def __init__(self, monkeypatch, steps):
        self.steps = list(steps)
        self.calls = []
        self.sleeps = []

        async def fake_sleep(delay):
            self.sleeps.append(delay)

        monkeypatch.setattr(aio_http, "asyncio", SimpleNamespace(sleep=fake_sleep))

    def handler(self, request):
        self.calls.append(request.method)
        if not self.steps:
            raise AssertionError(f"Unexpected request: {request.method} {request.url}")
        step = self.steps.pop(0)
        if isinstance(step, BaseException):
            raise step
        status, headers, payload = step
        if payload is None:
            return httpx.Response(status, headers=headers)
        if isinstance(payload, str):
            return httpx.Response(status, headers=headers, content=payload.encode())
        return httpx.Response(status, headers=headers, json=payload)


def _client(wire, **kwargs):
    return AsyncHttpxClient(transport=httpx.MockTransport(wire.handler), **kwargs)


def _run(coro):
    return asyncio.run(coro)


async def _send(client, method, body=None):
    return await client.request_with_headers(
        method, URL, {"Accept": "application/json"}, json=body
    )


def _json_ok():
    return (200, {"Content-Type": "application/json"}, {"id": 1})


def _backoff_ok(sleep_value, attempt):
    base = min(8.0, 0.5 * 2 ** (attempt - 1))
    assert base <= sleep_value < base + 0.1 + 1e-9


def test_get_503_is_retried_then_succeeds(monkeypatch):
    wire = Wire(monkeypatch, [(503, {}, {"message": "down"}), _json_ok()])

    body, headers = _run(_send(_client(wire), "GET"))

    assert body == {"id": 1}
    assert wire.calls == ["GET", "GET"]
    _backoff_ok(wire.sleeps[0], 1)
    assert headers["content-type"] == "application/json"


def test_get_503_backoff_grows_then_gives_up(monkeypatch):
    wire = Wire(monkeypatch, [(503, {}, {"message": "down"})] * 4)

    with pytest.raises(HttpClientError) as exc_info:
        _run(_send(_client(wire), "GET"))

    assert exc_info.value.status_code == 503
    assert len(wire.calls) == 4  # first attempt plus max_retries (3)
    for n, delay in enumerate(wire.sleeps, start=1):
        _backoff_ok(delay, n)


def test_post_503_is_not_retried(monkeypatch):
    wire = Wire(monkeypatch, [(503, {}, {"message": "down"})])

    with pytest.raises(HttpClientError) as exc_info:
        _run(_send(_client(wire), "POST", {"name": "s"}))

    assert exc_info.value.status_code == 503
    assert wire.calls == ["POST"]
    assert wire.sleeps == []


def test_429_retry_after_from_body_is_honored(monkeypatch):
    rate = {"error": {"type": "rate", "detail": "slow down", "retry_after": 2}}
    wire = Wire(monkeypatch, [(429, {}, rate), _json_ok()])

    body, _ = _run(_send(_client(wire), "POST", {"name": "s"}))

    assert body == {"id": 1}
    assert wire.calls == ["POST", "POST"]  # 429 is retried for every method
    assert wire.sleeps == [2]


def test_429_over_60_seconds_is_returned_not_retried(monkeypatch):
    rate = {"error": {"type": "rate", "detail": "later", "retry_after": 61}}
    wire = Wire(monkeypatch, [(429, {}, rate)])

    with pytest.raises(HttpClientError) as exc_info:
        _run(_send(_client(wire), "GET"))

    assert exc_info.value.status_code == 429
    assert wire.calls == ["GET"]
    assert wire.sleeps == []


def test_429_retries_are_capped_at_max_retries(monkeypatch):
    rate = {"error": {"type": "rate", "detail": "slow", "retry_after": 1}}
    wire = Wire(monkeypatch, [(429, {}, rate)] * 5)

    with pytest.raises(HttpClientError):
        _run(_send(_client(wire), "GET"))

    assert len(wire.calls) == 4
    assert wire.sleeps == [1, 1, 1]


def test_read_timeout_on_post_is_not_retried(monkeypatch):
    wire = Wire(monkeypatch, [httpx.ReadTimeout("slow")])

    with pytest.raises(HttpTimeoutError):
        _run(_send(_client(wire), "POST", {"name": "s"}))

    assert wire.calls == ["POST"]


def test_timeout_without_message_names_the_exception(monkeypatch):
    wire = Wire(monkeypatch, [httpx.ReadTimeout("")])

    with pytest.raises(HttpTimeoutError) as exc_info:
        _run(_send(_client(wire), "POST", {"name": "s"}))

    assert "ReadTimeout" in str(exc_info.value)


def test_read_timeout_on_get_is_retried(monkeypatch):
    wire = Wire(monkeypatch, [httpx.ReadTimeout("slow"), _json_ok()])

    body, _ = _run(_send(_client(wire), "GET"))

    assert body == {"id": 1}
    assert len(wire.calls) == 2


def test_connect_timeout_on_post_is_retried(monkeypatch):
    # The request was never sent, so every method is safe to retry.
    wire = Wire(monkeypatch, [httpx.ConnectTimeout("connect"), _json_ok()])

    body, _ = _run(_send(_client(wire), "POST", {"name": "s"}))

    assert body == {"id": 1}
    assert wire.calls == ["POST", "POST"]


def test_connection_refused_is_retried_then_raised(monkeypatch):
    refused = httpx.ConnectError("[Errno 61] Connection refused")
    wire = Wire(monkeypatch, [refused] * 4)

    with pytest.raises(HttpConnectionError):
        _run(_send(_client(wire), "GET"))

    assert len(wire.calls) == 4


def test_max_retries_zero_sends_once(monkeypatch):
    wire = Wire(monkeypatch, [(503, {}, {"message": "down"})])

    with pytest.raises(HttpClientError):
        _run(_send(_client(wire, max_retries=0), "GET"))

    assert len(wire.calls) == 1


def test_timeout_pair_is_applied(monkeypatch):
    seen = {}

    def handler(request):
        seen["timeout"] = request.extensions["timeout"]
        return httpx.Response(200, json={"id": 1})

    client = AsyncHttpxClient(timeout=(3, 7), transport=httpx.MockTransport(handler))

    _run(_send(client, "GET"))

    assert seen["timeout"] == {
        "connect": 3.0,
        "read": 7.0,
        "write": 7.0,
        "pool": 3.0,
    }


def test_aclose_closes_the_httpx_client():
    client = AsyncHttpxClient(
        transport=httpx.MockTransport(lambda r: httpx.Response(200))
    )

    async def run():
        await client.aclose()
        assert client._client.is_closed

    _run(run())
