#!/usr/bin/env python3
"""TonyPi wireless controller reference helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


BUTTON_ACTIONS: Dict[str, str] = {
    "START": "Return the robot to the initial posture",
    "L1": "Right tilt and lift the left foot",
    "R1": "Left tilt and lift the right foot",
    "UP": "Move forward",
    "DOWN": "Move backward",
    "LEFT": "Move left",
    "RIGHT": "Move right",
    "TRIANGLE": "Wave",
    "CROSS": "Bow",
    "SQUARE": "Twist waist",
    "CIRCLE": "Right-footed shot",
    "LEFT_STICK_UP": "Move forward",
    "LEFT_STICK_DOWN": "Move backward",
    "LEFT_STICK_LEFT": "Move left",
}


DANCE_BUTTONS: Dict[str, str] = {
    "SELECT+L1": "Dance 1",
    "SELECT+L2": "Dance 2",
    "SELECT+R1": "Dance 3",
    "SELECT+R2": "Dance 4",
    "SELECT+TRIANGLE": "Dance 5",
    "SELECT+SQUARE": "Dance 6",
    "SELECT+CIRCLE": "Dance 7",
    "SELECT+START": "Activate athlete mode",
}


MODE_SUMMARY: Dict[str, str] = {
    "single_green": "All buttons can be used.",
    "red_green": "Directional buttons are locked. The other buttons still work.",
}


def buttons() -> Dict[str, str]:
    return deepcopy(BUTTON_ACTIONS)


def dance_buttons() -> Dict[str, str]:
    return deepcopy(DANCE_BUTTONS)


def modes() -> Dict[str, str]:
    return deepcopy(MODE_SUMMARY)


def summary() -> Dict[str, Any]:
    return {
        "buttons": buttons(),
        "dance_buttons": dance_buttons(),
        "modes": modes(),
        "notes": [
            "Insert the wireless receiver before turning on the robot.",
            "For group control, power on the server robot first.",
            "Repeated presses work better than holding a direction for long continuous movement.",
        ],
    }
