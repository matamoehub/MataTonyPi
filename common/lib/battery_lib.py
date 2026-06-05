#!/usr/bin/env python3
"""Battery monitoring library for MataTonyPi."""
__version__ = "1.0.0"
from __future__ import annotations
import threading
import time
from typing import Any
from tonypi_support import ensure_vendor_paths, get_controller, get_board

MAX_V    = 12.6
MIN_V    =  9.0
WARN_V   = 10.5
CRITICAL_V = 10.0
POLL_S   = 30

_voltage: float = MAX_V
_critical: bool = False
_warn_fired: bool = False
_started: bool = False
_lock = threading.Lock()


def _buzz(freq, on_s, off_s, repeat):
    board = get_board()
    if board:
        try: board.set_buzzer(int(freq), float(on_s), float(off_s), int(repeat))
        except Exception as e: print(f"[battery_lib] buzzer: {e}")


def _read_voltage() -> float | None:
    ctl = get_controller()
    if ctl is None:
        return None
    try:
        mv = ctl.get_bus_servo_vin(1)
        return float(mv) / 1000.0
    except Exception as e:
        print(f"[battery_lib] read error: {e}")
        return None


def _monitor():
    global _voltage, _critical, _warn_fired
    from tonypi_support import run_action
    while True:
        time.sleep(POLL_S)
        v = _read_voltage()
        if v is None:
            continue
        with _lock:
            _voltage = v
            if v <= CRITICAL_V and not _critical:
                _critical = True
                print(f"[battery_lib] CRITICAL: {v:.2f}V — stopping robot")
                try:
                    _buzz(1000, 0.1, 0.1, 3)
                    time.sleep(0.8)
                    _buzz(1000, 0.5, 0.2, 3)
                    time.sleep(2.0)
                    _buzz(1000, 0.1, 0.1, 3)
                    run_action("stand")
                except Exception as e:
                    print(f"[battery_lib] critical action error: {e}")
            elif v <= WARN_V and not _warn_fired:
                _warn_fired = True
                print(f"[battery_lib] WARNING: low battery {v:.2f}V")
                _buzz(1200, 0.1, 0.1, 3)


def start_monitoring():
    global _started
    if _started:
        return
    ensure_vendor_paths()
    _started = True
    th = threading.Thread(target=_monitor, daemon=True, name="BatteryMonitor")
    th.start()


def get_voltage() -> float:
    with _lock:
        return _voltage


def get_percentage() -> int:
    v = get_voltage()
    if v <= MIN_V: return 0
    if v >= MAX_V: return 100
    return max(0, min(100, int((v - MIN_V) / (MAX_V - MIN_V) * 100)))


def is_critical() -> bool:
    with _lock:
        return _critical


def is_low() -> bool:
    return get_voltage() <= WARN_V
