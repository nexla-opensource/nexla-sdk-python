#!/usr/bin/env python3
"""Build route/spec/SDK parity matrices for Nexla SDK verification."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

import yaml

HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
SDK_REQUEST_RE = re.compile(r'_make_request\(\s*"([A-Z]+)"\s*,\s*([^)]+?)\s*(?:,|\))')
ROUTE_RE = re.compile(r"^\s*(get|post|put|delete|patch|match)\s+['\"]([^'\"]+)['\"]")
ROUTE_VIA_ARRAY_RE = re.compile(r":via\s*=>\s*\[([^\]]+)\]")
ROUTE_VIA_SINGLE_RE = re.compile(r"(?:via:|:via\s*=>)\s*:(\w+)")
PATH_VAR_RE = re.compile(r":([a-zA-Z_][a-zA-Z0-9_]*)")
ASSIGNMENT_RE = re.compile(r'^\s*(\w+)\s*=\s*(f?)"([^"]+)"')
DEF_RE = re.compile(r"^\s*def\s+\w+\(")
PATH_EQ_RE = re.compile(r'^\s*self\._path\s*=\s*"([^"]+)"')


@dataclass(frozen=True)
class Endpoint:
    method: str
    path: str
    source: str
    operation_id: Optional[str] = None

    def key(self) -> Tuple[str, str]:
        return self.method, self.path


def normalize_path(path: str) -> str:
    normalized = path.strip()
    normalized = normalized.replace("(.:format)", "")
    normalized = re.sub(r"\((/:([a-zA-Z_][a-zA-Z0-9_]*))\)", r"/:\2", normalized)
    normalized = re.sub(r"\(/([a-zA-Z_][a-zA-Z0-9_]*)\)", r"/\1", normalized)
    normalized = PATH_VAR_RE.sub(r"{\1}", normalized)
    normalized = re.sub(r"//+", "/", normalized)
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    if len(normalized) > 1 and normalized.endswith("/"):
        normalized = normalized[:-1]
    return normalized


def load_openapi_endpoints(spec_path: Path) -> List[Endpoint]:
    spec = yaml.safe_load(spec_path.read_text())
    endpoints: List[Endpoint] = []
    for path, path_item in (spec.get("paths") or {}).items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            upper_method = method.upper()
            if upper_method not in HTTP_METHODS:
                continue
            if not isinstance(operation, dict):
                continue
            endpoints.append(
                Endpoint(
                    method=upper_method,
                    path=normalize_path(path),
                    source="openapi",
                    operation_id=operation.get("operationId"),
                )
            )
    return endpoints


def _extract_match_methods(line: str) -> List[str]:
    via_array = ROUTE_VIA_ARRAY_RE.search(line)
    if via_array:
        tokens = [token.strip() for token in via_array.group(1).split(",")]
        return [token.lstrip(":").upper() for token in tokens if token.strip()]
    via_single = ROUTE_VIA_SINGLE_RE.search(line)
    if via_single:
        return [via_single.group(1).upper()]
    return []


def load_admin_routes(routes_path: Path) -> List[Endpoint]:
    endpoints: List[Endpoint] = []
    for line in routes_path.read_text().splitlines():
        route_match = ROUTE_RE.search(line)
        if not route_match:
            continue
        method = route_match.group(1).upper()
        path = normalize_path(route_match.group(2))
        methods: List[str]
        if method == "MATCH":
            methods = _extract_match_methods(line)
        else:
            methods = [method]

        for verb in methods:
            if verb in HTTP_METHODS:
                endpoints.append(
                    Endpoint(method=verb, path=path, source="admin_routes")
                )
    return endpoints


def _resolve_sdk_path_expr(
    expr: str, base_path: str, path_vars: Mapping[str, str]
) -> str:
    candidate = expr.strip()
    if candidate in path_vars:
        candidate = path_vars[candidate]

    if candidate.startswith('f"') and candidate.endswith('"'):
        candidate = candidate[2:-1]
    elif candidate.startswith('"') and candidate.endswith('"'):
        candidate = candidate[1:-1]
    elif candidate.startswith("'") and candidate.endswith("'"):
        candidate = candidate[1:-1]

    candidate = candidate.replace("{self._path}", base_path)
    if candidate == "self._path":
        candidate = base_path

    if "{self._path}" in candidate:
        candidate = candidate.replace("{self._path}", base_path)
    if "self._path" in candidate and candidate.startswith("self._path"):
        candidate = candidate.replace("self._path", base_path, 1)
    if candidate.startswith(base_path) or candidate.startswith("/"):
        return normalize_path(candidate)
    return normalize_path(f"{base_path}/{candidate}")


def load_sdk_endpoints(resources_dir: Path) -> List[Endpoint]:
    endpoints: List[Endpoint] = []
    for resource_file in sorted(resources_dir.glob("*.py")):
        text = resource_file.read_text()
        if "_make_request(" not in text:
            continue

        base_path = ""
        path_assign = PATH_EQ_RE.search(text)
        if path_assign:
            base_path = path_assign.group(1)

        path_vars: Dict[str, str] = {}
        for raw_line in text.splitlines():
            if DEF_RE.search(raw_line):
                path_vars = {}
            assign_match = ASSIGNMENT_RE.match(raw_line)
            if assign_match:
                var_name, is_f, value = assign_match.groups()
                path_vars[var_name] = f'f"{value}"' if is_f else f'"{value}"'

            request_match = SDK_REQUEST_RE.search(raw_line)
            if not request_match:
                continue

            method, path_expr = request_match.groups()
            if method not in HTTP_METHODS:
                continue
            if not base_path and "self._path" in path_expr:
                continue

            try:
                resolved_path = _resolve_sdk_path_expr(path_expr, base_path, path_vars)
            except Exception:
                continue

            endpoints.append(
                Endpoint(
                    method=method,
                    path=resolved_path,
                    source=str(resource_file),
                )
            )
    return endpoints


def dedupe(endpoints: Iterable[Endpoint]) -> List[Endpoint]:
    seen: Dict[Tuple[str, str], Endpoint] = {}
    for endpoint in endpoints:
        seen.setdefault(endpoint.key(), endpoint)
    return sorted(seen.values(), key=lambda endpoint: endpoint.key())


def build_diff(
    canonical: Iterable[Endpoint], sdk: Iterable[Endpoint]
) -> Dict[str, List[Dict[str, str]]]:
    canonical_set = {(endpoint.method, endpoint.path) for endpoint in canonical}
    sdk_set = {(endpoint.method, endpoint.path) for endpoint in sdk}

    missing_in_sdk = sorted(canonical_set - sdk_set)
    extra_in_sdk = sorted(sdk_set - canonical_set)

    return {
        "missing_in_sdk": [
            {"method": method, "path": path} for method, path in missing_in_sdk
        ],
        "extra_in_sdk": [
            {"method": method, "path": path} for method, path in extra_in_sdk
        ],
    }


def serialize_endpoints(endpoints: Iterable[Endpoint]) -> List[Dict[str, Any]]:
    return [
        {
            "method": endpoint.method,
            "path": endpoint.path,
            "source": endpoint.source,
            "operation_id": endpoint.operation_id,
        }
        for endpoint in endpoints
    ]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default="plugin-redoc-0.yaml")
    admin_api_root = os.environ.get("NEXLA_ADMIN_API_PATH")
    parser.add_argument(
        "--admin-routes",
        default=(
            os.path.join(admin_api_root, "config/routes.rb") if admin_api_root else None
        ),
        help=(
            "Path to admin-api config/routes.rb. Defaults to "
            "$NEXLA_ADMIN_API_PATH/config/routes.rb when the env var is set."
        ),
    )
    parser.add_argument("--resources-dir", default="nexla_sdk/resources")
    parser.add_argument("--out-dir", default="artifacts/parity")
    args = parser.parse_args()

    if not args.admin_routes:
        parser.error(
            "--admin-routes was not provided and NEXLA_ADMIN_API_PATH is unset. "
            "Pass the path explicitly or export the env var."
        )

    out_dir = Path(args.out_dir)
    spec_endpoints = dedupe(load_openapi_endpoints(Path(args.spec)))
    admin_endpoints = dedupe(load_admin_routes(Path(args.admin_routes)))
    sdk_endpoints = dedupe(load_sdk_endpoints(Path(args.resources_dir)))

    write_json(out_dir / "openapi_matrix.json", serialize_endpoints(spec_endpoints))
    write_json(
        out_dir / "admin_routes_matrix.json", serialize_endpoints(admin_endpoints)
    )
    write_json(out_dir / "sdk_matrix.json", serialize_endpoints(sdk_endpoints))
    write_json(
        out_dir / "diff_openapi_vs_sdk.json",
        build_diff(spec_endpoints, sdk_endpoints),
    )
    write_json(
        out_dir / "diff_admin_routes_vs_sdk.json",
        build_diff(admin_endpoints, sdk_endpoints),
    )

    print(f"Wrote parity matrices to {out_dir}")
    print(f"OpenAPI endpoints: {len(spec_endpoints)}")
    print(f"Admin route endpoints: {len(admin_endpoints)}")
    print(f"SDK endpoints: {len(sdk_endpoints)}")


if __name__ == "__main__":
    main()
