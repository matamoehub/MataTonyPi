"""Lesson 16 Level 1 notebook header."""

from __future__ import annotations

from lesson_loader import setup as _setup

_SETUP_INFO = _setup(verbose=False)

from student_robot_v2 import bot

myRobot = bot()

__all__ = ["myRobot", "_SETUP_INFO"]
