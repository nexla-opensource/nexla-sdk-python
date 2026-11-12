"""AsyncNexlaClient behavior: auth, retries, errors, pagination, lifecycle.

httpx.MockTransport serves every response. Handlers are async so that
concurrent tasks really interleave. Sleeps are recorded, not slept.
"""

import asyncio
import inspect
import json
import subprocess
import sys
import warnings
from types import SimpleNamespace

import httpx
import pytest

from nexla_sdk.aio import AsyncHttpxClient, AsyncNexlaClient, AsyncPaginator
from nexla_sdk.aio import http_client as aio_http
from nexla_sdk.aio.resources.webhooks import WebhooksResource
from nexla_sdk.exceptions import (
    AuthenticationError,
    NexlaConnectionError,
    NexlaError,
    NexlaTimeoutError,
    ServerError,
)

pytestmark = pytest.mark.unit

BASE = "https://api.test/nexla-api"
TOKEN = {"access_token": "tok", "token_type": "bearer", "expires_in": 86400}
SOURCE = {"id": 1, "name": "s", "status": "ACTIVE"}


@pytest.fixture
def sleeps(monkeypatch):
    """Record backoff sleeps instead of waiting."""
    recorded = []

    async def fake_sleep(delay):
        recorded.append(delay)

    monkeypatch.setattr(aio_http, "asyncio", SimpleNamespace(sleep=fake_sleep))
    return recorded


def _client(handler, **kwargs):
    kwargs.setdefault("service_key", "svc")
    kwargs.setdefault("base_url", BASE)
    http_client = AsyncHttpxClient(transport=httpx.MockTransport(handler))
    return AsyncNexlaClient(http_client=http_client, **kwargs)


def _route(routes, calls=None):
    """Build an async handler from {(method, path_suffix): response_fn}."""

    async def handler(request):
        await asyncio.sleep(0)  # let other tasks run between requests
        if calls is not None:
            calls.append((request.method, request.url.path, request.url.params))
        if request.url.path.endswith("/token"):
            return httpx.Response(200, json=TOKEN)
        for (method, suffix), respond in routes.items():
            if request.method == method and request.url.path.endswith(suffix):
                return respond(request)
        raise AssertionError(f"no route for {request.method} {request.url}")

    return handler


def _json(status, payload, headers=None):
    return lambda request: httpx.Response(status, json=payload, headers=headers or {})


def test_concurrent_callers_share_one_token_request():
    token_calls = []

    async def handler(request):
        if request.url.path.endswith("/token"):
            token_calls.append(request)
            await asyncio.sleep(0)
            return httpx.Response(200, json=TOKEN)
        return httpx.Response(200, json=SOURCE)

    client = _client(handler)

    async def run():
        return await asyncio.gather(*(client.sources.get(1) for _ in range(5)))

    results = asyncio.run(run())

    assert len(token_calls) == 1
    assert all(r.id == 1 for r in results)


def test_401_obtains_one_new_token_and_retries_once():
    tokens = []

    async def handler(request):
        if request.url.path.endswith("/token"):
            tokens.append(request)
            return httpx.Response(
                200, json={**TOKEN, "access_token": f"t{len(tokens)}"}
            )
        if request.headers["authorization"] == "Bearer t1":
            return httpx.Response(401, json={"message": "expired"})
        return httpx.Response(200, json=SOURCE)

    client = _client(handler)

    result = asyncio.run(client.sources.get(1))

    assert result.id == 1
    assert len(tokens) == 2


def test_direct_access_token_is_used_without_token_request():
    seen = []

    def handler(request):
        seen.append((request.url.path, request.headers["authorization"]))
        return httpx.Response(200, json=SOURCE)

    client = AsyncNexlaClient(
        access_token="direct",
        base_url=BASE,
        http_client=AsyncHttpxClient(transport=httpx.MockTransport(handler)),
    )

    asyncio.run(client.sources.get(1))

    assert seen == [("/nexla-api/data_sources/1", "Bearer direct")]


def test_refresh_access_token_forces_a_new_token_request():
    calls = []
    client = _client(_route({}, calls))

    async def run():
        return await client.refresh_access_token()

    assert asyncio.run(run()) == "tok"
    assert [c[1] for c in calls] == ["/nexla-api/token"]


