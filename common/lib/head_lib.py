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
