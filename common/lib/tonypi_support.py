#!/usr/bin/env python3
"""Helpers for locating and using the vendor TonyPi runtime."""

from __future__ import annotations

import importlib
import os
import re
import shutil
import site
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable


DEFAULT_PIPER_VOICE = "amy"
PIPER_VOICE_ENV = "MATA_PIPER_VOICE"
PIPER_VOICE_DIR = Path("/opt/robot/piper/voices")
PIPER_VOICE_MAP = {
    "amy": "en_US-amy-medium.onnx",
    "ryan": "en_US-ryan-high.onnx",
    "alan": "en_GB-alan-medium.onnx",
    "alba": "en_GB-alba-medium.onnx",
    "cori": "en_GB-cori-medium.onnx",
    "jenny": "en_GB-jenny_dioco-medium.onnx",
    "southern": "en_GB-southern_english_female-low.onnx",
    "bryce": "en_US-bryce-medium.onnx",
    "kristin": "en_US-kristin-medium.onnx",
}


def _preferred_audio_device() -> str | None:
    env_device = str(os.environ.get("MATA_AUDIO_DEVICE", "")).strip()
    if env_device:
        return env_device

    try:
        result = subprocess.run(["aplay", "-l"], capture_output=True, text=True, check=False)
    except Exception:
        return None

    lines = result.stdout.splitlines()
    usb_candidate = None
    first_candidate = None
    for line in lines:
        line = line.strip()
        if not line.startswith("card "):
            continue
        try:
            card_part, device_part = line.split(",", 1)
            card_num = int(card_part.split()[1].rstrip(":"))
            device_num = int(device_part.split("device", 1)[1].split(":", 1)[0].strip())
        except Exception:
            continue

        device = f"plughw:{card_num},{device_num}"
        if first_candidate is None:
            first_candidate = device
        if "USB" in line or "Audio Device" in line:
            usb_candidate = device
            break

    return usb_candidate or first_candidate


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
    user_site_candidates = []
    try:
        user_site = Path(site.getusersitepackages())
        user_site_candidates.append(user_site)
    except Exception:
        pass
    user_site_candidates.append(Path.home() / ".local" / f"lib/python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages")
    paths = [
        Path("/usr/lib/python3/dist-packages"),
        Path(f"/usr/local/lib/python{sys.version_info.major}.{sys.version_info.minor}/dist-packages"),
        Path(f"/usr/lib/python{sys.version_info.major}/dist-packages"),
        *user_site_candidates,
        vendor,
        vendor / "Functions",
        vendor / "Functions" / "voice_interaction",
        vendor / "HiwonderSDK",
        vendor / "HiwonderSDK" / "hiwonder",
    ]
    for path in reversed(paths):
        value = str(path)
        if not path.exists():
            continue
        if "dist-packages" in value or value.endswith("site-packages"):
            site.addsitedir(value)
        elif value not in sys.path:
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
def get_action_group_dict() -> dict[str, str]:
    try:
        mod = _import_any(("ActionGroupDict",))
        data = getattr(mod, "action_group_dict", None)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
    except Exception:
        pass
    return {}


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
    env_vertical = str(os.environ.get("MATA_HEAD_CENTER_VERTICAL", "")).strip()
    env_horizontal = str(os.environ.get("MATA_HEAD_CENTER_HORIZONTAL", "")).strip()
    if env_vertical or env_horizontal:
        return (
            int(env_vertical or 1500),
            int(env_horizontal or 1500),
        )

    # TonyPi's upstream RPC layer expects logical PWM centers of 1500 for
    # both channels. It only applies the yaml calibration offset to servo 2.
    return 1500, 1500


def _head_physical_pulses(vertical: int, horizontal: int) -> tuple[int, int]:
    servo_data = get_servo_data()
    vertical = int(vertical)
    horizontal = int(horizontal)
    horizontal = horizontal + int(servo_data.get("servo2", 1500)) - 1500
    return vertical, horizontal