def test_post_503_is_not_retried(sleeps):
    calls = []
    client = _client(
        _route({("POST", "/data_sources"): _json(503, {"message": "down"})}, calls)
    )

    with pytest.raises(ServerError) as exc_info:
        asyncio.run(client.sources.create({"name": "s"}))

    assert exc_info.value.message == "down"
    assert [c[0] for c in calls if c[1].endswith("/data_sources")] == ["POST"]
    assert sleeps == []


def test_read_timeout_maps_to_nexla_timeout_error(sleeps):
    def timeout(request):
        raise httpx.ReadTimeout("read timed out", request=request)

    client = _client(_route({("POST", "/data_sources"): timeout}))

    with pytest.raises(NexlaTimeoutError) as exc_info:
        asyncio.run(client.sources.create({"name": "s"}))

    assert isinstance(exc_info.value, ServerError)  # compatibility with sync
    assert exc_info.value.method == "POST"


def test_connection_refused_maps_to_nexla_connection_error(sleeps):
    def refused(request):
        raise httpx.ConnectError("[Errno 61] Connection refused", request=request)

    client = _client(_route({("GET", "/data_sources/1"): refused}))

    with pytest.raises(NexlaConnectionError) as exc_info:
        asyncio.run(client.sources.get(1))

    assert isinstance(exc_info.value, ServerError)
    assert len(sleeps) == 3  # GET is retried for connect errors, three times


def test_429_retry_after_from_body_is_retried(sleeps):
    responses = iter(
        [
            _json(
                429,
                {"error": {"type": "rate", "detail": "slow", "retry_after": 4}},
            ),
            _json(200, SOURCE),
        ]
    )
    client = _client(_route({("GET", "/data_sources/1"): lambda r: next(responses)(r)}))

    assert asyncio.run(client.sources.get(1)).id == 1
    assert sleeps == [4]


def test_unexpected_error_is_wrapped_as_nexla_error(sleeps):
    def boom(request):
        raise ValueError("bad payload")

    client = _client(_route({("GET", "/data_sources/1"): boom}))

    with pytest.raises(NexlaError) as exc_info:
        asyncio.run(client.sources.get(1))

    assert "Request failed" in exc_info.value.message
    assert isinstance(exc_info.value.original_error, ValueError)


def test_auth_error_status_maps_to_authentication_error(sleeps):
    client = _client(
        _route({("GET", "/data_sources/1"): _json(403, {"message": "no access"})})
    )

    with pytest.raises(NexlaError) as exc_info:
        asyncio.run(client.sources.get(1))

    assert type(exc_info.value).__name__ == "AuthorizationError"


def test_paginate_walks_pages_through_the_client():
    calls = []

    def page(request):
        number = int(request.url.params["page"])
        rows = [dict(SOURCE, id=10 * number + i) for i in range(2)]
        if number == 3:
            rows = rows[:1]  # short last page
        return httpx.Response(
            200,
            json=rows,
            headers={"X-Current-Page": str(number), "X-Total-Page-Count": "3"},
        )

    client = _client(_route({("GET", "/data_sources"): page}, calls))

    async def run():
        paginator = client.sources.paginate(per_page=2)
        assert isinstance(paginator, AsyncPaginator)
        return [s.id async for s in paginator.iter_items()]

    assert asyncio.run(run()) == [10, 11, 20, 21, 30]
    assert [c[2]["per_page"] for c in calls if c[1].endswith("/data_sources")] == [
        "2",
        "2",
        "2",
    ]


def test_last_response_headers_are_per_task(sleeps):
    def headers_for(path_id):
        def respond(request):
            return httpx.Response(200, json=SOURCE, headers={"X-Probe": path_id})

        return respond

    client = _client(
        _route(
            {
                ("GET", "/data_sources/1"): headers_for("one"),
                ("GET", "/data_sources/2"): headers_for("two"),
            }
        )
    )

    async def read(resource_id):
        await client.sources.get(resource_id)
        await asyncio.sleep(0)
        return client.last_response_headers["x-probe"]

    async def run():
        return await asyncio.gather(read(1), read(2))

    assert asyncio.run(run()) == ["one", "two"]


def test_last_response_headers_empty_before_any_request():
    client = _client(_route({}))
    assert dict(client.last_response_headers) == {}


def test_context_manager_closes_the_transport():
    client = _client(_route({}))

    async def run():
        async with client as entered:
            assert entered is client
        return client.http_client._client.is_closed

    assert asyncio.run(run()) is True


