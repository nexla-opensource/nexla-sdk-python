"""Operation drift check: scripts/parity extractor, manifest, and backend comparison."""

from __future__ import annotations

import ast
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest

ROOT = Path(__file__).resolve().parents[2]
PARITY = ROOT / "scripts" / "parity"
if str(PARITY) not in sys.path:
    sys.path.insert(0, str(PARITY))

extract = importlib.import_module("extract_sdk_operations")
check = importlib.import_module("check_operation_map_sync")

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _no_backend_spec_env(monkeypatch):
    monkeypatch.delenv("NEXLA_PUBLIC_SPEC", raising=False)


def _manifest_entries() -> List[Dict[str, Any]]:
    return json.loads(extract.DEFAULT_MANIFEST.read_text())["operations"]


def _write_spec(path: Path, keys: List[str]) -> Path:
    """Build a minimal backend spec that defines exactly these METHOD path keys."""
    paths: Dict[str, Dict[str, Any]] = {}
    for key in keys:
        method, template = key.split(" ", 1)
        # Use a named parameter so the test also covers {name} to {} normalization.
        spec_path = template.replace("{}", "{id}")
        paths.setdefault(spec_path, {})[method.lower()] = {"responses": {}}
    path.write_text(json.dumps({"openapi": "3.0.0", "paths": paths}))
    return path


def _function(source: str) -> ast.FunctionDef:
    module = ast.parse(source)
    return module.body[0].body[0]  # type: ignore[attr-defined]


def test_manifest_matches_current_sdk_operations(capsys):
    assert check.main([]) == 0
    assert "match" in capsys.readouterr().out


def test_stale_manifest_fails_with_regeneration_hint(tmp_path, capsys):
    entries = _manifest_entries()
    stale = tmp_path / "sdk_operations.json"
    stale.write_text(
        json.dumps({"operations": entries[1:]}, indent=2)
    )  # drop the first operation
    assert check.main(["--manifest", str(stale)]) == 1
    err = capsys.readouterr().err
    assert "added:" in err
    assert "extract_sdk_operations.py" in err


def test_missing_manifest_is_a_setup_error(tmp_path, capsys):
    assert check.main(["--manifest", str(tmp_path / "absent.json")]) == 2
    assert "Manifest not found" in capsys.readouterr().err


def test_backend_spec_missing_an_sdk_operation_fails(tmp_path, monkeypatch, capsys):
    spec = _write_spec(tmp_path / "spec.json", [])
    monkeypatch.setenv("NEXLA_PUBLIC_SPEC", str(spec))
    assert check.main([]) == 1
    err = capsys.readouterr().err
    assert "missing from the backend spec" in err
    assert "GET " in err


def test_backend_operation_missing_from_sdk_is_report_only(
    tmp_path, monkeypatch, capsys
):
    keys = [f"{e['operation']}" for e in _manifest_entries()]
    spec = _write_spec(tmp_path / "spec.json", keys + ["GET /only_in_backend"])
    monkeypatch.setenv("NEXLA_PUBLIC_SPEC", str(spec))
    assert check.main([]) == 0
    out = capsys.readouterr().out
    assert "report only, 1" in out
    assert "GET /only_in_backend" in out


def test_missing_public_spec_file_is_a_setup_error(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("NEXLA_PUBLIC_SPEC", str(tmp_path / "nope.json"))
    assert check.main([]) == 2
    assert "missing file" in capsys.readouterr().err


def test_conditional_path_and_default_verb_are_resolved():
    fn = _function(
        "class X:\n"
        "    def run(self, uid=None, method: str = 'POST'):\n"
        "        path = '/token' if uid is None else f'/token/{uid}'\n"
        "        return self._make_request(method.upper(), path)\n"
    )
    found, unresolved = extract.calls_in(fn, "/base", {})
    assert unresolved == []
    assert sorted(found) == [("POST", "/token"), ("POST", "/token/{}")]


def test_unresolvable_call_is_reported_not_dropped():
    fn = _function(
        "class X:\n"
        "    def run(self):\n"
        "        return self._make_request(mystery(), '/x')\n"
    )
    found, unresolved = extract.calls_in(fn, "/base", {})
    assert found == []
    assert unresolved == ["run (line 3)"]
