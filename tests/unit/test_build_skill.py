"""Unit tests for scripts/build_skill.py (nexla.skill bundle)."""

from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load_build_skill() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "build_skill", ROOT / "scripts" / "build_skill.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.unit
def test_build_is_deterministic():
    build_skill = _load_build_skill()
    files = build_skill.source_files()
    assert build_skill.build_archive(files) == build_skill.build_archive(files)


@pytest.mark.unit
def test_committed_bundle_matches_skill_source():
    build_skill = _load_build_skill()
    members = build_skill.build_members(build_skill.source_files())
    assert build_skill.committed_members() == members


@pytest.mark.unit
def test_check_fails_when_bundle_is_stale(tmp_path, monkeypatch):
    build_skill = _load_build_skill()
    stale = tmp_path / "nexla.skill"
    with zipfile.ZipFile(stale, "w") as archive:
        archive.writestr("nexla/SKILL.md", "stale")
    monkeypatch.setattr(build_skill, "OUTPUT", stale)
    monkeypatch.setattr(sys, "argv", ["build_skill.py", "--check"])
    assert build_skill.main() == 1
