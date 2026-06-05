#!/usr/bin/python3
# coding=utf8

import time
import threading
import hiwonder.ros_robot_controller_sdk as rrc
import hiwonder.ActionGroupControl as AGC
from hiwonder.Controller import Controller

board = rrc.Board()
ctl = Controller(board)

MAX_V = 12.6
MIN_V = 9.0
WARN_V = 10.5
CRITICAL_V = 10.0
POLL_INTERVAL = 30

_battery_voltage = MAX_V
_battery_critical = False
_warn_triggered = False
_monitor_thread = None
_monitor_started = False
_running = False


def init():
    pass


def start():
    global _running
    _running = True
    start_monitoring()


def stop():
    global _running
    _running = False


def exit():
    AGC.runActionGroup('stand_slow')


def run(img):
    return img


def get_percentage() -> int:
    v = _battery_voltage
    if v <= MIN_V:
        return 0
    if v >= MAX_V:
        return 100
    pct = int((v - MIN_V) / (MAX_V - MIN_V) * 100)
    return max(0, min(100, pct))


def is_critical() -> bool:
    return _battery_critical


def _buzz_sos():
    """Buzz SOS: 3 short, 3 long, 3 short."""
    try:
        # 3 short
        for _ in range(3):
            board.set_buzzer(1000, 0.1, 0.1, 1)
            time.sleep(0.25)
        # 3 long
        for _ in range(3):
            board.set_buzzer(1000, 0.5, 0.2, 1)
            time.sleep(0.8)
        # 3 short
        for _ in range(3):
            board.set_buzzer(1000, 0.1, 0.1, 1)
            time.sleep(0.25)
    except Exception as e:
        print(e)


def _monitor_loop():
    global _battery_voltage, _battery_critical, _warn_triggered
    while True:
        try:
            mv = ctl.get_bus_servo_vin(1)
            _battery_voltage = mv / 1000.0
        except Exception as e:
            print(e)

        v = _battery_voltage

        if v <= CRITICAL_V and not _battery_critical:
            print(f'[BatteryGuard] CRITICAL: {v:.2f}V')
            _battery_critical = True
            try:
                _buzz_sos()
                AGC.runActionGroup('stand')
            except Exception as e:
                print(e)
        elif v <= WARN_V and not _warn_triggered:
            print(f'[BatteryGuard] WARNING: {v:.2f}V — charge soon')
            _warn_triggered = True
            try:
                board.set_buzzer(1200, 0.1, 0.1, 3)
            except Exception as e:
                print(e)

        time.sleep(POLL_INTERVAL)


def start_monitoring():
    global _monitor_thread, _monitor_started
    if _monitor_started:
        return
    _monitor_started = True
    _monitor_thread = threading.Thread(target=_monitor_loop, daemon=True)
    _monitor_thread.start()


# Auto-start monitoring when module is imported
start_monitoring()
