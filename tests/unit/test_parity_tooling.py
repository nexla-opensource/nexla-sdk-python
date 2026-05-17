"""Unit tests for parity tooling scripts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# The OpenAPI spec is sourced from upstream and not committed to this repo.
# Skip parity-tooling tests when the spec file is absent so unit suites stay
# green for contributors who do not have the spec checked out locally.
SPEC_PATH = Path("plugin-redoc-0.yaml")
spec_required = pytest.mark.skipif(
    not SPEC_PATH.exists(),
    reason="plugin-redoc-0.yaml not present at repo root; parity tooling tests are local-only",
)


@spec_required
@pytest.mark.unit
def test_generate_operation_map_script():
    result = subprocess.run(
        [
            sys.executable,
            "scripts/parity/generate_operation_map.py",
            "--spec",
            "plugin-redoc-0.yaml",
            "--output",
            "nexla_sdk/generated/operation_map.py",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert Path("nexla_sdk/generated/operation_map.py").exists()


@spec_required
@pytest.mark.unit
def test_check_operation_map_sync_script():
    result = subprocess.run(
        [sys.executable, "scripts/parity/check_operation_map_sync.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


@spec_required
@pytest.mark.unit
def test_build_matrices_script_with_temp_routes(tmp_path: Path):
    routes = tmp_path / "routes.rb"
    routes.write_text(
        "\n".join(
            [
                "post '/token', :to => 'token#create'",
                "put '/token/logout', :to => 'token#invalidate'",
                "match '/notification_types/list' => 'notification_types#list', :via => [:get]",
            ]
        )
    )
    out_dir = tmp_path / "parity_out"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/parity/build_matrices.py",
            "--spec",
            "plugin-redoc-0.yaml",
            "--admin-routes",
            str(routes),
            "--resources-dir",
            "nexla_sdk/resources",
            "--out-dir",
            str(out_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    expected_files = {
        "openapi_matrix.json",
        "admin_routes_matrix.json",
        "sdk_matrix.json",
        "diff_openapi_vs_sdk.json",
        "diff_admin_routes_vs_sdk.json",
    }
    created_files = {path.name for path in out_dir.glob("*.json")}
    assert expected_files.issubset(created_files)

    diff_payload = json.loads((out_dir / "diff_openapi_vs_sdk.json").read_text())
    assert "missing_in_sdk" in diff_payload
    assert "extra_in_sdk" in diff_payload
