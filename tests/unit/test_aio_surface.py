"""Async resource surface must match the sync client.

Every resource attribute, public method and parameter list on NexlaClient must
exist on AsyncNexlaClient. Only the async-ness differs: a method is a coroutine
function when its sync counterpart reaches I/O. The sync-only allowlist below
lists the public methods that do no I/O.
"""

import inspect

import pytest

from nexla_sdk import NexlaClient
from nexla_sdk.aio import AsyncNexlaClient
from nexla_sdk.aio.resources.base_resource import BaseResource as AsyncBaseResource
from nexla_sdk.resources.base_resource import BaseResource

pytestmark = pytest.mark.unit

BASE = "https://api.test/nexla-api"

# Public resource methods that stay sync: paginate() builds a paginator, and
# the stubs raise NotImplementedError without I/O.
SYNC_ONLY = {"paginate"}


def _is_stub(fn):
    try:
        return "raise NotImplementedError" in inspect.getsource(fn)
    except (OSError, TypeError):
        return False


def _is_coroutine(fn):
    return inspect.iscoroutinefunction(inspect.unwrap(fn))


def _params(fn):
    return [
        (p.name, p.kind, p.default)
        for p in inspect.signature(fn).parameters.values()
        if p.name != "self"
    ]


@pytest.fixture(scope="module")
def clients():
    return (
        NexlaClient(access_token="x", base_url=BASE),
        AsyncNexlaClient(access_token="x", base_url=BASE),
    )


def _resource_names(client):
    return sorted(
        name
        for name, value in vars(client).items()
        if isinstance(value, (BaseResource, AsyncBaseResource))
    )


def test_resource_attributes_match(clients):
    sync, asynchronous = clients
    assert _resource_names(asynchronous) == _resource_names(sync)
    assert len(_resource_names(sync)) >= 58


def test_raw_attribute_matches(clients):
    sync, asynchronous = clients
    assert type(sync.raw).__name__ == type(asynchronous.raw).__name__
    assert sync.raw.list_operations() == asynchronous.raw.list_operations()


def test_resource_public_methods_and_parameters_match(clients):
    sync, asynchronous = clients
    problems = []
    for name in _resource_names(sync):
        sync_res = getattr(sync, name)
        async_res = getattr(asynchronous, name)
        sync_methods = sorted(
            m
            for m in dir(sync_res)
            if not m.startswith("_") and callable(getattr(sync_res, m))
        )
        async_methods = sorted(
            m
            for m in dir(async_res)
            if not m.startswith("_") and callable(getattr(async_res, m))
        )
        if sync_methods != async_methods:
            problems.append(f"{name}: method names differ")
            continue
        for method in sync_methods:
            sync_fn = getattr(sync_res, method)
            async_fn = getattr(async_res, method)
            if _params(sync_fn) != _params(async_fn):
                problems.append(f"{name}.{method}: parameters differ")
            expect_sync = method in SYNC_ONLY or _is_stub(sync_fn)
            if expect_sync == _is_coroutine(async_fn):
                problems.append(
                    f"{name}.{method}: expected {'sync' if expect_sync else 'async'}"
                )
    assert problems == []


def test_client_methods_match(clients):
    sync, asynchronous = clients
    shared = [
        "request",
        "request_with_headers",
        "switch_org",
        "logout",
        "refresh_access_token",
        "get_access_token",
        "create_webhook_client",
        "aclose",
    ]
    for name in shared:
        assert hasattr(asynchronous, name), name
    for name in (
        "request",
        "request_with_headers",
        "switch_org",
        "logout",
        "refresh_access_token",
        "get_access_token",
        "aclose",
    ):
        assert inspect.iscoroutinefunction(getattr(asynchronous, name)), name
    assert not inspect.iscoroutinefunction(asynchronous.create_webhook_client)
    assert _params(sync.request) == _params(asynchronous.request)
    assert _params(sync.switch_org) == _params(asynchronous.switch_org)
    assert _params(sync.create_webhook_client) == _params(
        asynchronous.create_webhook_client
    )


def test_paginators_are_async_iterables(clients):
    _, asynchronous = clients
    paginator = asynchronous.sources.paginate(per_page=5)
    assert hasattr(paginator, "__aiter__")
    assert inspect.isasyncgenfunction(paginator.iter_items)
    assert inspect.isasyncgenfunction(paginator.iter_pages)
