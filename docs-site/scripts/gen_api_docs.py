#!/usr/bin/env python3
"""
Generate API Reference (MDX) for the Nexla Python SDK using introspection.

Outputs under docs-site/docs/api/python/modules.
Also writes a coverage and gaps REPORT.md.
"""

import importlib
import inspect
import pkgutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
PKG_NAME = "nexla_sdk"
DOCS_DIR = Path(__file__).resolve().parents[1] / "docs" / "api" / "python" / "modules"
REPORT_PATH = Path(__file__).resolve().parents[1] / "REPORT.md"
TRACE: Dict[str, Any] = {}


def find_package_root() -> Path:
    return ROOT / PKG_NAME


def iter_module_names(package: str) -> List[str]:
    names: List[str] = []
    spec = importlib.util.find_spec(package)
    if spec is None or not spec.submodule_search_locations:
        return names
    for m in pkgutil.walk_packages(
        spec.submodule_search_locations, prefix=f"{package}."
    ):
        # Skip private or cache
        if any(part.startswith("_") for part in m.name.split(".")):
            continue
        names.append(m.name)
    # Include the package itself first
    return [package] + sorted(names)


def safe_import(name: str):
    try:
        return importlib.import_module(name)
    except Exception as e:
        return e


def public_members(mod) -> Tuple[List[Tuple[str, Any]], List[Tuple[str, Any]]]:
    """Return (classes, functions) defined in module and public."""
    classes, functions = [], []
    for n, obj in inspect.getmembers(mod):
        if n.startswith("_"):
            continue
        if inspect.isclass(obj) and getattr(obj, "__module__", "").startswith(
            mod.__name__
        ):
            classes.append((n, obj))
        elif inspect.isfunction(obj) and getattr(obj, "__module__", "").startswith(
            mod.__name__
        ):
            functions.append((n, obj))
    return classes, functions


def get_source_info(obj) -> Tuple[Optional[str], Optional[int]]:
    try:
        file = inspect.getsourcefile(obj)
        lines, start = inspect.getsourcelines(obj)
        # make repo-relative path
        if file:
            try:
                file = str(Path(file).resolve().relative_to(ROOT))
            except Exception:
                file = str(file)
        return file, start
    except Exception:
        return None, None


def pydantic_fields(cls) -> List[Tuple[str, str, Optional[str]]]:
    fields: List[Tuple[str, str, Optional[str]]] = []
    try:
        mf = getattr(cls, "model_fields", {})
        for name, fld in mf.items():
            ftype = getattr(fld, "annotation", None)
            ftype_str = None
            if ftype is not None:
                try:
                    ftype_str = getattr(ftype, "__name__", None) or str(ftype)
                except Exception:
                    ftype_str = str(ftype)
            fdesc = getattr(fld, "description", None)
            fields.append((name, ftype_str or "", fdesc))
    except Exception:
        pass
    return fields


def enum_members(cls) -> List[Tuple[str, Any]]:
    try:
        import enum

        if issubclass(cls, enum.Enum):
            return [(m.name, m.value) for m in cls]  # type: ignore[attr-defined]
    except Exception:
        pass
    return []


def format_signature(obj) -> str:
    try:
        return str(inspect.signature(obj))
    except Exception:
        return "()"


def mdx_text(text: str) -> str:
    """Escape generated prose so Python examples are treated as MDX text."""
    return text.replace("{", "\\{").replace("}", "\\}")


