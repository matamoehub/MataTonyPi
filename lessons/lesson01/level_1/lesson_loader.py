#!/usr/bin/env python3
"""Notebook bootstrap helper for MataTonyPi lesson folders."""

from __future__ import annotations

from pathlib import Path
import importlib
import importlib.util
import os
import sys
from typing import Dict


COMMON_MODULES = [
    "student_robot_v2",
]


def _safe_start_dir() -> Path:
    try:
        return Path.cwd().resolve()
    except Exception:
        home = os.environ.get("HOME")
        if home and Path(home).is_dir():
            return Path(home).resolve()
        return Path("/tmp").resolve()


def _find_repo_root(start: Path) -> Path:
    p = start.resolve()
    for _ in range(30):
        if (p / "lessons").is_dir() and (p / "common").is_dir():
            return p
        if p.parent == p:
            break
        p = p.parent
    raise FileNotFoundError(f"Could not find lessons root from {start}")


def _resolve_common_lib(root: Path) -> Path:
    candidates = [
        Path("/opt/robot/students/lessons_cache/common/lib"),
        Path("/opt/robot/students/lesson_cache/common/lib"),
        root / "common" / "lib",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("Could not find common/lib")


def setup(verbose: bool = True):
    start = _safe_start_dir()
    try:
        os.chdir(str(start))
    except Exception:
        pass

    root = _find_repo_root(start)
    common_lib = _resolve_common_lib(root)
    lessons_lib = root / "lessons" / "lib"

    for path in (common_lib, lessons_lib):
        path_s = str(path)
        if path.exists() and path_s not in sys.path:
            sys.path.insert(0, path_s)

    if verbose:
        print(f"[lesson_loader] common_lib={common_lib}")
        print(f"[lesson_loader] lessons_lib={lessons_lib}")

    bootstrap_path = common_lib / "bootstrap.py"
    spec = importlib.util.spec_from_file_location("lesson_bootstrap", str(bootstrap_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load bootstrap from {bootstrap_path}")
    bootstrap = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bootstrap)
    info = bootstrap.bootstrap(verbose=verbose)

    loaded: Dict[str, object] = {}
    for name in COMMON_MODULES:
        loaded[name] = importlib.import_module(name)
    return {"bootstrap": info, "modules": loaded}
