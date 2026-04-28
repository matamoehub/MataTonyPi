"""Lesson 12 - Pickup and Intelligent Transport Level 1 notebook header."""

from lesson_loader import setup as _setup

_setup(verbose=False)

from student_robot_v2 import bot

if "myRobot" not in globals():
    myRobot = bot()
