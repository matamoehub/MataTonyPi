#!/usr/bin/env python3
"""Helpers for locating and using the vendor TonyPi runtime."""

from __future__ import annotations

import importlib
import os
import re
import sys
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "lessons").is_dir() and (parent / "common").is_dir():
            return parent
    return here.parents[2]


@lru_cache(maxsize=1)
def resolve_vendor_root() -> Path:
    candidates: list[Path] = []

    for env_name in (
        "MATA_TONYPI_VENDOR_DIR",
        "TONYPI_VENDOR_DIR",
        "HIWONDER_TONYPI_DIR",
        "ROBOT_LIB_REPO_DIR",
    ):
        value = str(os.environ.get(env_name, "")).strip()
        if not value:
            continue
        path = Path(value).expanduser()
        if env_name == "ROBOT_LIB_REPO_DIR":
            candidates.append(path / "TonyPi")
        else:
            candidates.append(path)

    candidates.extend(
        [
            Path("/opt/robot/TonyPi"),
            Path("/home/pi/TonyPi"),
            repo_root() / "vendor" / "TonyPi",
        ]
    )

    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate.resolve(strict=False))
        if key in seen:
            continue
        seen.add(key)
        if (candidate / "Functions").is_dir() or (candidate / "HiwonderSDK").is_dir():
            return candidate

    return candidates[-1]


def ensure_vendor_paths() -> Path:
    vendor = resolve_vendor_root()
    paths = [
        vendor,
        vendor / "Functions",
        vendor / "Functions" / "voice_interaction",
        vendor / "HiwonderSDK",
        vendor / "HiwonderSDK" / "hiwonder",
    ]
    for path in reversed(paths):
        value = str(path)
        if path.exists() and value not in sys.path:
            sys.path.insert(0, value)
    return vendor


def vendor_available() -> bool:
    vendor = ensure_vendor_paths()
    return vendor.exists()


def _import_any(module_names: Iterable[str]) -> Any:
    ensure_vendor_paths()
    last_error: Exception | None = None
    for module_name in module_names:
        try:
            return importlib.import_module(module_name)
        except Exception as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    raise ImportError("No module names provided")


@lru_cache(maxsize=1)
def get_action_group_module() -> Any | None:
    try:
        return _import_any(("hiwonder.ActionGroupControl", "ActionGroupControl"))
    except Exception:
        return None


@lru_cache(maxsize=1)
def get_board() -> Any | None:
    try:
        rrc = _import_any(("hiwonder.ros_robot_controller_sdk", "ros_robot_controller_sdk"))
        return rrc.Board()
    except Exception:
        return None


@lru_cache(maxsize=1)
def get_controller() -> Any | None:
    board = get_board()
    if board is None:
        return None
    try:
        controller_mod = _import_any(("hiwonder.Controller", "Controller"))
        controller_cls = getattr(controller_mod, "Controller", None)
        if controller_cls is None:
            return None
        return controller_cls(board)
    except Exception:
        return None


@lru_cache(maxsize=1)
def get_yaml_handle() -> Any | None:
    try:
        return _import_any(("hiwonder.yaml_handle", "yaml_handle"))
    except Exception:
        return None


@lru_cache(maxsize=1)
def get_servo_data() -> dict[str, Any]:
    yaml_handle = get_yaml_handle()
    if yaml_handle is None:
        return {}
    try:
        return dict(yaml_handle.get_yaml_data(yaml_handle.servo_file_path) or {})
    except Exception:
        return {}


def head_center() -> tuple[int, int]:
    servo_data = get_servo_data()
    vertical = int(servo_data.get("servo1", 1500))
    horizontal = int(servo_data.get("servo2", 1500))
    return vertical, horizontal


def set_head(vertical: int | None = None, horizontal: int | None = None, duration_ms: int = 300) -> dict[str, Any]:
    ctl = get_controller()
    board = get_board()
    center_vertical, center_horizontal = head_center()
    vertical = center_vertical if vertical is None else int(vertical)
    horizontal = center_horizontal if horizontal is None else int(horizontal)

    if ctl is not None:
        ctl.set_pwm_servo_pulse(1, vertical, int(duration_ms))
        ctl.set_pwm_servo_pulse(2, horizontal, int(duration_ms))
    elif board is not None:
        board.pwm_servo_set_position(float(duration_ms) / 1000.0, [[1, vertical], [2, horizontal]])
    else:
        raise RuntimeError("TonyPi head controller unavailable")

    return {"vertical": vertical, "horizontal": horizontal, "duration_ms": int(duration_ms)}


def run_action(name: str, times: int = 1, lock_servos: str = "") -> dict[str, Any]:
    agc = get_action_group_module()
    if agc is None:
        raise RuntimeError("TonyPi action group controller unavailable")
    runner = getattr(agc, "runActionGroup", None)
    if not callable(runner):
        raise RuntimeError("TonyPi action group runner unavailable")

    kwargs = {}
    if lock_servos:
        kwargs["lock_servos"] = lock_servos
    try:
        runner(str(name), int(times), **kwargs)
    except TypeError:
        runner(str(name), int(times))
    return {"action_group": str(name), "times": int(times)}


def stop_actions() -> None:
    agc = get_action_group_module()
    if agc is None:
        return
    for name in ("stopAction", "stopActionGroup", "stop_action_group"):
        fn = getattr(agc, name, None)
        if callable(fn):
            try:
                fn()
            except Exception:
                pass


def action_group_dir() -> Path:
    return resolve_vendor_root() / "ActionGroups"


@lru_cache(maxsize=1)
def list_action_groups() -> list[str]:
    root = action_group_dir()
    if not root.is_dir():
        return []
    return sorted(path.stem for path in root.iterdir() if path.is_file())


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def resolve_action_name(candidates: Iterable[str | tuple[str, ...]]) -> str | None:
    actions = list_action_groups()
    if not actions:
        return None

    normalized = {_normalize(name): name for name in actions}
    for candidate in candidates:
        if isinstance(candidate, tuple):
            continue
        exact = normalized.get(_normalize(candidate))
        if exact is not None:
            return exact

    for candidate in candidates:
        if isinstance(candidate, tuple):
            tokens = [_normalize(part) for part in candidate if _normalize(part)]
        else:
            tokens = [_normalize(candidate)]
        for action in actions:
            norm = _normalize(action)
            if all(token in norm for token in tokens):
                return action
    return None


def say(text: str, block: bool = True) -> Any:
    ensure_vendor_paths()
    for module_name in ("tts_lib",):
        try:
            mod = importlib.import_module(module_name)
        except Exception:
            continue
        for fn_name in ("say", "speak"):
            fn = getattr(mod, fn_name, None)
            if callable(fn):
                return fn(str(text), block=bool(block))
    raise RuntimeError("TonyPi speech backend unavailable")


def sleep(seconds: float) -> None:
    time.sleep(float(seconds))