def set_head(vertical: int | None = None, horizontal: int | None = None, duration_ms: int = 300) -> dict[str, Any]:
    ctl = get_controller()
    board = get_board()
    center_vertical, center_horizontal = head_center()
    vertical = center_vertical if vertical is None else int(vertical)
    horizontal = center_horizontal if horizontal is None else int(horizontal)
    physical_vertical, physical_horizontal = _head_physical_pulses(vertical, horizontal)

    if ctl is not None:
        ctl.set_pwm_servo_pulse(1, physical_vertical, int(duration_ms))
        ctl.set_pwm_servo_pulse(2, physical_horizontal, int(duration_ms))
    elif board is not None:
        board.pwm_servo_set_position(
            float(duration_ms) / 1000.0,
            [[1, physical_vertical], [2, physical_horizontal]],
        )
    else:
        raise RuntimeError("TonyPi head controller unavailable")

    return {
        "vertical": vertical,
        "horizontal": horizontal,
        "physical_vertical": physical_vertical,
        "physical_horizontal": physical_horizontal,
        "duration_ms": int(duration_ms),
    }


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
        return sorted(set(get_action_group_dict().values()))
    names = {path.stem for path in root.iterdir() if path.is_file()}
    names.update(get_action_group_dict().values())
    return sorted(names)


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


def action_name_for_id(action_id: str | int) -> str | None:
    token = str(action_id).strip()
    available = set(list_action_groups())
    if token in available:
        return token
    return get_action_group_dict().get(token)


def _action_category(name: str, action_id: str | None = None) -> str:
    token = _normalize(name)
    if action_id is not None:
        try:
            idx = int(action_id)
            if 16 <= idx <= 24:
                return "dance"
        except Exception:
            pass

    if any(part in token for part in ("dance", "twist", "stepping", "chest", "weightlifting")):
        return "dance"
    if any(part in token for part in ("forward", "back", "move", "turn", "walk", "step")):
        return "motion"
    if any(part in token for part in ("wave", "bow", "greet", "hello")):
        return "greeting"
    if any(part in token for part in ("kick", "shot", "shoot")):
        return "sport"
    if any(part in token for part in ("grab", "pickup", "carry", "release", "place", "transport", "catch")):
        return "pickup"
    if any(part in token for part in ("stand", "sit", "squat", "rest", "ready", "home")):
        return "pose"
    return "action"


def action_group_catalog() -> list[dict[str, Any]]:
    names = list_action_groups()
    id_map = get_action_group_dict()
    name_to_ids: dict[str, list[str]] = {}
    for action_id, name in id_map.items():
        name_to_ids.setdefault(str(name), []).append(str(action_id))

    catalog: list[dict[str, Any]] = []
    for name in names:
        ids = sorted(name_to_ids.get(str(name), []), key=lambda item: int(item) if item.isdigit() else item)
        primary_id = ids[0] if ids else None
        catalog.append(
            {
                "name": str(name),
                "ids": ids,
                "id": primary_id,
                "category": _action_category(str(name), primary_id),
            }
        )
    return catalog


def dance_action_groups() -> list[dict[str, Any]]:
    return [item for item in action_group_catalog() if item["category"] == "dance"]


