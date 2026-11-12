"""Replay the shared contract fixtures through AsyncNexlaClient.

Same fixtures and assertions as test_contract_fixtures.py. The transport is the
real AsyncHttpxClient over httpx.MockTransport. Sleeps are recorded, not slept.
"""

import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest

from nexla_sdk.aio import AsyncHttpxClient, AsyncNexlaClient
from nexla_sdk.aio import http_client as aio_http
from nexla_sdk.exceptions import NexlaError
from tests.contract.test_contract_fixtures import (
    BASE,
    EXPECTED_FIXTURE_COUNT,
    FIXTURES,
    _assert_error,
    _assert_request,
    _assert_subset,
    _custodians,
    _plain,
    _step,
)

pytestmark = pytest.mark.unit


class _Wire:
    """Serves scripted steps in order and records every request."""

    def __init__(self, monkeypatch, steps):
        self.steps = list(steps)
        self.calls = []
        self.sleeps = []

        async def fake_sleep(delay):
            self.sleeps.append(delay)

        monkeypatch.setattr(aio_http, "asyncio", SimpleNamespace(sleep=fake_sleep))

    def handler(self, request):
        self.calls.append(
            {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "body": request.content or None,
            }
        )
        if not self.steps:
            raise AssertionError(f"Unexpected request: {request.method} {request.url}")
        status, headers, payload = self.steps.pop(0)
        if payload is None:
            return httpx.Response(status, headers=headers)
        if isinstance(payload, str):
            return httpx.Response(status, headers=headers, content=payload.encode())
        return httpx.Response(status, headers=headers, json=payload)


async def _run(client, call):
    """Map a fixture op to one async SDK call (fixture README: Ops)."""
    op, args = call["op"], call["args"]
    if op == "get_source":
        return await client.sources.get(args["id"])
    if op == "create_source":
        return await client.sources.create(args["body"])
    if op == "list_sources_all":
        return [
            item
            async for item in client.sources.paginate(
                per_page=args["per_page"]
            ).iter_items()
        ]
    if op == "add_custodians":
        return await client.organizations.add_custodians(
            args["org_id"], _custodians(args)
        )
    if op == "reset_custodians":
        return await client.organizations.reset_custodians(
            args["org_id"], _custodians(args)
        )
    if op == "reject_approval":
        return await client.approval_requests.reject(args["request_id"])
    if op == "login":
        await client.refresh_access_token()  # forces POST /token
        return await client.sources.get(1)
    raise AssertionError(f"Unknown fixture op: {op}")


def test_fixture_count_matches_contract():
    assert len(FIXTURES) == EXPECTED_FIXTURE_COUNT


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.stem)
def test_fixture_replays_through_async_client(fixture, monkeypatch):
    spec = json.loads(fixture.read_text())
    wire = _Wire(monkeypatch, [_step(ex["response"]) for ex in spec["exchanges"]])
    max_retries = spec["client"].get("max_retries", 3)

    async def scenario():
        http_client = AsyncHttpxClient(
            max_retries=max_retries, transport=httpx.MockTransport(wire.handler)
        )
        client = AsyncNexlaClient(
            base_url=BASE,
            http_client=http_client,
            **{k: v for k, v in spec["client"].items() if k != "max_retries"},
        )
        try:
            return ("ok", _plain(await _run(client, spec["call"])))
        except NexlaError as err:
            return ("error", err)
        finally:
            await client.aclose()

    outcome, value = asyncio.run(scenario())

    if "error" in spec["expect"]:
        assert outcome == "error", f"expected an error, got {value!r}"
        _assert_error(value, spec["expect"]["error"])
    else:
        assert outcome == "ok", f"unexpected error: {value!r}"
        _assert_subset(spec["expect"]["result"], value, "result")

    assert len(wire.calls) == len(spec["exchanges"]), "request count"
    for index, (expected, actual) in enumerate(zip(spec["exchanges"], wire.calls)):
        _assert_request(expected["request"], actual, index)
