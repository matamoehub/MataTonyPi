"""Lesson 16 Level 1 loader."""

from __future__ import annotations

from pathlib import Path
import sys


def _find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "common" / "lib").exists() and (candidate / "lessons" / "lib").exists():
            return candidate
    raise RuntimeError("Could not find MataTonyPi repo root from lesson16 loader")


def setup(verbose: bool = False) -> dict[str, str]:
    start = Path.cwd()
    root = _find_repo_root(start)
    common_lib = root / "common" / "lib"
    lessons_lib = root / "lessons" / "lib"

    for path in [str(lessons_lib), str(common_lib)]:
        if path not in sys.path:
            sys.path.insert(0, path)

    info = {
        "start": str(start),
        "root": str(root),
        "common_lib": str(common_lib),
        "lessons_lib": str(lessons_lib),
    }

    if verbose:
        print(f"[lesson_loader] start={info['start']}")
        print(f"[lesson_loader] root={info['root']}")
        print(f"[lesson_loader] common_lib={info['common_lib']}")
        print(f"[lesson_loader] lessons_lib={info['lessons_lib']}")

    return info
