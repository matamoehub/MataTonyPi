#!/usr/bin/env python3
"""Navigation library for MataTonyPi."""
__version__ = "1.0.0"
from __future__ import annotations
import copy
import threading
import time
from typing import Any
from tonypi_support import ensure_vendor_paths, run_action, get_board, get_controller, head_center

# ── AprilTag nav ───────────────────────────────────────────────────────────────

_tag_map: dict[int, dict] = {}
_tag_lock = threading.Lock()
_nav_thread: threading.Thread | None = None
_nav_stop = threading.Event()

FRAME_W, FRAME_H = 640, 480
CENTRE_LOW, CENTRE_HIGH = 280, 360
ARRIVED_AREA_FRAC = 0.30


def update_tag_map(tag_id: int, cx: int, cy: int, area: float):
    with _tag_lock:
        _tag_map[int(tag_id)] = {
            "center_x": int(cx), "center_y": int(cy),
            "area": float(area), "last_seen": time.time(),
        }


def get_tag_map() -> dict:
    with _tag_lock:
        return copy.deepcopy(_tag_map)


def navigate_to_tag(tag_id: int, timeout: float = 10.0) -> dict[str, Any]:
    """Non-blocking: start a daemon thread to navigate toward tag_id."""
    def _nav():
        deadline = time.time() + float(timeout)
        search_steps = 0
        while time.time() < deadline and not _nav_stop.is_set():
            with _tag_lock:
                info = _tag_map.get(int(tag_id))
                fresh = info and (time.time() - info["last_seen"]) < 3.0

            if fresh:
                search_steps = 0
                cx   = info["center_x"]
                area = info["area"]
                arrived_area = ARRIVED_AREA_FRAC * FRAME_W * FRAME_H

                if area >= arrived_area:
                    print(f"[navigation_lib] Arrived at tag {tag_id}")
                    break
                elif cx < CENTRE_LOW:
                    run_action("turn_left_small_step")
                elif cx > CENTRE_HIGH:
                    run_action("turn_right_small_step")
                else:
                    run_action("go_forward_one_step")
                time.sleep(0.4)
            else:
                # Search: rotate right
                if search_steps >= 20:
                    print(f"[navigation_lib] Tag {tag_id} not found after search")
                    break
                run_action("turn_right_small_step")
                search_steps += 1
                time.sleep(0.5)

    _nav_stop.clear()
    th = threading.Thread(target=_nav, daemon=True, name=f"NavTag{tag_id}")
    th.start()
    return {"ok": True, "tag_id": tag_id, "timeout": timeout}


def stop_navigation():
    _nav_stop.set()


# ── Person following (YOLOv8n) ─────────────────────────────────────────────────

_follow_stop = threading.Event()


def follow_person(tof_min_mm: int = 350, tof_max_mm: int = 650) -> dict[str, Any]:
    """Non-blocking: follow a person using YOLOv8n + ToF distance gating."""
    from yolo_lib import find_class, is_available as yolo_ok
    from sensor_lib import get_distance

    if not yolo_ok():
        return {"ok": False, "note": "YOLOv8n not available — pip install ultralytics"}

    def _follow():
        import vision_lib
        ctl = get_controller()
        board = get_board()
        center_v, center_h = head_center()

        while not _follow_stop.is_set():
            vision = vision_lib.get_vision()
            frame = vision._capture_frame()
            person = find_class(frame, "person")
            dist = get_distance()

            if person is None:
                time.sleep(0.1)
                continue

            cx = person["cx"]
            too_close = (dist != -1 and dist < tof_min_mm)
            close_range = (dist != -1 and tof_min_mm <= dist <= tof_max_mm)

            # Head tracking — always follows the person
            err_x = cx - FRAME_W // 2
            new_h = center_h - int(err_x * 0.5)
            new_h = max(500, min(2500, new_h))
            if ctl:
                try: ctl.set_pwm_servo_pulse(2, new_h, 200)
                except Exception as e: print(f"[navigation_lib] head pan: {e}")

            # Body motion
            if too_close:
                pass  # hold
            elif close_range:
                pass  # head tracking only
            else:
                if cx < CENTRE_LOW:
                    run_action("turn_left_small_step")
                elif cx > CENTRE_HIGH:
                    run_action("turn_right_small_step")
                else:
                    run_action("go_forward_one_step")

            time.sleep(0.15)

    _follow_stop.clear()
    th = threading.Thread(target=_follow, daemon=True, name="FollowPerson")
    th.start()
    return {"ok": True, "note": "Following person"}


def stop_follow():
    _follow_stop.set()
