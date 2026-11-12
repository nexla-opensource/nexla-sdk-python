#!/usr/bin/env python3
"""Extract the HTTP operations that nexla_sdk sends, and write the drift manifest.

The extractor walks nexla_sdk/resources/*.py with the ast module. For each
resource class it resolves self._path and every _make_request(method, path)
call. It follows super() calls and helper methods, and it reads literal and
default HTTP verbs. A call it cannot resolve is an error. Such a call would
otherwise drop out of the manifest without notice.

Usage:
    python scripts/parity/extract_sdk_operations.py            # rewrite the manifest
    python scripts/parity/extract_sdk_operations.py --stdout   # print, write nothing

check_operation_map_sync.py compares the manifest with the current code.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "scripts" / "parity" / "sdk_operations.json"
HTTP = {"GET", "POST", "PUT", "PATCH", "DELETE"}

Endpoints = Dict[Tuple[str, str], Set[str]]
Operations = List[Tuple[str, List[str]]]


def normalize_path(path: str) -> str:
    """Replace every path parameter with {} and drop a trailing slash."""
    return re.sub(r"\{[^}]*\}", "{}", path).rstrip("/") or "/"


def class_paths(root: Path) -> Dict[str, Tuple[str, str, type]]:
    """Map resource class name to (attribute name, _path, class) on a client."""
    sys.path.insert(0, str(root))
    import nexla_sdk
    from nexla_sdk import NexlaClient
    from nexla_sdk.resources.base_resource import BaseResource

    # The AST pass reads files under root. The runtime pass must import the same tree.
    loaded = Path(nexla_sdk.__file__).resolve().parent.parent
    if loaded != root.resolve():
        raise RuntimeError(
            f"nexla_sdk was imported from {loaded}, not {root}. "
            f"Run with PYTHONPATH={root}."
        )

    client = NexlaClient(access_token="extract-only")
    out: Dict[str, Tuple[str, str, type]] = {}
    for name in dir(client):
        try:
            value = getattr(client, name)
        except Exception:
            continue
        if isinstance(value, BaseResource):
            out[type(value).__name__] = (name, value._path, type(value))
    return out


def _values(expr: ast.AST, path: str, scope: Dict[str, List[str]]) -> List[str]:
    """Every string the expression can take. An empty list means unknown."""
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        return [expr.value]
    if isinstance(expr, ast.JoinedStr):
        acc = [""]
        for part in expr.values:
            if isinstance(part, ast.Constant):
                pieces = [str(part.value)]
            else:
                inner = _values(part.value, path, scope)
                # An absolute path is substituted. Any other value is a {} parameter.
                pieces = [v if v.startswith("/") else "{}" for v in inner] or ["{}"]
            acc = [a + b for a in acc for b in pieces]
        return acc
    if isinstance(expr, ast.Attribute) and expr.attr == "_path":
        return [path]
    if isinstance(expr, ast.Name):
        return list(scope.get(expr.id, []))
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
        return [
            a + b
            for a in _values(expr.left, path, scope)
            for b in _values(expr.right, path, scope)
        ]
    if isinstance(expr, ast.IfExp):
        return _values(expr.body, path, scope) + _values(expr.orelse, path, scope)
    return []


def _verb_literals(node: ast.AST) -> Set[str]:
    return {
        c.value.upper()
        for c in ast.walk(node)
        if isinstance(c, ast.Constant)
        and isinstance(c.value, str)
        and c.value.upper() in HTTP
    }


def verbs_for(m_arg: ast.AST, fn: ast.FunctionDef) -> Set[str]:
    """HTTP verbs a dynamic method argument can take.

    Covers `method`, `method.upper()`, a local assigned a literal or a dict
    lookup, and a parameter with a literal default such as method="POST".
    """
    if (
        isinstance(m_arg, ast.Call)
        and isinstance(m_arg.func, ast.Attribute)
        and m_arg.func.attr == "upper"
    ):
        m_arg = m_arg.func.value
    if not isinstance(m_arg, ast.Name):
        return set()

    out: Set[str] = set()
    dict_names: Set[str] = set()
    for node in ast.walk(fn):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == m_arg.id
        ):
            out |= _verb_literals(node.value)
            for sub in ast.walk(node.value):
                if (
                    isinstance(sub, ast.Call)
                    and isinstance(sub.func, ast.Attribute)
                    and sub.func.attr == "get"
                    and isinstance(sub.func.value, ast.Name)
                ):
                    dict_names.add(sub.func.value.id)
    for node in ast.walk(fn):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in dict_names
            and isinstance(node.value, ast.Dict)
        ):
            out |= _verb_literals(node.value)

    defaults: Dict[str, ast.AST] = {}
    if fn.args.defaults:
        positional = fn.args.args[-len(fn.args.defaults) :]
        defaults.update(zip((a.arg for a in positional), fn.args.defaults))
    for arg, default in zip(fn.args.kwonlyargs, fn.args.kw_defaults):
        if default is not None:
            defaults[arg.arg] = default
    if m_arg.id in defaults:
        out |= _verb_literals(defaults[m_arg.id])
    return out


def calls_in(
    fn: ast.FunctionDef,
    path: str,
    helper_methods: Dict[str, Set[str]],
) -> Tuple[List[Tuple[str, str]], List[str]]:
    """Return the (method, path) pairs this function sends, and its unresolved calls."""
    scope: Dict[str, List[str]] = {}
    for node in ast.walk(fn):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            values = _values(node.value, path, scope)
            if values:
                scope[node.targets[0].id] = values

    out: List[Tuple[str, str]] = []
    unresolved: List[str] = []
    for node in ast.walk(fn):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "_make_request"
            and len(node.args) >= 2
        ):
            continue
        m_arg, p_arg = node.args[0], node.args[1]
        if isinstance(m_arg, ast.Constant) and isinstance(m_arg.value, str):
            methods = [m_arg.value.upper()]
        else:
            methods = sorted(verbs_for(m_arg, fn) or helper_methods.get(fn.name, set()))
        paths = sorted(set(_values(p_arg, path, scope)))
        if not methods or not paths:
            unresolved.append(f"{fn.name} (line {node.lineno})")
            continue
        out += [(m, p) for m in methods for p in paths]
    return out, unresolved


def helper_method_literals(cls: ast.AST) -> Dict[str, Set[str]]:
    """Map helper name to the HTTP verb literals passed to it as self.<helper>(...)."""
    res: Dict[str, Set[str]] = {}
    for node in ast.walk(cls):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "self"
        ):
            args = list(node.args) + [k.value for k in node.keywords]
            literals = {
                a.value.upper()
                for a in args
                if isinstance(a, ast.Constant)
                and isinstance(a.value, str)
                and a.value.upper() in HTTP
            }
            if literals:
                res.setdefault(node.func.attr, set()).update(literals)
    return res


def calls_super(fn: ast.FunctionDef) -> bool:
    return any(
        isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and isinstance(n.func.value, ast.Call)
        and isinstance(n.func.value.func, ast.Name)
        and n.func.value.func.id == "super"
        for n in ast.walk(fn)
    )


def extract(root: Path) -> Tuple[Endpoints, List[str]]:
    paths = class_paths(root)
    trees: Dict[str, ast.ClassDef] = {}
    for source in sorted((root / "nexla_sdk" / "resources").glob("*.py")):
        for node in ast.parse(source.read_text()).body:
            if isinstance(node, ast.ClassDef):
                trees[node.name] = node

    endpoints: Endpoints = {}
    unresolved: List[str] = []
    for cls_name, (attr, path, cls) in paths.items():
        seen: Set[str] = set()
        delegating: Set[str] = set()
        # Walk the MRO so inherited methods resolve against this class's _path.
        for klass in cls.__mro__:
            node = trees.get(klass.__name__)
            if node is None:
                continue
            helpers: Dict[str, Set[str]] = {}
            for source in (trees[cls_name], node):
                for name, verbs in helper_method_literals(source).items():
                    helpers.setdefault(name, set()).update(verbs)
            for fn in node.body:
                if not isinstance(fn, ast.FunctionDef):
                    continue
                if fn.name in seen and fn.name not in delegating:
                    continue
                seen.add(fn.name)
                delegating.discard(fn.name)
                # A wrapper that calls super().<name>() hands its endpoints to the base method.
                if calls_super(fn):
                    delegating.add(fn.name)
                found, missed = calls_in(fn, path, helpers)
                unresolved += [f"{cls_name}.{m}" for m in missed]
                for method, endpoint in found:
                    endpoints.setdefault((method, endpoint), set()).add(
                        f"{attr}.{fn.name}"
                    )
    return endpoints, sorted(unresolved)


def collect(root: Path) -> Tuple[Operations, List[str]]:
    """Return the sorted operations with their owners, and the unresolved calls."""
    endpoints, unresolved = extract(root)
    operations: Dict[str, Set[str]] = {}
    for (method, path), owners in endpoints.items():
        key = f"{method} {normalize_path(path)}"
        operations.setdefault(key, set()).update(owners)
    return [
        (key, sorted(owners)) for key, owners in sorted(operations.items())
    ], unresolved


def render(operations: Operations) -> str:
    """One line per operation, so a change shows as one diff line."""
    rows = []
    for key, owners in operations:
        methods = ", ".join(f'"{owner}"' for owner in owners)
        rows.append(f'    {{"operation": "{key}", "methods": [{methods}]}}')
    body = ",\n".join(rows)
    return '{\n  "operations": [\n' + body + "\n  ]\n}\n"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument(
        "--manifest", type=Path, default=DEFAULT_MANIFEST, help="manifest to write"
    )
    parser.add_argument(
        "--stdout", action="store_true", help="print the manifest and write nothing"
    )
    args = parser.parse_args(argv)

    operations, unresolved = collect(args.root.resolve())
    if unresolved:
        print(
            "Cannot resolve these _make_request calls. Make the method or path a "
            "literal, or teach extract_sdk_operations.py the pattern:",
            file=sys.stderr,
        )
        for item in unresolved:
            print(f"  {item}", file=sys.stderr)
        return 1

    text = render(operations)
    if args.stdout:
        sys.stdout.write(text)
        return 0
    args.manifest.write_text(text)
    print(f"Wrote {len(operations)} operations to {args.manifest}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
