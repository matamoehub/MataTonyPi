#!/usr/bin/env python3
"""Sensor library for MataTonyPi — ToF, IMU, buzzer."""
__version__ = "1.0.0"
from __future__ import annotations
import threading
import time
from typing import Any
from tonypi_support import ensure_vendor_paths, get_board

# ── ToF (VL53L0X) ─────────────────────────────────────────────────────────────

_tof = None
_tof_distance: int = -1
_tof_lock = threading.Lock()
_tof_running = False


def _tof_thread():
    global _tof_distance
    while _tof_running:
        try:
            d = _tof.get_distance()
            with _tof_lock:
                _tof_distance = int(d)
        except Exception as e:
            print(f"[sensor_lib] ToF read error: {e}")
        time.sleep(0.1)


def init_tof(i2c_bus: int = 1, i2c_address: int = 0x29) -> bool:
    global _tof, _tof_running
    ensure_vendor_paths()
    try:
        import VL53L0X
        _tof = VL53L0X.VL53L0X(i2c_bus=int(i2c_bus), i2c_address=int(i2c_address))
        _tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)
        _tof_running = True
        th = threading.Thread(target=_tof_thread, daemon=True, name="ToFSensor")
        th.start()
        return True
    except Exception as e:
        print(f"[sensor_lib] ToF init failed: {e}")
        return False


def get_distance() -> int:
    """Return last ToF reading in mm, or -1 if unavailable."""
    with _tof_lock:
        return _tof_distance


def close_tof():
    global _tof_running
    _tof_running = False
    if _tof is not None:
        try:
            _tof.stop_ranging()
        except Exception as e:
            print(f"[sensor_lib] ToF close error: {e}")


# ── IMU ────────────────────────────────────────────────────────────────────────

def get_imu() -> dict[str, Any]:
    """Return IMU accelerometer data."""
    board = get_board()
    if board is None:
        return {"ok": False, "note": "Board unavailable"}
    try:
        data = board.get_imu()
        return {"ok": True, "data": data}
    except Exception as e:
        return {"ok": False, "note": str(e)}


# ── Buzzer ─────────────────────────────────────────────────────────────────────

def buzz(freq_hz: int, on_secs: float = 0.1, off_secs: float = 0.05, repeat: int = 1):
    """Play buzzer tone."""
    board = get_board()
    if board is None:
        return {"ok": False, "note": "Board unavailable"}
    try:
        board.set_buzzer(int(freq_hz), float(on_secs), float(off_secs), int(repeat))
        return {"ok": True, "freq_hz": freq_hz}
    except Exception as e:
        return {"ok": False, "note": str(e)}


def buzz_pattern(pattern: str):
    """Named buzzer patterns: happy, sad, sos, short, long."""
    patterns = {
        "short":  (1500, 0.1, 0.05, 1),
        "long":   (1000, 0.5, 0.1,  1),
        "happy":  (1800, 0.1, 0.05, 2),
        "sad":    (600,  0.4, 0.1,  1),
        "sos":    None,   # handled specially
    }
    if pattern == "sos":
        for _ in range(3): buzz(1000, 0.1, 0.1, 1); time.sleep(0.25)
        for _ in range(3): buzz(1000, 0.5, 0.2, 1); time.sleep(0.8)
        for _ in range(3): buzz(1000, 0.1, 0.1, 1); time.sleep(0.25)
        return {"ok": True, "pattern": "sos"}
    args = patterns.get(pattern)
    if args is None:
        return {"ok": False, "note": f"Unknown pattern '{pattern}'"}
    return buzz(*args)
