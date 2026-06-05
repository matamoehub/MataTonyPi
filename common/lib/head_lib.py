#!/usr/bin/env python3
"""TonyPi head movement helper."""

from __future__ import annotations

from tonypi_support import head_center, set_head, sleep

HEAD_SETTLE_S = 0.14


def center(duration_ms: int = 300):
    vertical, horizontal = head_center()
    result = set_head(vertical=vertical, horizontal=horizontal, duration_ms=duration_ms)
    sleep(HEAD_SETTLE_S)
    return result


def look_left(delta: int = 320, duration_ms: int = 280):
    vertical, horizontal = head_center()
    result = set_head(vertical=vertical, horizontal=horizontal + int(delta), duration_ms=duration_ms)
    sleep(HEAD_SETTLE_S)
    return result


def look_right(delta: int = 320, duration_ms: int = 280):
    vertical, horizontal = head_center()
    result = set_head(vertical=vertical, horizontal=horizontal - int(delta), duration_ms=duration_ms)
    sleep(HEAD_SETTLE_S)
    return result


def look_up(delta: int = 260, duration_ms: int = 280):
    vertical, horizontal = head_center()
    result = set_head(vertical=vertical + int(delta), horizontal=horizontal, duration_ms=duration_ms)
    sleep(HEAD_SETTLE_S)
    return result


def look_down(delta: int = 260, duration_ms: int = 280):
    vertical, horizontal = head_center()
    result = set_head(vertical=vertical - int(delta), horizontal=horizontal, duration_ms=duration_ms)
    sleep(HEAD_SETTLE_S)
    return result


def nod():
    vertical, horizontal = head_center()
    set_head(vertical=vertical + 160, horizontal=horizontal, duration_ms=220)
    sleep(0.18)
    set_head(vertical=vertical - 120, horizontal=horizontal, duration_ms=220)
    sleep(0.18)
    return center()


def shake():
    vertical, horizontal = head_center()
    set_head(vertical=vertical, horizontal=horizontal + 220, duration_ms=200)
    sleep(0.15)
    set_head(vertical=vertical, horizontal=horizontal - 220, duration_ms=200)
    sleep(0.15)
    return center()


def scan():
    vertical, horizontal = head_center()
    set_head(vertical=vertical, horizontal=horizontal + 300, duration_ms=260)
    sleep(0.18)
    set_head(vertical=vertical, horizontal=horizontal - 300, duration_ms=260)
    sleep(0.18)
    return center()


def wiggle(cycles: int = 2, amplitude: int = 200, duration_ms: int = 200):
    """Friendly yaw wiggle left-right."""
    _, horizontal = head_center()
    for _ in range(int(cycles)):
        set_head(horizontal=horizontal - int(amplitude), duration_ms=duration_ms)
        sleep(duration_ms / 1000.0 + 0.05)
        set_head(horizontal=horizontal + int(amplitude), duration_ms=duration_ms)
        sleep(duration_ms / 1000.0 + 0.05)
    return center()


def tiny_wiggle(seconds: float = 2.0, amplitude: int = 90, duration_ms: int = 120):
    """Very small continuous wiggle for given seconds."""
    import time as _time
    _, horizontal = head_center()
    end = _time.time() + float(seconds)
    while _time.time() < end:
        set_head(horizontal=horizontal - int(amplitude), duration_ms=duration_ms)
        sleep(duration_ms / 1000.0 + 0.02)
        set_head(horizontal=horizontal + int(amplitude), duration_ms=duration_ms)
        sleep(duration_ms / 1000.0 + 0.02)
    return center()


def glance_left(amplitude: int = 250, hold_s: float = 0.15):
    """Quick look left then return to centre."""
    _, horizontal = head_center()
    set_head(horizontal=horizontal + int(amplitude), duration_ms=200)
    sleep(float(hold_s))
    return center()


def glance_right(amplitude: int = 250, hold_s: float = 0.15):
    """Quick look right then return to centre."""
    _, horizontal = head_center()
    set_head(horizontal=horizontal - int(amplitude), duration_ms=200)
    sleep(float(hold_s))
    return center()
