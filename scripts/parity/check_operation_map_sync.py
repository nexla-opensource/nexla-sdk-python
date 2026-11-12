#!/usr/bin/env python3
"""Check the SDK's HTTP operations for drift.

Default check:
    The operations in nexla_sdk must equal scripts/parity/sdk_operations.json.
    Any added, removed, or re-owned operation fails the check. When the change
    is intended, regenerate the manifest with extract_sdk_operations.py.

Backend check (optional):
    Set NEXLA_PUBLIC_SPEC to a public backend spec JSON. Build it with
    nexla-sdk-js/scripts/backend-spec/build_public_spec.py.
      - An SDK operation missing from the backend spec fails the check.
      - A backend operation missing from the SDK is reported, and does not fail.

Local OpenAPI check:
    When plugin-redoc-0.yaml exists at the repo root, nexla_sdk/generated/operation_map.py
    must match it. The file is not committed, so the check prints a skip message without it.

Exit codes: 0 pass, 1 drift or a missing backend operation, 2 setup error.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import extract_sdk_operations as extractor  # noqa: E402

BACKEND_METHODS = ("get", "post", "put", "patch", "delete")
MANIFEST_HINT = (
    "Run: python scripts/parity/extract_sdk_operations.py, "
    "then commit scripts/parity/sdk_operations.json."
)


def load_manifest(path: Path) -> Dict[str, List[str]]:
    data = json.loads(path.read_text())
    return {entry["operation"]: entry["methods"] for entry in data["operations"]}


def manifest_drift(
    current: Dict[str, List[str]], manifest: Dict[str, List[str]]
) -> List[str]:
    """One line per difference. An empty list means the two match."""
    lines = []
    for key in sorted(set(current) - set(manifest)):
        lines.append(f"  added:   {key} {current[key]}")
    for key in sorted(set(manifest) - set(current)):
        lines.append(f"  removed: {key}")
    for key in sorted(set(current) & set(manifest)):
        if current[key] != manifest[key]:
            lines.append(f"  owners:  {key} {manifest[key]} -> {current[key]}")
    return lines


def backend_operations(spec_path: Path) -> Set[str]:
    spec = json.loads(spec_path.read_text())
    keys: Set[str] = set()
    for path, item in spec.get("paths", {}).items():
        for method in item:
            if method in BACKEND_METHODS:
                keys.add(f"{method.upper()} {extractor.normalize_path(path)}")
    return keys


def check_manifest(current: Dict[str, List[str]], manifest_path: Path) -> int:
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}. {MANIFEST_HINT}", file=sys.stderr)
        return 2
    drift = manifest_drift(current, load_manifest(manifest_path))
    if drift:
        print(f"SDK operations differ from {manifest_path.name}:", file=sys.stderr)
        for line in drift:
            print(line, file=sys.stderr)
        print(
            f"If the change is intended, update the manifest. {MANIFEST_HINT}",
            file=sys.stderr,
        )
        return 1
    print(f"SDK operations match {manifest_path.name} ({len(current)} operations).")
    return 0


def check_backend_spec(sdk_keys: Iterable[str], spec_path: Path) -> int:
    if not spec_path.exists():
        print(
            f"NEXLA_PUBLIC_SPEC points to a missing file: {spec_path}", file=sys.stderr
        )
        return 2
    backend = backend_operations(spec_path)
    sdk = set(sdk_keys)
    missing_in_backend = sorted(sdk - backend)
    missing_in_sdk = sorted(backend - sdk)
    print(f"Backend spec: {len(backend)} operations. SDK: {len(sdk)} operations.")
    if missing_in_sdk:
        print(
            f"Backend operations not in the SDK (report only, {len(missing_in_sdk)}):"
        )
        for key in missing_in_sdk:
            print(f"  {key}")
    if missing_in_backend:
        print(
            f"SDK operations missing from the backend spec ({len(missing_in_backend)}):",
            file=sys.stderr,
        )
        for key in missing_in_backend:
            print(f"  {key}", file=sys.stderr)
        return 1
    print("Every SDK operation exists in the backend spec.")
    return 0


def check_operation_map(spec: Path, target: Path) -> int:
    if not spec.exists():
        print(
            f"Skipped operation_map.py check: {spec.name} is not present (local only)."
        )
        return 0
    if not target.exists():
        print(f"Target file does not exist: {target}", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory() as tmpdir:
        generated = Path(tmpdir) / "operation_map.py"
        result = subprocess.run(
            [
                sys.executable,
                str(HERE / "generate_operation_map.py"),
                "--spec",
                str(spec),
                "--output",
                str(generated),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            sys.stderr.write(result.stderr)
            return result.returncode
        if target.read_text() != generated.read_text():
            print(
                f"operation_map.py is out of sync with {spec.name}. "
                "Run: python scripts/parity/generate_operation_map.py",
                file=sys.stderr,
            )
            return 1
    print("operation_map.py is in sync.")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=extractor.DEFAULT_MANIFEST,
        help="manifest to compare",
    )
    parser.add_argument("--spec", type=Path, default=Path("plugin-redoc-0.yaml"))
    parser.add_argument(
        "--target", type=Path, default=Path("nexla_sdk/generated/operation_map.py")
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()

    operations, unresolved = extractor.collect(root)
    if unresolved:
        print("Cannot resolve these _make_request calls:", file=sys.stderr)
        for item in unresolved:
            print(f"  {item}", file=sys.stderr)
        return 2
    current = dict(operations)

    status = check_manifest(current, args.manifest)

    public_spec = os.environ.get("NEXLA_PUBLIC_SPEC")
    if public_spec:
        status = max(status, check_backend_spec(current, Path(public_spec)))

    spec = args.spec if args.spec.is_absolute() else root / args.spec
    target = args.target if args.target.is_absolute() else root / args.target
    status = max(status, check_operation_map(spec, target))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
