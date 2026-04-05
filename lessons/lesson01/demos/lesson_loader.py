#!/usr/bin/env python3
"""Demo notebook bootstrap helper for MataTonyPi lesson folders."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def setup(verbose: bool = True):
    here = Path(__file__).resolve()
    level_loader = here.parents[1] / "level_1" / "lesson_loader.py"
    spec = importlib.util.spec_from_file_location("lesson01_level_loader", str(level_loader))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load lesson loader from {level_loader}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.setup(verbose=verbose)
