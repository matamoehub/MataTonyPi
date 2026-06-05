#!/usr/bin/python3
# coding=utf8

import cv2
import time
import random
import threading
import numpy as np
import hiwonder.ros_robot_controller_sdk as rrc
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle
from hiwonder.Controller import Controller

board = rrc.Board()
ctl = Controller(board)

# Tones per colour
COLOUR_TONES = {
    'red':   1200,
    'green': 1600,
    'blue':  900,
}
COLOURS = ['red', 'green', 'blue']

# State machine states
STATE_IDLE = 'IDLE'
STATE_SHOWING = 'SHOWING'
STATE_WAITING = 'WAITING'
STATE_RESULT = 'RESULT'

# Difficulty defaults (level 1)
_max_rounds = 4
_timeout = 5.0

_state = STATE_IDLE
_sequence = []
_current_step = 0
_detected_colour = None
_running = False
_move_thread = None
_lab_data = None
_colour_lock = threading.Lock()


def _load_lab_data():
    global _lab_data
    try:
        _lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    except Exception as e:
        print(f'[SimonSays] yaml load error: {e}')
        _lab_data = {}


def init():
    _load_lab_data()


def start():
    global _running, _move_thread, _state, _sequence, _current_step
    _running = True
    _state = STATE_IDLE
    _sequence = []
    _current_step = 0

    if _move_thread is None or not _move_thread.is_alive():
        _move_thread = threading.Thread(target=_move_loop, daemon=True)
        _move_thread.start()


def stop():
    global _running, _state
    _running = False
    _state = STATE_IDLE


def exit():
    AGC.runActionGroup('stand_slow')


def set_difficulty(level: int):
    global _max_rounds, _timeout
    if level == 1:
        _max_rounds = 4
        _timeout = 5.0
    elif level == 2:
        _max_rounds = 8
        _timeout = 5.0
    elif level == 3:
        _max_rounds = 8
        _timeout = 3.0
    else:
        print(f'[SimonSays] Unknown level: {level}')


def _buzz_colour(colour):
    freq = COLOUR_TONES.get(colour, 1200)
    try:
        board.set_buzzer(freq, 0.3, 0.2, 1)
        time.sleep(0.6)
    except Exception as e:
        print(e)


def _correct_feedback():
    try:
        board.set_buzzer(1800, 0.1, 0.05, 1)
        time.sleep(0.2)
        ctl.set_pwm_servo_pulse(1, 1700, 200)
        time.sleep(0.25)
        ctl.set_pwm_servo_pulse(1, 1500, 200)
        time.sleep(0.25)
    except Exception as e:
        print(e)


def _wrong_feedback():
    try:
        board.set_buzzer(600, 0.3, 0.1, 2)
        time.sleep(0.9)
        AGC.runActionGroup('stand')
    except Exception as e:
        print(e)


def _win_feedback():
    try:
        board.set_buzzer(1800, 0.1, 0.1, 3)
        time.sleep(0.6)
        AGC.runActionGroup('wave')
    except Exception as e:
        print(e)


def _show_sequence():
    """Play back the current sequence as buzzer tones."""
    for colour in _sequence:
        _buzz_colour(colour)
        time.sleep(0.2)


def _move_loop():
    global _state, _sequence, _current_step, _detected_colour

    # Wait briefly before starting
    time.sleep(1.0)
    _state = STATE_SHOWING

    while _running:
        if _state == STATE_SHOWING:
            # Add a new colour to sequence
            _sequence.append(random.choice(COLOURS))
            print(f'[SimonSays] Sequence: {_sequence}')
            _show_sequence()
            _current_step = 0
            _state = STATE_WAITING
            _round_start = time.time()

        elif _state == STATE_WAITING:
            elapsed = time.time() - _round_start
            if elapsed > _timeout:
                print('[SimonSays] Timeout!')
                _wrong_feedback()
                _state = STATE_IDLE
                _running_ref = _running
                if _running_ref:
                    # Reset for new game
                    _sequence = []
                    _current_step = 0
                    time.sleep(2.0)
                    if _running:
                        _state = STATE_SHOWING
                continue

            with _colour_lock:
                detected = _detected_colour

            if detected is not None:
                with _colour_lock:
                    _detected_colour = None  # consume

                expected = _sequence[_current_step]
                if detected == expected:
                    _correct_feedback()
                    _current_step += 1
                    _round_start = time.time()  # reset timeout for next step

                    if _current_step >= len(_sequence):
                        # Completed the sequence
                        if len(_sequence) >= _max_rounds:
                            print('[SimonSays] You won!')
                            _win_feedback()
                            _state = STATE_IDLE
                            time.sleep(3.0)
                            if _running:
                                _sequence = []
                                _current_step = 0
                                _state = STATE_SHOWING
                        else:
                            time.sleep(1.0)
                            _state = STATE_SHOWING
                else:
                    print(f'[SimonSays] Wrong! Expected {expected}, got {detected}')
                    _wrong_feedback()
                    _state = STATE_IDLE
                    time.sleep(2.0)
                    if _running:
                        _sequence = []
                        _current_step = 0
                        _state = STATE_SHOWING

        elif _state == STATE_IDLE:
            pass

        time.sleep(0.01)


def _detect_colour(img):
    """Detect dominant LAB colour in centre region. Returns colour name or None."""
    if _lab_data is None:
        return None
    try:
        h, w = img.shape[:2]
        roi = img[h//4:3*h//4, w//4:3*w//4]
        lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)

        best_colour = None
        best_count = 0

        for colour in COLOURS:
            if colour not in _lab_data:
                continue
            cr = _lab_data[colour]
            lower = np.array([cr['min'][0], cr['min'][1], cr['min'][2]])
            upper = np.array([cr['max'][0], cr['max'][1], cr['max'][2]])
            mask = cv2.inRange(lab, lower, upper)
            count = cv2.countNonZero(mask)
            if count > best_count and count > 200:
                best_count = count
                best_colour = colour

        return best_colour
    except Exception as e:
        print(e)
        return None


def run(img):
    if img is None:
        return img

    detected = _detect_colour(img)
    if detected is not None:
        with _colour_lock:
            _detected_colour = detected

    # OSD
    cv2.putText(img, f'SimonSays [{_state}]', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    if _sequence:
        seq_str = ' '.join(_sequence)
        cv2.putText(img, f'Seq: {seq_str}', (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(img, f'Step: {_current_step}/{len(_sequence)}', (10, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    return img
