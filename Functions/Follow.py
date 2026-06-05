#!/usr/bin/python3
# coding=utf8

import cv2
import time
import threading
import numpy as np
import hiwonder.ros_robot_controller_sdk as rrc
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle
import hiwonder.PID as PID
import hiwonder.Misc as Misc
from hiwonder.Controller import Controller

board = rrc.Board()
ctl = Controller(board)

try:
    import VL53L0X
    _TOF_AVAILABLE = True
except Exception:
    _TOF_AVAILABLE = False

# Lab colour data
lab_data = None

# PID for head pan (servo2)
_pan_pid = PID.PID(P=0.035, I=0.0001, D=0.0)

# State
_running = False
_move_thread = None
_tof_thread = None
_tof = None
_tof_distance = 1000  # mm; default far
_too_close = False
_detected_blob = None  # (cx, cy, area) or None
_blob_lock = threading.Lock()

# Image dimensions
IMG_W = 640
IMG_H = 480
IMG_CX = IMG_W // 2
IMG_CY = IMG_H // 2

# Servo centres
PAN_CENTRE = 1500
PAN_MIN = 500
PAN_MAX = 2500
_pan_pulse = PAN_CENTRE

# Colour to track (set externally or default 'red')
_target_colour = 'red'


def _load_lab_data():
    global lab_data
    try:
        lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    except Exception as e:
        print(f'[Follow] yaml load error: {e}')
        lab_data = {}


def init():
    global _tof
    _load_lab_data()
    if _TOF_AVAILABLE:
        try:
            _tof = VL53L0X.VL53L0X(i2c_bus=1, i2c_address=0x29)
            _tof.open()
            _tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)
        except Exception as e:
            print(f'[Follow] ToF init error: {e}')


def start():
    global _running, _move_thread, _tof_thread
    _running = True
    _pan_pid.clear()

    if _move_thread is None or not _move_thread.is_alive():
        _move_thread = threading.Thread(target=_move_loop, daemon=True)
        _move_thread.start()

    if _TOF_AVAILABLE and _tof is not None:
        if _tof_thread is None or not _tof_thread.is_alive():
            _tof_thread = threading.Thread(target=_tof_loop, daemon=True)
            _tof_thread.start()


def stop():
    global _running
    _running = False


def exit():
    global _tof
    if _tof is not None:
        try:
            _tof.stop_ranging()
            _tof.close()
        except Exception as e:
            print(e)
        _tof = None
    AGC.runActionGroup('stand_slow')


def _tof_loop():
    global _tof_distance
    while _running:
        if _tof is not None:
            try:
                dist = _tof.get_distance()
                if dist > 0:
                    _tof_distance = dist
            except Exception as e:
                print(e)
        time.sleep(0.1)


def _detect_colour_blob(img):
    """Detect target colour blob in LAB space. Returns (cx, cy, area) or None."""
    if lab_data is None or _target_colour not in lab_data:
        return None
    try:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        color_range = lab_data[_target_colour]
        lower = np.array([color_range['min'][0], color_range['min'][1], color_range['min'][2]])
        upper = np.array([color_range['max'][0], color_range['max'][1], color_range['max'][2]])
        mask = cv2.inRange(lab, lower, upper)
        mask = cv2.erode(mask, None, iterations=1)
        mask = cv2.dilate(mask, None, iterations=1)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        if area < 500:
            return None
        M = cv2.moments(largest)
        if M['m00'] == 0:
            return None
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        return (cx, cy, area)
    except Exception as e:
        print(e)
        return None


def _move_loop():
    global _pan_pulse, _too_close
    while _running:
        with _blob_lock:
            blob = _detected_blob

        dist = _tof_distance

        # Distance gating
        if dist < 350:
            _too_close = True
        elif dist > 650:
            _too_close = False

        if blob is not None:
            cx, cy, area = blob

            # PID on pan servo to centre blob horizontally
            error_x = IMG_CX - cx
            _pan_pid.SetPoint = 0
            _pan_pid.update(error_x)
            _pan_pulse = int(_pan_pulse - _pan_pid.output)
            _pan_pulse = max(PAN_MIN, min(PAN_MAX, _pan_pulse))

            try:
                ctl.set_pwm_servo_pulse(2, _pan_pulse, 100)
            except Exception as e:
                print(e)

            centred = abs(error_x) < 40

            if centred and not _too_close and 350 < dist <= 650:
                # Hold position, only pan/tilt head
                pass
            elif centred and not _too_close and dist > 650:
                try:
                    AGC.runActionGroup('go_forward_one_step')
                except Exception as e:
                    print(e)
        else:
            # No blob: slowly return head to centre
            if abs(_pan_pulse - PAN_CENTRE) > 50:
                _pan_pulse = int(_pan_pulse * 0.9 + PAN_CENTRE * 0.1)
                try:
                    ctl.set_pwm_servo_pulse(2, _pan_pulse, 200)
                except Exception as e:
                    print(e)

        time.sleep(0.05)


def set_target_colour(colour_name: str):
    global _target_colour
    _target_colour = colour_name


def run(img):
    global _detected_blob
    if img is None:
        return img

    blob = _detect_colour_blob(img)
    with _blob_lock:
        _detected_blob = blob

    if blob is not None:
        cx, cy, area = blob
        cv2.circle(img, (cx, cy), 8, (0, 255, 0), -1)
        cv2.putText(img, f'Tracking {_target_colour}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    if _too_close:
        cv2.putText(img, 'TOO CLOSE', (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    return img
