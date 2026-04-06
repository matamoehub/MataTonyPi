#!/usr/bin/env python3
"""Minimal TonyPi camera helper."""

from __future__ import annotations

import importlib
from typing import Any

from tonypi_support import ensure_vendor_paths


class CameraWrapper:
    def __init__(self, backend: Any):
        self._backend = backend

    def __getattr__(self, name: str):
        return getattr(self._backend, name)


def get_camera():
    ensure_vendor_paths()
    for module_name in ("hiwonder.Camera", "Camera"):
        try:
            mod = importlib.import_module(module_name)
        except Exception:
            continue
        camera_cls = getattr(mod, "Camera", None)
        if camera_cls is None:
            continue
        return CameraWrapper(camera_cls())
    raise RuntimeError("TonyPi camera backend unavailable")
