#!/usr/bin/env python3
"""Emotion expression library for MataTonyPi."""
__version__ = "1.0.0"
from __future__ import annotations
import threading
import time
from typing import Any
from tonypi_support import ensure_vendor_paths, get_board, get_controller, run_action

# Arm servo IDs
L_SHOULDER, L_ELBOW, R_SHOULDER, R_ELBOW = 7, 6, 15, 14

# Pulse values
NEUTRAL, HALF_UP, FULL_UP, DROPPED = 500, 650, 800, 350

_busy = threading.Event()   # set = currently expressing
_lock = threading.Lock()


def _bus(duration_ms: int, positions: list):
    """Move bus servos. positions = [[id, pulse], ...]"""
    board = get_board()
    if board is None:
        return
    try:
        board.bus_servo_set_position(int(duration_ms), positions)
    except Exception as e:
        print(f"[emotion_lib] bus servo error: {e}")


def _pwm(servo_id: int, pulse: int, duration_ms: int = 300):
    ctl = get_controller()
    board = get_board()
    if ctl is not None:
        try:
            ctl.set_pwm_servo_pulse(int(servo_id), int(pulse), int(duration_ms))
        except Exception as e:
            print(f"[emotion_lib] pwm error: {e}")
    elif board is not None:
        try:
            board.pwm_servo_set_position(duration_ms / 1000.0, [[int(servo_id), int(pulse)]])
        except Exception as e:
            print(f"[emotion_lib] pwm error: {e}")


def _buzz(freq: int, on_s: float, off_s: float, repeat: int):
    board = get_board()
    if board is None:
        return
    try:
        board.set_buzzer(int(freq), float(on_s), float(off_s), int(repeat))
    except Exception as e:
        print(f"[emotion_lib] buzzer error: {e}")


def _arms_neutral():
    _bus(400, [[L_SHOULDER, NEUTRAL], [L_ELBOW, NEUTRAL], [R_SHOULDER, NEUTRAL], [R_ELBOW, NEUTRAL]])


def _head_centre():
    _pwm(1, 1500, 300)
    _pwm(2, 1500, 300)


# --- Individual emotion implementations ---

def _happy():
    try:
        _bus(500, [[L_SHOULDER, HALF_UP], [L_ELBOW, HALF_UP], [R_SHOULDER, HALF_UP], [R_ELBOW, HALF_UP]])
        time.sleep(0.6)
        for _ in range(2):
            _pwm(1, 1700, 200); time.sleep(0.25)
            _pwm(1, 1300, 200); time.sleep(0.25)
        _pwm(1, 1500, 200)
        _buzz(1800, 0.1, 0.05, 1); time.sleep(0.2)
        _buzz(2000, 0.1, 0.05, 1)
        time.sleep(0.4)
        _arms_neutral()
    except Exception as e:
        print(f"[emotion_lib] happy error: {e}")


def _sad():
    try:
        _bus(600, [[L_SHOULDER, DROPPED], [L_ELBOW, DROPPED], [R_SHOULDER, DROPPED], [R_ELBOW, DROPPED]])
        _pwm(1, 1200, 400)
        time.sleep(0.5)
        _buzz(600, 0.4, 0.1, 1)
        time.sleep(1.0)
        _arms_neutral(); _head_centre()
    except Exception as e:
        print(f"[emotion_lib] sad error: {e}")


def _excited():
    try:
        run_action("wave", times=1)
        for _ in range(4):
            _buzz(2000, 0.05, 0.05, 1); time.sleep(0.12)
    except Exception as e:
        print(f"[emotion_lib] excited error: {e}")


def _confused():
    try:
        _pwm(2, 1800, 300); time.sleep(0.7)
        _pwm(2, 1200, 300); time.sleep(0.7)
        _head_centre()
        _buzz(1200, 0.2, 0.05, 1)
    except Exception as e:
        print(f"[emotion_lib] confused error: {e}")


def _greet():
    try:
        run_action("wave", times=1)
        _buzz(1500, 0.1, 0.05, 1)
    except Exception as e:
        print(f"[emotion_lib] greet error: {e}")


_EMOTIONS = {
    "happy": _happy,
    "sad": _sad,
    "excited": _excited,
    "confused": _confused,
    "greet": _greet,
}


def express(emotion: str) -> dict[str, Any]:
    """Express an emotion non-blocking. Returns immediately."""
    ensure_vendor_paths()
    name = str(emotion).strip().lower()
    if name not in _EMOTIONS:
        return {"ok": False, "note": f"Unknown emotion '{emotion}'. Available: {list(_EMOTIONS)}"}
    if _busy.is_set():
        return {"ok": False, "note": "Already expressing an emotion"}
    def _run():
        _busy.set()
        try:
            _EMOTIONS[name]()
        finally:
            _busy.clear()
    th = threading.Thread(target=_run, daemon=True)
    th.start()
    return {"ok": True, "emotion": name}


def available() -> list[str]:
    return list(_EMOTIONS.keys())


def is_busy() -> bool:
    return _busy.is_set()
