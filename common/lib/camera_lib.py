#!/usr/bin/env python3
"""Minimal TonyPi camera helper."""

from __future__ import annotations

import importlib
from typing import Any, Optional

from tonypi_support import ensure_vendor_paths

_CAMERA: Optional["CameraWrapper"] = None


class CameraWrapper:
    def __init__(self, backend: Any):
        self._backend = backend

    def __getattr__(self, name: str):
        backend = self.__dict__.get("_backend")
        if backend is None:
            raise AttributeError(f"Camera backend unavailable ({name})")
        return getattr(backend, name)


def get_camera() -> "CameraWrapper":
    global _CAMERA
    if _CAMERA is not None:
        return _CAMERA
    ensure_vendor_paths()
    for module_name in ("hiwonder.Camera", "Camera"):
        try:
            mod = importlib.import_module(module_name)
        except Exception:
            continue
        camera_cls = getattr(mod, "Camera", None)
        if camera_cls is None:
            continue
        _CAMERA = CameraWrapper(camera_cls())
        return _CAMERA
    raise RuntimeError("TonyPi camera backend unavailable")
