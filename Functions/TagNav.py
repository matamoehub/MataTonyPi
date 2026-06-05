#!/usr/bin/python3
# coding=utf8

import cv2
import time
import copy
import threading
import numpy as np
import hiwonder.ros_robot_controller_sdk as rrc
import hiwonder.ActionGroupControl as AGC
from hiwonder.Controller import Controller

board = rrc.Board()
ctl = Controller(board)

try:
    import apriltag
    _APRILTAG_AVAILABLE = True
except Exception:
    _APRILTAG_AVAILABLE = False

IMG_W = 640
IMG_H = 480
CENTRE_X = IMG_W // 2
CENTRE_DEAD = 40      # pixels either side of centre
AREA_ARRIVED = 0.3 * IMG_W * IMG_H  # 30% of frame

_tag_map = {}          # {tag_id: {'center_x', 'center_y', 'area', 'last_seen'}}
_map_lock = threading.Lock()
_running = False
_nav_thread = None
_detector = None


def _make_detector():
    global _detector
    if not _APRILTAG_AVAILABLE:
        return
    try:
        opts = apriltag.DetectorOptions(families='tag36h11')
        _detector = apriltag.Detector(opts)
    except Exception as e:
        print(f'[TagNav] Detector init error: {e}')


def init():
    _make_detector()


def start():
    global _running
    _running = True


def stop():
    global _running
    _running = False


def exit():
    AGC.runActionGroup('stand_slow')


def get_tag_map() -> dict:
    with _map_lock:
        return copy.deepcopy(_tag_map)


def navigate_to_tag(tag_id: int):
    """Non-blocking: launch navigation to a specific tag in a daemon thread."""
    t = threading.Thread(target=_nav_loop, args=(tag_id,), daemon=True)
    t.start()


def _nav_loop(tag_id: int):
    search_attempts = 0
    max_attempts = 20

    while _running:
        with _map_lock:
            tag_info = _tag_map.get(tag_id)

        # Check if tag is fresh (seen within 3 seconds)
        if tag_info is not None and (time.time() - tag_info['last_seen']) < 3.0:
            cx = tag_info['center_x']
            area = tag_info['area']
            search_attempts = 0  # reset search counter

            if cx < CENTRE_X - CENTRE_DEAD:
                try:
                    AGC.runActionGroup('turn_left_small_step')
                except Exception as e:
                    print(e)
                time.sleep(0.3)

            elif cx > CENTRE_X + CENTRE_DEAD:
                try:
                    AGC.runActionGroup('turn_right_small_step')
                except Exception as e:
                    print(e)
                time.sleep(0.3)

            else:
                # Centred
                if area >= AREA_ARRIVED:
                    print(f'[TagNav] Arrived at tag {tag_id}')
                    return
                else:
                    try:
                        AGC.runActionGroup('go_forward_one_step')
                    except Exception as e:
                        print(e)
                    time.sleep(0.5)

        else:
            # Tag not visible — search
            print(f'[TagNav] Tag {tag_id} not found, searching... ({search_attempts}/{max_attempts})')
            for _ in range(3):
                if not _running:
                    return
                try:
                    AGC.runActionGroup('turn_right_small_step')
                except Exception as e:
                    print(e)
                time.sleep(0.2)
            time.sleep(0.5)
            search_attempts += 1

            if search_attempts >= max_attempts:
                print(f'[TagNav] Tag {tag_id} not found after timeout')
                return

        time.sleep(0.05)


def run(img):
    if img is None:
        return img

    if not _APRILTAG_AVAILABLE or _detector is None:
        cv2.putText(img, 'apriltag not available', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        return img

    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        detections = _detector.detect(gray)

        now = time.time()
        with _map_lock:
            for det in detections:
                tag_id = det.tag_id
                corners = det.corners.astype(int)
                cx = int(det.center[0])
                cy = int(det.center[1])

                # Compute area via shoelace on corners
                x_c = corners[:, 0].astype(float)
                y_c = corners[:, 1].astype(float)
                area = 0.5 * abs(np.dot(x_c, np.roll(y_c, 1)) - np.dot(y_c, np.roll(x_c, 1)))

                _tag_map[tag_id] = {
                    'center_x': cx,
                    'center_y': cy,
                    'area': float(area),
                    'last_seen': now
                }

                # Draw outline
                cv2.polylines(img, [corners.reshape((-1, 1, 2))], True, (0, 255, 0), 2)
                cv2.circle(img, (cx, cy), 5, (0, 0, 255), -1)
                cv2.putText(img, f'ID:{tag_id}', (cx - 20, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    except Exception as e:
        print(f'[TagNav] Detection error: {e}')

    return img
