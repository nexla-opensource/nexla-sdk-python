#!/usr/bin/env python3
"""Generate a Python operation map from the OpenAPI spec."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import yaml

HTTP_METHODS = {"get", "post", "put", "delete", "patch", "head", "options"}
SAFE_IDENTIFIER = re.compile(r"[^a-zA-Z0-9_]")


def normalize_operation_id(operation_id: str, fallback: str) -> str:
    cleaned = SAFE_IDENTIFIER.sub("_", operation_id).strip("_")
    if not cleaned:
        cleaned = fallback
    if cleaned[0].isdigit():
        cleaned = f"op_{cleaned}"
    return cleaned


def iter_operations(spec: Dict[str, Any]) -> Iterable[Tuple[str, Dict[str, Any]]]:
    paths = spec.get("paths", {})
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            fallback = f"{method.lower()}_{path.strip('/').replace('/', '_')}"
            raw_operation_id = operation.get("operationId") or fallback
            operation_id = normalize_operation_id(raw_operation_id, fallback)
            yield (
                operation_id,
                {
                    "method": method.upper(),
                    "path": path,
                    "tags": operation.get("tags", []),
                    "summary": operation.get("summary", ""),
                    "path_params": sorted(
                        {match.group(1) for match in re.finditer(r"\{([^}]+)\}", path)}
                    ),
                },
            )


def render_output(operations: Dict[str, Dict[str, Any]]) -> str:
    operation_ids = sorted(operations.keys())
    literal_values = ",\n    ".join(
        repr(operation_id) for operation_id in operation_ids
    )
    lines: List[str] = []
    lines.append(
        '"""Auto-generated operation map from OpenAPI. Do not edit manually."""'
    )
    lines.append("")
    lines.append("from typing import Dict, List, Literal, TypedDict")
    lines.append("")
    lines.append("")
    lines.append("class OperationSpec(TypedDict):")
    lines.append("    method: str")
    lines.append("    path: str")
    lines.append("    tags: List[str]")
    lines.append("    summary: str")
    lines.append("    path_params: List[str]")
    lines.append("")
    lines.append("")
    lines.append("OperationId = Literal[")
    if literal_values:
        lines.append(f"    {literal_values}")
    lines.append("]")
    lines.append("")
    lines.append("")
    lines.append("OPERATION_MAP: Dict[str, OperationSpec] = {")
    for operation_id in operation_ids:
        spec = operations[operation_id]
        lines.append(f"    {operation_id!r}: {{")
        lines.append(f"        'method': {spec['method']!r},")
        lines.append(f"        'path': {spec['path']!r},")
        lines.append(f"        'tags': {spec['tags']!r},")
        lines.append(f"        'summary': {spec['summary']!r},")
        lines.append(f"        'path_params': {spec['path_params']!r},")
        lines.append("    },")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spec",
        default="plugin-redoc-0.yaml",
        help="Path to OpenAPI spec file",
    )
    parser.add_argument(
        "--output",
        default="nexla_sdk/generated/operation_map.py",
        help="Output Python module path",
    )
    args = parser.parse_args()

    spec_path = Path(args.spec)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    spec = yaml.safe_load(spec_path.read_text())
    operations: Dict[str, Dict[str, Any]] = {}

    duplicates: Dict[str, int] = {}
    for operation_id, operation_spec in iter_operations(spec):
        if operation_id in operations:
            duplicates[operation_id] = duplicates.get(operation_id, 1) + 1
            operation_id = f"{operation_id}_{duplicates[operation_id]}"
        operations[operation_id] = operation_spec

    output = render_output(operations)
    out_path.write_text(output)

    print(f"Generated {out_path} with {len(operations)} operations from {spec_path}.")


if __name__ == "__main__":
    main()
