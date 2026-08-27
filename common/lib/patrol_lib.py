#!/usr/bin/env python3
"""Patrol library for MataTonyPi."""
from __future__ import annotations
__version__ = "1.0.0"
import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from tonypi_support import run_action
from sensor_lib import get_distance
import llm_lib

LOG_DIR = Path("/home/pi/TonyPi/patrol_logs")

_log: list[dict] = []
_frame_index: int = 0
_current_frame = None
_running = False
_frame_lock = threading.Lock()
_log_lock = threading.Lock()


def _ensure_log_dir():
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[patrol_lib] log dir error: {e}")


def update_frame(frame):
    global _frame_index, _current_frame
    with _frame_lock:
        _current_frame = frame
        _frame_index += 1


def _obstacle_thread():
    import cv2
    while _running:
        time.sleep(0.2)
        dist = get_distance()
        if dist == -1 or dist >= 400:
            continue
        # Log obstacle
        ts = time.time()
        with _frame_lock:
            fi = _frame_index
            frame_copy = _current_frame.copy() if _current_frame is not None else None
        entry = {"time": ts, "distance_mm": dist, "frame_index": fi}
        with _log_lock:
            _log.append(entry)
        print(f"[patrol_lib] Obstacle at {dist}mm (frame {fi})")
        # Snapshot
        if frame_copy is not None:
            _ensure_log_dir()
            snap_path = str(LOG_DIR / f"snapshot_{int(ts)}.jpg")
            try:
                cv2.imwrite(snap_path, frame_copy)
            except Exception as e:
                print(f"[patrol_lib] snapshot error: {e}")
        # Avoid
        try:
            run_action("back_fast")
            time.sleep(0.5)
            run_action("turn_right"); time.sleep(0.8)
            run_action("turn_right"); time.sleep(0.8)
            run_action("go_forward")
        except Exception as e:
            print(f"[patrol_lib] avoidance error: {e}")


def start():
    global _running, _log
    _log = []
    _running = True
    th = threading.Thread(target=_obstacle_thread, daemon=True, name="PatrolObstacle")
    th.start()
    return {"ok": True}


def stop() -> dict[str, Any]:
    global _running
    _running = False
    with _log_lock:
        log_copy = list(_log)

    _ensure_log_dir()
    dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / f"patrol_{dt_str}.json"
    try:
        with open(str(log_path), "w") as f:
            json.dump(log_copy, f, indent=2)
        print(f"[patrol_lib] Log saved: {log_path}")
    except Exception as e:
        print(f"[patrol_lib] log save error: {e}")

    summary = _get_summary(log_copy)
    return {"ok": True, "obstacles": len(log_copy), "log_path": str(log_path), "summary": summary}


def get_log() -> list[dict]:
    with _log_lock:
        return list(_log)


def _get_summary(log: list) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or not log:
        n = len(log)
        return f"Patrol complete. {n} obstacle{'s' if n != 1 else ''} detected."
    try:
        import json as _json
        prompt = (f"Summarise this robot patrol log in 2 sentences for a non-technical user. "
                  f"Focus on how many obstacles were found and whether the patrol was successful.\n\n"
                  f"{_json.dumps(log)}")
        payload = {
            "max_tokens": 150,
            "messages": [{"role": "user", "content": prompt}],
        }
        return llm_lib.call_claude(payload, api_key=api_key)
    except Exception as e:
        print(f"[patrol_lib] summary error: {e}")
        n = len(log)
        return f"Patrol complete. {n} obstacle{'s' if n != 1 else ''} detected."