def _resolve_piper_binary() -> str | None:
    candidates = [
        "/home/pi/.local/bin/piper",
        shutil.which("piper"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


def available_voices(installed_only: bool = True) -> list[str]:
    voices = list(PIPER_VOICE_MAP.keys())
    if not installed_only:
        return voices
    return [name for name in voices if (PIPER_VOICE_DIR / PIPER_VOICE_MAP[name]).exists()]


def resolve_voice_name(voice: str | None = None) -> str:
    token = str(voice or os.environ.get(PIPER_VOICE_ENV) or DEFAULT_PIPER_VOICE).strip().lower()
    if token.isdigit():
        voices = available_voices(installed_only=True)
        idx = int(token)
        if not voices:
            voices = available_voices(installed_only=False)
        if idx < 1 or idx > len(voices):
            raise ValueError(f"Voice number out of range: {idx} (1..{len(voices)})")
        return voices[idx - 1]
    if token not in PIPER_VOICE_MAP:
        voices = available_voices(installed_only=False)
        raise ValueError(f"Unknown voice '{token}'. Available: {voices}")
    return token


def _resolve_piper_model(voice: str | None = None) -> str | None:
    candidates = []
    env_model = str(os.environ.get("MATA_PIPER_MODEL", "")).strip()
    if env_model:
        candidates.append(Path(env_model).expanduser())

    try:
        selected = resolve_voice_name(voice)
        candidates.append(PIPER_VOICE_DIR / PIPER_VOICE_MAP[selected])
    except Exception:
        pass

    preferred = [PIPER_VOICE_MAP[name] for name in ("amy", "ryan", "alan") if name in PIPER_VOICE_MAP]
    candidates.extend(PIPER_VOICE_DIR / name for name in preferred)
    candidates.extend(sorted(PIPER_VOICE_DIR.glob("*.onnx")) if PIPER_VOICE_DIR.is_dir() else [])

    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        if candidate.exists():
            return str(candidate)
    return None


def _say_with_piper(text: str, block: bool = True, voice: str | None = None) -> Any:
    piper_bin = _resolve_piper_binary()
    selected = resolve_voice_name(voice)
    model = _resolve_piper_model(selected)
    if not piper_bin or not model:
        raise RuntimeError("Piper binary or model unavailable")

    output_file = Path("/tmp") / f"matatonypi_{int(time.time() * 1000)}.wav"
    with subprocess.Popen(
        [piper_bin, "--model", model, "--output_file", str(output_file)],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    ) as proc:
        proc.communicate(str(text))
        if proc.returncode not in (0, None):
            raise RuntimeError(f"Piper failed with code {proc.returncode}")

    player = shutil.which("aplay") or shutil.which("paplay") or shutil.which("ffplay")
    if player is None:
        return {"cmd": piper_bin, "model": model, "output_file": str(output_file)}

    player_name = Path(player).name
    if player_name == "ffplay":
        play_cmd = [player, "-nodisp", "-autoexit", str(output_file)]
    elif player_name == "aplay":
        device = _preferred_audio_device()
        play_cmd = [player]
        if device:
            play_cmd.extend(["-D", device])
        play_cmd.append(str(output_file))
    else:
        play_cmd = [player, str(output_file)]

    if block:
        completed = subprocess.run(play_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if completed.returncode != 0:
            raise RuntimeError(
                f"Audio playback failed with code {completed.returncode}: {completed.stderr.strip()}"
            )
    else:
        subprocess.Popen(play_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {
        "cmd": piper_bin,
        "model": model,
        "voice": selected,
        "output_file": str(output_file),
        "player": player,
        "audio_device": _preferred_audio_device(),
    }


def say(text: str, block: bool = True, voice: str | None = None) -> Any:
    ensure_vendor_paths()
    try:
        return _say_with_piper(text=str(text), block=bool(block), voice=voice)
    except Exception:
        pass

    local_tts = Path(__file__).resolve().parent / "tts_lib.py"
    for module_name in ("tts_lib", "voice_interaction.tts", "voice_interaction.tts_node"):
        try:
            mod = importlib.import_module(module_name)
        except Exception:
            continue
        mod_file = Path(getattr(mod, "__file__", "")).resolve(strict=False) if getattr(mod, "__file__", None) else None
        if mod_file == local_tts:
            continue
        for fn_name in ("say", "speak"):
            fn = getattr(mod, fn_name, None)
            if callable(fn):
                try:
                    return fn(str(text), voice=voice, block=bool(block))
                except TypeError:
                    return fn(str(text), block=bool(block))

    for cmd in ("espeak-ng", "espeak", "spd-say"):
        if not shutil.which(cmd):
            continue
        proc = subprocess.Popen([cmd, str(text)])
        if block:
            proc.wait()
        return {"cmd": cmd, "text": str(text)}

    raise RuntimeError("TonyPi speech backend unavailable")


def sleep(seconds: float) -> None:
    time.sleep(float(seconds))
