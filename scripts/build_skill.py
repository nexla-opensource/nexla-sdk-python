#!/usr/bin/env python3
"""Build nexla.skill from skills/nexla/. The skills/ tree is the only source.

Usage:
    python scripts/build_skill.py          # rewrite nexla.skill
    python scripts/build_skill.py --check  # exit 1 if nexla.skill differs

The archive holds one top-level folder, nexla/, as the skill loader expects.
Entries have a fixed timestamp and sorted order, so a rebuild from the same
source gives the same archive. --check compares member names and bytes, not
raw zip bytes, so it does not depend on the zlib version.
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import zipfile
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "skills" / "nexla"
OUTPUT = ROOT / "nexla.skill"
ARCHIVE_ROOT = "nexla"
# ZIP stores no timezone and cannot store dates before 1980.
FIXED_DATE_TIME = (1980, 1, 1, 0, 0, 0)


def source_files() -> List[Path]:
    return sorted(
        path
        for path in SOURCE_DIR.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and not path.name.startswith(".")
        and path.suffix != ".pyc"
    )


def arcname(path: Path) -> str:
    return f"{ARCHIVE_ROOT}/{path.relative_to(SOURCE_DIR).as_posix()}"


def build_members(files: List[Path]) -> Dict[str, bytes]:
    """Return archive member name -> file bytes."""
    return {arcname(path): path.read_bytes() for path in files}


def build_archive(files: List[Path]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            info = zipfile.ZipInfo(arcname(path), date_time=FIXED_DATE_TIME)
            mode = 0o755 if os.access(path, os.X_OK) else 0o644
            info.external_attr = (0o100000 | mode) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    return buffer.getvalue()


def committed_members() -> Dict[str, bytes]:
    with zipfile.ZipFile(OUTPUT) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if nexla.skill does not match skills/nexla/ (writes nothing)",
    )
    args = parser.parse_args()

    files = source_files()
    members = build_members(files)
    if args.check:
        if not OUTPUT.exists():
            print(
                f"{OUTPUT.name} is missing. Run: python scripts/build_skill.py",
                file=sys.stderr,
            )
            return 1
        if committed_members() != members:
            print(
                f"{OUTPUT.name} is out of sync with skills/nexla/. "
                "Run: python scripts/build_skill.py, then commit nexla.skill.",
                file=sys.stderr,
            )
            return 1
        print(f"{OUTPUT.name} matches skills/nexla/ ({len(members)} files).")
        return 0

    OUTPUT.write_bytes(build_archive(files))
    print(f"Wrote {OUTPUT} with {len(members)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
