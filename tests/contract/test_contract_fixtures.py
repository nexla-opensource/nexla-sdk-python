"""Replay the shared contract fixtures through the real NexlaClient.

Fixtures are shared with the TypeScript SDK (tests/contract/fixtures/README.md).
Each fixture is one SDK call against a scripted HTTP exchange. The transport is
the real RequestsHttpClient with urllib3's socket-level request replaced
(tests/utils/scripted_transport.py). Sleeps are recorded, not slept.
"""

import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from nexla_sdk import NexlaClient
from nexla_sdk.exceptions import NexlaError
from nexla_sdk.models.organizations.custodians import (
    OrgCustodianRef,
    OrgCustodiansPayload,
)
from tests.utils.scripted_transport import ScriptedWire

pytestmark = pytest.mark.unit

FIXTURE_DIR = Path(__file__).parent / "fixtures"
FIXTURES = sorted(FIXTURE_DIR.glob("*.json"))
BASE = "https://api.test/nexla-api"
BASE_PATH = "/nexla-api"
EXPECTED_FIXTURE_COUNT = 21


def _custodians(args):
    return OrgCustodiansPayload(
        custodians=[OrgCustodianRef(**c) for c in args["custodians"]]
    )


def _run(client, call):
    """Map a fixture op to one SDK call (fixture README: Ops)."""
    op, args = call["op"], call["args"]
    if op == "get_source":
        return client.sources.get(args["id"])
    if op == "create_source":
        return client.sources.create(args["body"])
    if op == "list_sources_all":
        return list(client.sources.paginate(per_page=args["per_page"]).iter_items())
    if op == "add_custodians":
        return client.organizations.add_custodians(args["org_id"], _custodians(args))
    if op == "reset_custodians":
        return client.organizations.reset_custodians(args["org_id"], _custodians(args))
    if op == "reject_approval":
        return client.approval_requests.reject(args["request_id"])
    if op == "login":
        client.refresh_access_token()  # forces POST /token
        return client.sources.get(1)
    raise AssertionError(f"Unknown fixture op: {op}")


def _plain(value):
    if isinstance(value, list):
        return [_plain(v) for v in value]
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    return value


def _assert_subset(expected, actual, path):
    """Dicts: expected keys must match. Lists: same length, element by element. Others: equal."""
    if isinstance(expected, dict):
        assert isinstance(actual, dict), f"{path}: expected object, got {actual!r}"
        for key, value in expected.items():
            assert key in actual, f"{path}.{key} missing from {actual!r}"
            _assert_subset(value, actual[key], f"{path}.{key}")
    elif isinstance(expected, list):
        assert isinstance(actual, list) and len(actual) == len(expected), (
            f"{path}: expected {len(expected)} items, got {actual!r}"
        )
        for i, (e, a) in enumerate(zip(expected, actual)):
            _assert_subset(e, a, f"{path}[{i}]")
    else:
        assert actual == expected, f"{path}: expected {expected!r}, got {actual!r}"


def _assert_request(expected, actual, index):
    where = f"exchange {index}"
    assert actual["method"] == expected["method"], f"{where}: method"
    parts = urlsplit(actual["url"])
    assert parts.path == BASE_PATH + expected["path"], f"{where}: path {parts.path}"

    query = parse_qs(parts.query)
    for key, value in expected.get("query", {}).items():
        assert query.get(key) == [str(value)], f"{where}: query {key}={query.get(key)}"

    sent_headers = {k.lower(): v for k, v in actual["headers"].items()}
    for key, value in expected.get("headers", {}).items():
        assert sent_headers.get(key.lower()) == value, (
            f"{where}: header {key}={sent_headers.get(key.lower())!r}"
        )

    if "body" in expected:
        body = json.loads(actual["body"]) if actual["body"] else None
        _assert_subset(expected["body"], body, f"{where} body")


def _assert_error(err, expected):
    assert type(err).__name__ == expected["class"], (
        f"expected {expected['class']}, got {type(err).__name__}: {err}"
    )
    assert err.status_code == expected["status"]
    if "message" in expected:
        assert err.message == expected["message"]
    if "error_code" in expected:
        assert err.error_code == expected["error_code"]
    if "retry_after" in expected:
        assert err.retry_after == expected["retry_after"]
    if "request_id" in expected:
        assert err.request_id == expected["request_id"]


def _step(response):
    if "body" in response:
        payload = response["body"]
    elif "text" in response:
        payload = response["text"]
    else:
        payload = None
    return (response["status"], response.get("headers", {}), payload)


def test_fixture_count_matches_contract():
    assert len(FIXTURES) == EXPECTED_FIXTURE_COUNT


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.stem)
def test_fixture_replays_through_real_client(fixture, monkeypatch):
    spec = json.loads(fixture.read_text())
    wire = ScriptedWire(
        monkeypatch, [_step(ex["response"]) for ex in spec["exchanges"]]
    )
    client = NexlaClient(base_url=BASE, **spec["client"])

    if "error" in spec["expect"]:
        with pytest.raises(NexlaError) as exc_info:
            _run(client, spec["call"])
        _assert_error(exc_info.value, spec["expect"]["error"])
    else:
        _assert_subset(
            spec["expect"]["result"], _plain(_run(client, spec["call"])), "result"
        )

    assert len(wire.calls) == len(spec["exchanges"]), "request count"
    for index, (expected, actual) in enumerate(zip(spec["exchanges"], wire.calls)):
        _assert_request(expected["request"], actual, index)


def test_manifest_lists_every_fixture_with_matching_sha256():
    manifest = {}
    for line in (FIXTURE_DIR / "MANIFEST.sha256").read_text().splitlines():
        digest, name = line.split(None, 1)
        manifest[name.strip()] = digest

    assert set(manifest) == {p.name for p in FIXTURES}
    for name, digest in manifest.items():
        actual = hashlib.sha256((FIXTURE_DIR / name).read_bytes()).hexdigest()
        assert actual == digest, f"{name}: fixture changed. Do not edit fixtures here."