def test_switch_org_and_logout_are_coroutines():
    calls = []

    def handler(request):
        calls.append(request.url.path)
        if request.url.path.endswith("/token/refresh"):
            return httpx.Response(200, json={**TOKEN, "access_token": "org-tok"})
        return httpx.Response(200, json={})

    client = AsyncNexlaClient(
        access_token="direct",
        base_url=BASE,
        http_client=AsyncHttpxClient(transport=httpx.MockTransport(handler)),
    )

    async def run():
        token = await client.switch_org(42)
        await client.logout()
        return token.access_token

    assert asyncio.run(run()) == "org-tok"
    assert calls == ["/nexla-api/token/refresh", "/nexla-api/token/logout"]


def test_webhook_client_uses_the_async_transport():
    seen = []

    def handler(request):
        seen.append((request.method, str(request.url)))
        return httpx.Response(200, json={"dataset_id": 7, "processed": 1})

    client = AsyncNexlaClient(
        access_token="direct",
        base_url=BASE,
        http_client=AsyncHttpxClient(transport=httpx.MockTransport(handler)),
    )
    hooks = client.create_webhook_client("hook-key")

    assert isinstance(hooks, WebhooksResource)
    response = asyncio.run(
        hooks.send_one_record("https://hooks.test/webhook/abc", {"id": 1})
    )

    assert response.dataset_id == 7
    assert seen == [("POST", "https://hooks.test/webhook/abc?api_key=hook-key")]


def test_raw_operations_are_awaited():
    client = _client(_route({("GET", "/data_sources/1"): _json(200, SOURCE)}))

    body = asyncio.run(client.raw.get("/data_sources/1"))

    assert body == SOURCE


def test_missing_route_warns_and_stays_a_coroutine(sleeps):
    client = _client(_route({("GET", "/data_flows/data_source"): _json(200, [])}))

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        pending = client.data_flows.list_data_source_flows()

    assert inspect.iscoroutine(pending)
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)
    assert asyncio.run(pending) == []


def test_missing_credentials_raise_before_any_request(monkeypatch):
    for name in ("NEXLA_SERVICE_KEY", "NEXLA_API_KEY", "NEXLA_ACCESS_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(NexlaError):
        AsyncNexlaClient(base_url=BASE)


def test_token_fetch_failure_is_authentication_error(sleeps):
    def denied(request):
        return httpx.Response(401, json={"message": "bad key"})

    client = AsyncNexlaClient(
        service_key="bad",
        base_url=BASE,
        http_client=AsyncHttpxClient(
            transport=httpx.MockTransport(
                lambda r: denied(r) if r.url.path.endswith("/token") else None
            )
        ),
    )

    with pytest.raises(AuthenticationError):
        asyncio.run(client.get_access_token())


def test_importing_without_httpx_raises_a_clear_error():
    code = (
        "import sys\n"
        "sys.modules['httpx'] = None\n"
        "import nexla_sdk\n"
        "from nexla_sdk.exceptions import NexlaError\n"
        "try:\n"
        "    import nexla_sdk.aio\n"
        "except ImportError as exc:\n"
        "    print(str(exc))\n"
        "    raise SystemExit(0)\n"
        "raise SystemExit('no ImportError')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stderr
    assert "nexla-sdk[async]" in result.stdout


def test_sync_client_imports_without_httpx():
    # The sync client does not import httpx. Its import must keep working.
    code = (
        "import sys, json\n"
        "sys.modules['httpx'] = None\n"
        "from nexla_sdk import NexlaClient\n"
        "c = NexlaClient(access_token='x', base_url='https://a.test/n')\n"
        "print(json.dumps(sorted(k for k in vars(c) if not k.startswith('_'))[:3]))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout.strip())


def test_resource_wiring_matches_sync_client_names():
    from nexla_sdk import NexlaClient

    sync = NexlaClient(access_token="x", base_url=BASE)
    client = AsyncNexlaClient(access_token="x", base_url=BASE)

    sync_attrs = {k for k, v in vars(sync).items() if not k.startswith("_")}
    async_attrs = {k for k, v in vars(client).items() if not k.startswith("_")}
    assert async_attrs - {
        "api_url",
        "api_version",
        "tracer",
        "http_client",
        "auth_handler",
    } == (
        sync_attrs - {"api_url", "api_version", "tracer", "http_client", "auth_handler"}
    )


def test_async_client_init_signature_matches_sync():
    from nexla_sdk import NexlaClient

    def params(fn):
        return [
            (p.name, p.default)
            for p in inspect.signature(fn).parameters.values()
            if p.name != "self"
        ]

    assert params(AsyncNexlaClient.__init__) == params(NexlaClient.__init__)
