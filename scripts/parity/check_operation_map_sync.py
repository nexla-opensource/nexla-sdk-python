#!/usr/bin/env python3
"""Fail if generated operation map is out of sync with OpenAPI spec."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default="plugin-redoc-0.yaml")
    parser.add_argument("--target", default="nexla_sdk/generated/operation_map.py")
    args = parser.parse_args()

    spec = Path(args.spec)
    if not spec.exists():
        # The OpenAPI spec is sourced from upstream and not committed to this
        # repo, so the parity check has nothing to compare against in CI or for
        # contributors who have not checked it out locally. Match the skip
        # behavior used in tests/unit/test_parity_tooling.py.
        print(
            f"Spec {spec} not present; skipping operation_map sync check.",
            file=sys.stderr,
        )
        return 0

    target = Path(args.target)
    if not target.exists():
        print(f"Target file does not exist: {target}", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_target = Path(tmpdir) / "operation_map.py"
        cmd = [
            sys.executable,
            "scripts/parity/generate_operation_map.py",
            "--spec",
            args.spec,
            "--output",
            str(tmp_target),
        ]
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if result.returncode != 0:
            sys.stderr.write(result.stderr)
            return result.returncode

        current = target.read_text()
        generated = tmp_target.read_text()
        if current != generated:
            print(
                "operation_map.py is out of sync with plugin-redoc-0.yaml. "
                "Run: python scripts/parity/generate_operation_map.py",
                file=sys.stderr,
            )
            return 1

    print("operation_map.py is in sync.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
