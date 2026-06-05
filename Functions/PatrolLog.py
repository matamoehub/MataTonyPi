#!/usr/bin/python3
# coding=utf8

import os
import cv2
import json
import time
import datetime
import threading
import urllib.request
import hiwonder.ros_robot_controller_sdk as rrc
import hiwonder.ActionGroupControl as AGC
from hiwonder.Controller import Controller

board = rrc.Board()
ctl = Controller(board)

try:
    import VL53L0X
    _TOF_AVAILABLE = True
except Exception:
    _TOF_AVAILABLE = False

LOG_DIR = '/home/pi/TonyPi/patrol_logs'

_running = False
_frame_index = 0
_current_frame = None
_frame_lock = threading.Lock()

_tof = None
_tof_distance = 1000
_tof_thread = None

_obstacle_log = []
_log_lock = threading.Lock()
_obstacle_thread = None

_line_cx = None  # centre x of detected line


def _ensure_log_dir():
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception as e:
        print(f'[PatrolLog] Could not create log dir: {e}')


def init():
    global _tof
    _ensure_log_dir()
    if _TOF_AVAILABLE:
        try:
            _tof = VL53L0X.VL53L0X(i2c_bus=1, i2c_address=0x29)
            _tof.open()
            _tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)
        except Exception as e:
            print(f'[PatrolLog] ToF init error: {e}')


def start():
    global _running, _obstacle_log, _tof_thread, _obstacle_thread, _frame_index
    _running = True
    _frame_index = 0

    with _log_lock:
        _obstacle_log.clear()

    if _TOF_AVAILABLE and _tof is not None:
        if _tof_thread is None or not _tof_thread.is_alive():
            _tof_thread = threading.Thread(target=_tof_loop, daemon=True)
            _tof_thread.start()

    if _obstacle_thread is None or not _obstacle_thread.is_alive():
        _obstacle_thread = threading.Thread(target=_obstacle_check_loop, daemon=True)
        _obstacle_thread.start()


def stop():
    global _running
    _running = False

    # Save log
    _save_log()


def exit():
    global _tof
    if _tof is not None:
        try:
            _tof.stop_ranging()
            _tof.close()
        except Exception as e:
            print(e)
        _tof = None
    AGC.runActionGroup('stand_slow')


def _tof_loop():
    global _tof_distance
    while _running:
        if _tof is not None:
            try:
                dist = _tof.get_distance()
                if dist > 0:
                    _tof_distance = dist
            except Exception as e:
                print(e)
        time.sleep(0.1)


def _obstacle_check_loop():
    while _running:
        if _tof_distance < 400:
            # Log obstacle
            with _frame_lock:
                frame = _current_frame.copy() if _current_frame is not None else None

            entry = {
                'time': time.time(),
                'distance_mm': _tof_distance,
                'frame_index': _frame_index
            }
            with _log_lock:
                _obstacle_log.append(entry)

            print(f'[PatrolLog] Obstacle at {_tof_distance}mm (frame {_frame_index})')

            # Save snapshot
            if frame is not None:
                snapshot_path = os.path.join(LOG_DIR, f'snapshot_{int(time.time())}.jpg')
                try:
                    cv2.imwrite(snapshot_path, frame)
                except Exception as e:
                    print(f'[PatrolLog] Snapshot save error: {e}')

            # Avoidance manoeuvre
            try:
                AGC.runActionGroup('back_fast')
                time.sleep(0.5)
                AGC.runActionGroup('turn_right')
                time.sleep(0.5)
                AGC.runActionGroup('turn_right')
                time.sleep(0.5)
                AGC.runActionGroup('go_forward')
            except Exception as e:
                print(e)

        time.sleep(0.2)


def _detect_line(img):
    """Detect black line centroid via HSV thresholding."""
    try:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, 80))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None, mask
        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) < 500:
            return None, mask
        M = cv2.moments(largest)
        if M['m00'] == 0:
            return None, mask
        cx = int(M['m10'] / M['m00'])
        return cx, mask
    except Exception as e:
        print(e)
        return None, None


def _steer_to_line(cx, img_width=640):
    """Simple bang-bang steering based on line centroid."""
    centre = img_width // 2
    dead = 40
    try:
        if cx < centre - dead:
            AGC.runActionGroup('turn_left_small_step')
        elif cx > centre + dead:
            AGC.runActionGroup('turn_right_small_step')
        else:
            AGC.runActionGroup('go_forward_one_step')
    except Exception as e:
        print(e)


def _summarise_with_claude(log_entries):
    """POST log summary to Claude API. Returns summary string."""
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return None

    summary_data = {
        'obstacle_count': len(log_entries),
        'patrol_duration_s': (log_entries[-1]['time'] - log_entries[0]['time']) if len(log_entries) > 1 else 0,
        'distances_mm': [e['distance_mm'] for e in log_entries],
    }

    prompt_text = (
        f"Summarise this robot patrol log in 2 sentences for a non-technical user. "
        f"Focus on how many obstacles were found and whether the patrol was successful.\n\n"
        f"Log data: {json.dumps(summary_data)}"
    )

    payload = {
        "model": "claude-opus-4-5",
        "max_tokens": 150,
        "messages": [{"role": "user", "content": prompt_text}]
    }

    try:
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(payload).encode(),
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data["content"][0]["text"]
    except Exception as e:
        print(f'[PatrolLog] Claude summary error: {e}')
        return None


def _save_log():
    with _log_lock:
        log_copy = list(_obstacle_log)

    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = os.path.join(LOG_DIR, f'patrol_{ts}.json')

    try:
        with open(log_path, 'w') as f:
            json.dump(log_copy, f, indent=2)
        print(f'[PatrolLog] Saved log to {log_path}')
    except Exception as e:
        print(f'[PatrolLog] Log save error: {e}')

    if log_copy:
        summary = _summarise_with_claude(log_copy)
        if summary:
            print(f'[PatrolLog] Summary: {summary}')
            safe = summary.replace('"', "'").replace('`', "'").replace('$', '')
            try:
                os.system(f'espeak-ng "{safe}"')
            except Exception as e:
                print(e)


def run(img):
    global _frame_index, _current_frame, _line_cx

    if img is None:
        return img

    _frame_index += 1
    with _frame_lock:
        _current_frame = img.copy()

    cx, mask = _detect_line(img)
    _line_cx = cx

    if _running and cx is not None:
        _steer_to_line(cx, img.shape[1])
        cv2.circle(img, (cx, img.shape[0] - 30), 8, (0, 255, 0), -1)

    obstacle_count = len(_obstacle_log)
    cv2.putText(img, f'PatrolLog | Obstacles: {obstacle_count}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.putText(img, f'ToF: {_tof_distance}mm', (10, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    return img
