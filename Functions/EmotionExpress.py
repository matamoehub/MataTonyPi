#!/usr/bin/python3
# coding=utf8

import time
import threading
import hiwonder.ros_robot_controller_sdk as rrc
import hiwonder.ActionGroupControl as AGC
from hiwonder.Controller import Controller

board = rrc.Board()
ctl = Controller(board)

# Arm servo IDs
L_SHOULDER = 7
L_ELBOW = 6
R_SHOULDER = 15
R_ELBOW = 14

# Pulse values
NEUTRAL = 500
HALF_UP = 650
FULL_UP = 800
DROPPED = 350

_emotion_busy = threading.Event()
_running = False


def init():
    pass


def start():
    global _running
    _running = True


def stop():
    global _running
    _running = False


def exit():
    AGC.runActionGroup('stand_slow')


def run(img):
    return img


def _do_happy():
    try:
        board.bus_servo_set_position(500, [[L_SHOULDER, HALF_UP], [L_ELBOW, HALF_UP],
                                           [R_SHOULDER, HALF_UP], [R_ELBOW, HALF_UP]])
        time.sleep(0.6)
        # bob head up/down twice
        for _ in range(2):
            ctl.set_pwm_servo_pulse(1, 1500 + 200, 200)
            time.sleep(0.25)
            ctl.set_pwm_servo_pulse(1, 1500 - 200, 200)
            time.sleep(0.25)
        ctl.set_pwm_servo_pulse(1, 1500, 200)
        time.sleep(0.25)
        # cheerful two-tone buzz
        board.set_buzzer(1800, 0.1, 0.05, 1)
        time.sleep(0.2)
        board.set_buzzer(2000, 0.1, 0.05, 1)
        time.sleep(0.2)
    except Exception as e:
        print(e)


def _do_sad():
    try:
        board.bus_servo_set_position(500, [[L_SHOULDER, DROPPED], [L_ELBOW, DROPPED],
                                           [R_SHOULDER, DROPPED], [R_ELBOW, DROPPED]])
        time.sleep(0.6)
        ctl.set_pwm_servo_pulse(1, 1500 - 300, 300)
        time.sleep(0.4)
        board.set_buzzer(600, 0.4, 0.1, 1)
        time.sleep(0.6)
    except Exception as e:
        print(e)


def _do_excited():
    try:
        AGC.runActionGroup('wave')
        for _ in range(4):
            board.set_buzzer(2000, 0.05, 0.05, 1)
            time.sleep(0.15)
    except Exception as e:
        print(e)


def _do_confused():
    try:
        ctl.set_pwm_servo_pulse(2, 1500 + 300, 400)
        time.sleep(0.6)
        ctl.set_pwm_servo_pulse(2, 1500 - 300, 400)
        time.sleep(0.6)
        ctl.set_pwm_servo_pulse(2, 1500, 300)
        time.sleep(0.4)
        board.set_buzzer(1200, 0.2, 0.1, 1)
        time.sleep(0.4)
    except Exception as e:
        print(e)


def _do_greet():
    try:
        AGC.runActionGroup('wave')
        board.set_buzzer(1500, 0.1, 0.05, 1)
        time.sleep(0.2)
    except Exception as e:
        print(e)


_EMOTION_MAP = {
    'happy': _do_happy,
    'sad': _do_sad,
    'excited': _do_excited,
    'confused': _do_confused,
    'greet': _do_greet,
}


def _emotion_worker(emotion_name):
    fn = _EMOTION_MAP.get(emotion_name)
    if fn is None:
        print(f'Unknown emotion: {emotion_name}')
        _emotion_busy.clear()
        return
    try:
        fn()
    except Exception as e:
        print(e)
    finally:
        _emotion_busy.clear()


def express(emotion_name: str):
    """Non-blocking. Runs emotion in daemon thread. Skips if busy."""
    if _emotion_busy.is_set():
        return
    _emotion_busy.set()
    t = threading.Thread(target=_emotion_worker, args=(emotion_name,), daemon=True)
    t.start()