def write_module_page(
    module_name: str, mod, coverage: Dict[str, Any], gaps: List[str]
) -> None:
    classes, functions = public_members(mod)
    file, line = get_source_info(mod)
    title = module_name
    slug = f"/api/python/modules/{module_name.replace('.', '/')}"
    out_path = DOCS_DIR / f"{module_name}.mdx"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    total_symbols = len(classes) + len(functions)
    documented = 0

    # record module trace
    TRACE[module_name] = {
        "module_source": f"{file}:{line}" if file and line else None,
        "classes": {},
        "functions": {},
    }

    with out_path.open("w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"id: {module_name}\n")
        f.write(f"title: {title}\n")
        f.write(f"slug: {slug}\n")
        f.write(f"description: API for {module_name}\n")
        f.write("keywords: [Nexla, SDK, Python, API]\n")
        f.write("---\n\n")

        if file and line:
            f.write(f"Source: `{file}:{line}`\n\n")

        mdoc = inspect.getdoc(mod) or ""
        if mdoc:
            f.write(mdx_text(mdoc) + "\n\n")

        if classes:
            f.write("## Classes\n\n")
            for cname, cls in classes:
                cdoc = inspect.getdoc(cls) or ""
                cfile, cline = get_source_info(cls)
                f.write(f"### {cname}\n\n")
                if cfile and cline:
                    f.write(f"Defined in `{cfile}:{cline}`\n\n")
                    TRACE[module_name]["classes"][cname] = f"{cfile}:{cline}"
                if cdoc:
                    f.write(mdx_text(cdoc) + "\n\n")
                # Pydantic fields
                fields = pydantic_fields(cls)
                if fields:
                    f.write("Fields:\n\n")
                    for n, t, d in fields:
                        dd = f" — {mdx_text(d)}" if d else ""
                        f.write(f"- `{n}`: `{t}`{dd}\n")
                    f.write("\n")
                # Enum members
                em = enum_members(cls)
                if em:
                    f.write("Members:\n\n")
                    for n, v in em:
                        f.write(f"- `{n}` = `{v}`\n")
                    f.write("\n")
                # Methods
                methods = [
                    (n, m)
                    for n, m in inspect.getmembers(cls, predicate=inspect.isfunction)
                    if not n.startswith("_")
                    and getattr(m, "__module__", "").startswith(mod.__name__)
                ]
                if methods:
                    f.write("Methods:\n\n")
                    for n, m in methods:
                        sig = format_signature(m)
                        mdoc = inspect.getdoc(m) or ""
                        mfile, mline = get_source_info(m)
                        f.write(f"- `{n}{sig}`\n")
                        if mfile and mline:
                            f.write(f"  - Source: `{mfile}:{mline}`\n")
                            TRACE[module_name]["classes"][f"{cname}.{n}"] = (
                                f"{mfile}:{mline}"
                            )
                        if mdoc:
                            f.write(f"  - {mdx_text(mdoc.splitlines()[0])}\n")
                    f.write("\n")
                documented += 1

        if functions:
            f.write("## Functions\n\n")
            for fname, func in functions:
                sig = format_signature(func)
                fdoc = inspect.getdoc(func) or ""
                ffile, fline = get_source_info(func)
                f.write(f"### `{fname}{sig}`\n\n")
                if ffile and fline:
                    f.write(f"Source: `{ffile}:{fline}`\n\n")
                    TRACE[module_name]["functions"][fname] = f"{ffile}:{fline}"
                if fdoc:
                    f.write(mdx_text(fdoc) + "\n\n")
                documented += 1

        # TODO marker if no symbols found
        if total_symbols == 0:
            f.write(
                "🚧 TODO: No public symbols detected. Verify module visibility and docstrings.\n\n"
            )
            if file and line:
                gaps.append(f"No symbols in {file}:{line}")

    coverage[module_name] = {
        "total": total_symbols,
        "documented": documented,
    }


def main() -> None:
    # Ensure import path includes repo root to import nexla_sdk from source
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    modules = iter_module_names(PKG_NAME)
    coverage: Dict[str, Any] = {}
    gaps: List[str] = []
    failures: List[str] = []

    for modname in modules:
        mod = safe_import(modname)
        if isinstance(mod, Exception):
            failures.append(f"Failed to import {modname}: {mod}")
            continue
        write_module_page(modname, mod, coverage, gaps)

    # Write coverage report
    total_symbols = sum(v["total"] for v in coverage.values())
    documented = sum(v["documented"] for v in coverage.values())
    with REPORT_PATH.open("w", encoding="utf-8") as r:
        r.write("# Documentation Report\n\n")
        r.write("## Coverage Summary\n")
        r.write(f"- Modules processed: {len(coverage)}\n")
        r.write(f"- Symbols documented: {documented} / {total_symbols}\n\n")
        r.write("## Known Gaps (🚧 TODO)\n")
        if not gaps and not failures:
            r.write("- None\n")
        else:
            for g in gaps:
                r.write(f"- {g}\n")
            for fmsg in failures:
                r.write(f"- {fmsg}\n")
        r.write("\n## How to Regenerate API Docs\n")
        r.write("```bash\npython3 scripts/gen_api_docs.py\n```\n\n")
        r.write("## How to Publish\n")
        r.write("See README.md for GitHub Pages/Netlify/Cloudflare Pages.\n")
        r.write("\n\n## Traceability Map\n")
        r.write("Each API page embeds per-symbol source links. Summary below.\n\n")
        for modname in sorted(TRACE.keys()):
            r.write(f"### {modname}\n")
            modsrc = TRACE[modname].get("module_source")
            if modsrc:
                r.write(f"- Module: `{modsrc}`\n")
            classes = TRACE[modname].get("classes", {}) or {}
            funcs = TRACE[modname].get("functions", {}) or {}
            for cname, loc in classes.items():
                r.write(f"- {cname}: `{loc}`\n")
            for fname, loc in funcs.items():
                r.write(f"- {fname}(): `{loc}`\n")

    # Write index file to help navigation (optional)
    index_path = DOCS_DIR.parent / "modules-index.md"
    with index_path.open("w", encoding="utf-8") as idx:
        idx.write("---\n")
        idx.write("id: api-modules-index\n")
        idx.write("title: Modules Index\n")
        idx.write("slug: /api/python/modules\n")
        idx.write("---\n\n")
        for modname in modules:
            idx.write(f"- [{modname}](./modules/{modname}.mdx)\n")


if __name__ == "__main__":
    main()
