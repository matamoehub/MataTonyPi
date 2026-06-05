#!/usr/bin/python3
# coding=utf8

import cv2
import time
import threading
import hiwonder.ros_robot_controller_sdk as rrc
import hiwonder.ActionGroupControl as AGC
from hiwonder.Controller import Controller

board = rrc.Board()
ctl = Controller(board)

try:
    import mediapipe as mp
    _mp_face = mp.solutions.face_detection
    _USE_MP = True
except Exception:
    _USE_MP = False

_face_count = 0
_last_count = -1
_running = False
_move_thread = None
_lock = threading.Lock()

# Haar cascade fallback
_haar_cascade = None


def _load_haar():
    global _haar_cascade
    try:
        import os
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if os.path.exists(cascade_path):
            _haar_cascade = cv2.CascadeClassifier(cascade_path)
    except Exception as e:
        print(e)


def init():
    if not _USE_MP:
        _load_haar()


def start():
    global _running, _move_thread
    _running = True
    if _move_thread is None or not _move_thread.is_alive():
        _move_thread = threading.Thread(target=_move_loop, daemon=True)
        _move_thread.start()


def stop():
    global _running
    _running = False


def exit():
    AGC.runActionGroup('stand_slow')


def _move_loop():
    global _last_count
    while _running:
        with _lock:
            count = _face_count

        if count == 0 and _last_count != 0:
            _last_count = 0

        elif count == 1 and _last_count != 1:
            try:
                AGC.runActionGroup('wave')
            except Exception as e:
                print(e)
            _last_count = 1

        elif count == 2 and _last_count != 2:
            try:
                ctl.set_pwm_servo_pulse(2, 1500 + 200, 300)
                time.sleep(0.5)
                ctl.set_pwm_servo_pulse(2, 1500 - 200, 300)
                time.sleep(0.5)
                ctl.set_pwm_servo_pulse(2, 1500, 300)
                time.sleep(0.35)
            except Exception as e:
                print(e)
            _last_count = 2

        elif count >= 3 and _last_count != 3:
            try:
                AGC.runActionGroup('wave')
                board.set_buzzer(1900, 0.1, 0.1, 3)
            except Exception as e:
                print(e)
            _last_count = 3

        time.sleep(0.05)


def _detect_faces_mp(img):
    """Detect faces using MediaPipe. Returns list of (x,y,w,h) tuples."""
    boxes = []
    try:
        with _mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_det:
            h, w = img.shape[:2]
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = face_det.process(rgb)
            if results.detections:
                for det in results.detections:
                    bbox = det.location_data.relative_bounding_box
                    x = int(bbox.xmin * w)
                    y = int(bbox.ymin * h)
                    bw = int(bbox.width * w)
                    bh = int(bbox.height * h)
                    boxes.append((x, y, bw, bh))
    except Exception as e:
        print(e)
    return boxes


def _detect_faces_haar(img):
    """Detect faces using Haar cascade. Returns list of (x,y,w,h) tuples."""
    if _haar_cascade is None:
        return []
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = _haar_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) == 0:
            return []
        return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]
    except Exception as e:
        print(e)
        return []


def run(img):
    global _face_count

    if img is None:
        return img

    if _USE_MP:
        boxes = _detect_faces_mp(img)
    else:
        boxes = _detect_faces_haar(img)

    with _lock:
        _face_count = len(boxes)

    for (x, y, w, h) in boxes:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.putText(img, f'Faces: {len(boxes)}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    return img
