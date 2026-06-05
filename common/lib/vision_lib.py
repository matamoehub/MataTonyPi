#!/usr/bin/env python3
from __future__ import annotations

"""TonyPi notebook-friendly camera and vision helper."""

__version__ = "1.4.0"

import copy
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HSVRange = Tuple[Tuple[int, int, int], Tuple[int, int, int]]


DEFAULT_COLOR_PROFILES: Dict[str, List[HSVRange]] = {
    "red": [
        ((0, 120, 50), (10, 255, 255)),
        ((170, 120, 50), (179, 255, 255)),
    ],
    "green": [
        ((35, 80, 40), (85, 255, 255)),
    ],
    "blue": [
        ((90, 80, 40), (135, 255, 255)),
    ],
    "yellow": [
        ((18, 90, 60), (38, 255, 255)),
    ],
}


def _normalize_color_name(color: str) -> str:
    value = str(color or "").strip().lower()
    aliases = {"r": "red", "g": "green", "b": "blue", "y": "yellow"}
    return aliases.get(value, value)


def _require_runtime():
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except Exception as e:
        raise RuntimeError(f"vision_lib requires OpenCV and NumPy. Import failed: {e}") from e
    return cv2, np


def _require_mediapipe_runtime():
    try:
        import mediapipe as mp  # type: ignore
    except Exception as e:
        raise RuntimeError(f"vision_lib MediaPipe features require mediapipe. Import failed: {e}") from e
    return mp


def _load_haar_face_cascade():
    cv2, _np = _require_runtime()
    try:
        base = Path(cv2.data.haarcascades)  # type: ignore[attr-defined]
    except Exception:
        return None
    cascade = cv2.CascadeClassifier(str(base / "haarcascade_frontalface_default.xml"))
    if cascade.empty():
        return None
    return cascade


def _display_png_bytes(png_bytes: bytes) -> bool:
    try:
        from IPython.display import Image, display  # type: ignore
    except Exception:
        return False
    display(Image(data=png_bytes))
    return True


def _coerce_range(lower: Sequence[int], upper: Sequence[int]) -> HSVRange:
    low = tuple(int(v) for v in lower)
    high = tuple(int(v) for v in upper)
    if len(low) != 3 or len(high) != 3:
        raise ValueError("HSV ranges must contain exactly 3 values")
    return low, high


def _clamp_pixel(value: float, maximum: int) -> int:
    return max(0, min(int(round(value)), maximum))


def _hand_landmark_xy(landmarks, index: int) -> Tuple[float, float]:
    point = landmarks[index]
    return float(point.x), float(point.y)


def _classify_hand_gesture(landmarks, handedness: str) -> Tuple[str, Dict[str, bool]]:
    wrist_x, wrist_y = _hand_landmark_xy(landmarks, 0)
    thumb_tip_x, thumb_tip_y = _hand_landmark_xy(landmarks, 4)
    thumb_ip_x, thumb_ip_y = _hand_landmark_xy(landmarks, 3)
    index_tip_y = _hand_landmark_xy(landmarks, 8)[1]
    index_pip_y = _hand_landmark_xy(landmarks, 6)[1]
    middle_tip_y = _hand_landmark_xy(landmarks, 12)[1]
    middle_pip_y = _hand_landmark_xy(landmarks, 10)[1]
    ring_tip_y = _hand_landmark_xy(landmarks, 16)[1]
    ring_pip_y = _hand_landmark_xy(landmarks, 14)[1]
    pinky_tip_y = _hand_landmark_xy(landmarks, 20)[1]
    pinky_pip_y = _hand_landmark_xy(landmarks, 18)[1]

    fingers = {
        "thumb": (thumb_tip_x < thumb_ip_x) if handedness.lower().startswith("right") else (thumb_tip_x > thumb_ip_x),
        "index": index_tip_y < index_pip_y,
        "middle": middle_tip_y < middle_pip_y,
        "ring": ring_tip_y < ring_pip_y,
        "pinky": pinky_tip_y < pinky_pip_y,
    }

    if all(fingers.values()):
        return "open_palm", fingers
    if not any(fingers.values()):
        return "fist", fingers
    if fingers["index"] and fingers["middle"] and not fingers["ring"] and not fingers["pinky"]:
        return "peace", fingers
    if fingers["index"] and not fingers["middle"] and not fingers["ring"] and not fingers["pinky"]:
        return "point", fingers
    if fingers["thumb"] and not fingers["index"] and not fingers["middle"] and not fingers["ring"] and not fingers["pinky"]:
        if thumb_tip_y < wrist_y and thumb_ip_y < wrist_y:
            return "thumbs_up", fingers
        return "thumb_out", fingers
    if fingers["index"] and fingers["pinky"] and not fingers["middle"] and not fingers["ring"]:
        return "rock", fingers
    return "unknown", fingers


def _gesture_to_game_move(gesture: str):
    mapping = {
        "fist": "rock",
        "open_palm": "paper",
        "peace": "scissors",
        "rock": "rock",     # index+pinky = rock sign
    }
    return mapping.get(str(gesture).strip().lower())


class Vision:
    def __init__(self, camera_index: Optional[int] = None, width: int = 640, height: int = 480, warmup_s: float = 0.25, min_area: int = 350):
        env_value = os.environ.get("CAM_INDEX")
        self.camera_index = int(env_value) if env_value is not None else (camera_index if camera_index is not None else 0)
        self._camera_env_value = env_value
        self.width = int(width)
        self.height = int(height)
        self.warmup_s = float(warmup_s)
        self.min_area = int(min_area)
        self._profiles: Dict[str, List[HSVRange]] = copy.deepcopy(DEFAULT_COLOR_PROFILES)
        self._index_confirmed = False
        self.skip_frames = int(os.environ.get("CAM_SKIP_FRAMES", 3))
        self._cal_K = None
        self._cal_D = None
        self._cal_dim = None
        self._cal_map1 = None
        self._cal_map2 = None
        self._yolo_model = None

    def _open_capture(self, index: int):
        cv2, _np = _require_runtime()
        cap = cv2.VideoCapture(index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        return cap

    def _discover_camera_index(self) -> int:
        candidates = [self.camera_index]
        for index in range(6):
            if index not in candidates:
                candidates.append(index)

        for index in candidates:
            cap = self._open_capture(index)
            try:
                if not cap.isOpened():
                    continue
                ok, frame = cap.read()
                if ok and frame is not None:
                    self.camera_index = index
                    return index
            finally:
                cap.release()

        attempted = ", ".join(str(index) for index in candidates)
        raise RuntimeError(
            "TonyPi camera could not be opened from OpenCV. "
            f"Tried indices: {attempted}. "
            "On this robot the working camera is often index 0."
        )

    def _capture_frame(self):
        cv2, _np = _require_runtime()
        if not self._index_confirmed:
            capture_index = self._discover_camera_index()
            self._index_confirmed = True
        else:
            capture_index = self.camera_index
        cap = self._open_capture(capture_index)
        if not cap.isOpened():
            cap.release()
            self._index_confirmed = False
            capture_index = self._discover_camera_index()
            self._index_confirmed = True
            cap = self._open_capture(capture_index)
        if self.warmup_s > 0:
            time.sleep(self.warmup_s)
        # Drain stale V4L2 buffer frames — the first N reads after open
        # return buffered-up old frames, not the current scene.
        for _ in range(self.skip_frames):
            cap.read()
        ok, frame = cap.read()
        cap.release()
        if not ok or frame is None:
            raise RuntimeError("TonyPi camera opened, but no frame was available from OpenCV capture")
        return frame.copy()

    def _write_image(self, frame_bgr, save_path: Optional[str] = None) -> str:
        cv2, _np = _require_runtime()
        target = Path(save_path) if save_path else Path(tempfile.gettempdir()) / f"tonypi_vision_{int(time.time() * 1000)}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        ok = cv2.imwrite(str(target), frame_bgr)
        if not ok:
            raise RuntimeError(f"Failed to write image to {target}")
        return str(target)

    def show_image(self, frame_bgr, save_path: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
        cv2, _np = _require_runtime()
        ok, encoded = cv2.imencode(".png", frame_bgr)
        if not ok:
            raise RuntimeError("Failed to encode image for notebook display")
        displayed = _display_png_bytes(encoded.tobytes())
        path = self._write_image(frame_bgr, save_path=save_path)
        if title:
            print(title)
        if not displayed:
            print(f"Image saved: {path}")
        return {"displayed": displayed, "path": path}

    def snapshot(self, show: bool = True, save_path: Optional[str] = None) -> Dict[str, Any]:
        frame = self._capture_frame()
        info = self.show_image(frame, save_path=save_path, title="TonyPi Camera Snapshot") if show else {
            "displayed": False,
            "path": self._write_image(frame, save_path=save_path),
        }
        return {"frame_bgr": frame, **info}

    def get_color_profile(self, color: str) -> List[HSVRange]:
        name = _normalize_color_name(color)
        if name not in self._profiles:
            raise KeyError(f"Unknown colour profile: {color}")
        return copy.deepcopy(self._profiles[name])

    def _combined_mask(self, hsv_frame, ranges: Sequence[HSVRange]):
        cv2, np = _require_runtime()
        mask = None
        for lower, upper in ranges:
            part = cv2.inRange(hsv_frame, np.array(lower), np.array(upper))
            mask = part if mask is None else cv2.bitwise_or(mask, part)
        mask = cv2.erode(mask, None, iterations=1)
        mask = cv2.dilate(mask, None, iterations=2)
        return mask

    def find_color(self, color: str, show: bool = True, save_path: Optional[str] = None, min_area: Optional[int] = None) -> Dict[str, Any]:
        cv2, _np = _require_runtime()
        name = _normalize_color_name(color)
        ranges = self.get_color_profile(name)
        frame = self._capture_frame()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = self._combined_mask(hsv, ranges)
        contours, _hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        threshold = int(self.min_area if min_area is None else min_area)
        objects = []
        annotated = frame.copy()

        for contour in contours:
            area = float(cv2.contourArea(contour))
            if area < threshold:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            m = cv2.moments(contour)
            if m["m00"] == 0:
                continue
            cx = int(m["m10"] / m["m00"])
            cy = int(m["m01"] / m["m00"])
            obj = {"x": int(x), "y": int(y), "w": int(w), "h": int(h), "cx": cx, "cy": cy, "area": area}
            objects.append(obj)
            cv2.rectangle(annotated, (obj["x"], obj["y"]), (obj["x"] + obj["w"], obj["y"] + obj["h"]), (0, 255, 255), 2)

        objects.sort(key=lambda item: item["cx"])
        for idx, item in enumerate(objects, start=1):
            item["index"] = idx

        path = None
        if show:
            info = self.show_image(annotated, save_path=save_path, title=f"Detected {name} objects: {len(objects)}")
            path = info["path"]
        elif save_path:
            path = self._write_image(annotated, save_path=save_path)

        frame_h, frame_w = frame.shape[:2]
        return {
            "color": name, "found": bool(objects), "count": len(objects), "objects": objects, "path": path,
            "width": int(frame_w), "height": int(frame_h), "center_x": int(frame_w // 2),
        }

    def detect_faces(self, show: bool = True, save_path: Optional[str] = None, min_confidence: float = 0.5) -> Dict[str, Any]:
        cv2, _np = _require_runtime()
        frame_bgr = self._capture_frame()
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        annotated = frame_bgr.copy()
        h, w = annotated.shape[:2]
        faces: List[Dict[str, Any]] = []
        backend = "mediapipe"
        note = ""

        try:
            mp = _require_mediapipe_runtime()
            with mp.solutions.face_detection.FaceDetection(model_selection=0, min_detection_confidence=float(min_confidence)) as detector:
                result = detector.process(frame_rgb)

            detections = getattr(result, "detections", None) or []
            for idx, detection in enumerate(detections, start=1):
                bbox = detection.location_data.relative_bounding_box
                x = _clamp_pixel(bbox.xmin * w, w - 1)
                y = _clamp_pixel(bbox.ymin * h, h - 1)
                bw = max(1, _clamp_pixel(bbox.width * w, w))
                bh = max(1, _clamp_pixel(bbox.height * h, h))
                face = {"index": idx, "x": x, "y": y, "w": bw, "h": bh, "cx": int(x + bw / 2), "cy": int(y + bh / 2), "score": float(detection.score[0]) if getattr(detection, "score", None) else 0.0}
                faces.append(face)
                cv2.rectangle(annotated, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
        except Exception as exc:
            backend = "opencv-haar"
            note = f"MediaPipe unavailable, used OpenCV fallback: {exc}"
            cascade = _load_haar_face_cascade()
            if cascade is not None:
                gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
                detections = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
                for idx, (x, y, bw, bh) in enumerate(detections, start=1):
                    face = {"index": idx, "x": int(x), "y": int(y), "w": int(bw), "h": int(bh), "cx": int(x + bw / 2), "cy": int(y + bh / 2), "score": 0.6}
                    faces.append(face)
                    cv2.rectangle(annotated, (int(x), int(y)), (int(x + bw), int(y + bh)), (0, 255, 0), 2)
            else:
                note = "Face detection unavailable: MediaPipe is not installed and OpenCV Haar cascade was not found"

        path = None
        if show:
            info = self.show_image(annotated, save_path=save_path, title=f"Detected faces: {len(faces)}")
            path = info["path"]
        elif save_path:
            path = self._write_image(annotated, save_path=save_path)

        return {"found": bool(faces), "count": len(faces), "faces": faces, "path": path, "backend": backend, "note": note}

    def find_face(self, show: bool = True, save_path: Optional[str] = None) -> Dict[str, Any]:
        return self.detect_faces(show=show, save_path=save_path)

    def recognize_hands(self, show: bool = True, save_path: Optional[str] = None, max_hands: int = 2) -> Dict[str, Any]:
        cv2, _np = _require_runtime()
        frame_bgr = self._capture_frame()
        annotated = frame_bgr.copy()
        hands_found: List[Dict[str, Any]] = []
        note = ""
        try:
            mp = _require_mediapipe_runtime()
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            with mp.solutions.hands.Hands(static_image_mode=True, max_num_hands=int(max_hands), min_detection_confidence=0.5, min_tracking_confidence=0.5) as detector:
                result = detector.process(frame_rgb)

            multi_landmarks = getattr(result, "multi_hand_landmarks", None) or []
            multi_handedness = getattr(result, "multi_handedness", None) or []
            for idx, landmarks in enumerate(multi_landmarks, start=1):
                handedness_label = "unknown"
                if idx - 1 < len(multi_handedness):
                    try:
                        handedness_label = multi_handedness[idx - 1].classification[0].label
                    except Exception:
                        pass
                xs = [_clamp_pixel(pt.x * annotated.shape[1], annotated.shape[1] - 1) for pt in landmarks.landmark]
                ys = [_clamp_pixel(pt.y * annotated.shape[0], annotated.shape[0] - 1) for pt in landmarks.landmark]
                gesture, fingers = _classify_hand_gesture(landmarks.landmark, handedness_label)
                mp.solutions.drawing_utils.draw_landmarks(annotated, landmarks, mp.solutions.hands.HAND_CONNECTIONS)
                cv2.putText(
                    annotated,
                    f"{handedness_label} {gesture}",
                    (min(xs), max(18, min(ys) - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 0),
                    2,
                )
                hands_found.append(
                    {
                        "index": idx,
                        "handedness": handedness_label,
                        "gesture": gesture,
                        "game_move": _gesture_to_game_move(gesture),
                        "fingers": fingers,
                        "bbox": {
                            "x": min(xs),
                            "y": min(ys),
                            "w": max(xs) - min(xs),
                            "h": max(ys) - min(ys),
                        },
                    }
                )
        except Exception as exc:
            note = f"Hand detection unavailable on this robot image: {exc}"

        path = None
        if show:
            info = self.show_image(annotated, save_path=save_path, title=f"Detected hands: {len(hands_found)}")
            path = info["path"]
        elif save_path:
            path = self._write_image(annotated, save_path=save_path)

        return {
            "found": bool(hands_found),
            "count": len(hands_found),
            "hands": hands_found,
            "path": path,
            "note": note,
            "game_moves": [h["game_move"] for h in hands_found if h.get("game_move")],
        }

    def set_color_profile(self, color: str, lower_hsv, upper_hsv=None):
        """Set a custom HSV colour profile. lower_hsv can be a (lower, upper) tuple or list of such pairs."""
        name = _normalize_color_name(color)
        if upper_hsv is None:
            # Expect list of (lower, upper) pairs
            ranges = []
            for pair in lower_hsv:
                ranges.append(_coerce_range(pair[0], pair[1]))
        else:
            ranges = [_coerce_range(lower_hsv, upper_hsv)]
        self._profiles[name] = ranges
        return {"color": name, "ranges": ranges}

    def show_profiles(self):
        """Print and return all colour profiles."""
        for name in sorted(self._profiles):
            print(f"{name}: {self._profiles[name]}")
        return copy.deepcopy(self._profiles)

    def target_position(self, color: str, target_x=None, deadzone: int = 50,
                        show: bool = True, min_area=None) -> Dict[str, Any]:
        """Find the largest colour object and return its direction from centre.
        Returns: found, direction ("left"|"center"|"right"|"lost"), error (pixels), target_x, deadzone, object, result."""
        result = self.find_color(color=color, show=show, min_area=min_area)
        objects = result.get("objects", [])
        centre_x = int(result.get("center_x", self.width // 2) if target_x is None else target_x)
        threshold = abs(int(deadzone))

        if not objects:
            return {
                "color": result.get("color", color),
                "found": False,
                "direction": "lost",
                "error": None,
                "target_x": centre_x,
                "deadzone": threshold,
                "object": None,
                "result": result,
            }

        target = max(objects, key=lambda item: item["area"])
        error = int(target["cx"] - centre_x)
        if abs(error) <= threshold:
            direction = "center"
        elif error < 0:
            direction = "left"
        else:
            direction = "right"

        return {
            "color": result.get("color", color),
            "found": True,
            "direction": direction,
            "error": error,
            "target_x": centre_x,
            "deadzone": threshold,
            "object": target,
            "result": result,
        }

    def locate_object(self, color: str, target_x=None, deadzone: int = 50,
                      show: bool = True, min_area=None,
                      object_diameter_cm=None) -> Dict[str, Any]:
        """Enhanced target_position — adds angle_x_deg, lateral_cm, normalised error.
        direction: "left" | "center" | "right" | "lost"
        error_norm: -1.0 (far left) to +1.0 (far right), resolution-independent.
        angle_x_deg: positive = object is to the RIGHT of centre.
        lateral_cm: estimated lateral cm if object_diameter_cm provided and calibration loaded."""
        result = self.find_color(color=color, show=show, min_area=min_area)
        objects = result.get("objects", [])
        frame_w = result.get("width", self.width) or self.width
        centre_x = int(frame_w // 2 if target_x is None else target_x)
        threshold = abs(int(deadzone))

        if not objects:
            return {
                "color": result.get("color", color),
                "found": False,
                "direction": "lost",
                "error": None,
                "error_norm": None,
                "angle_x_deg": None,
                "lateral_cm": None,
                "target_x": centre_x,
                "deadzone": threshold,
                "object": None,
                "result": result,
            }

        target = max(objects, key=lambda item: item["area"])
        error = int(target["cx"] - centre_x)
        error_norm = round(error / max(1, frame_w / 2), 3)
        angles = self.pixel_to_angle(target["cx"])
        angle_x_deg = angles["angle_x_deg"]
        lateral_cm = None
        if object_diameter_cm is not None:
            lateral_cm = self.estimate_lateral_cm(target["cx"], target.get("w", 0), object_diameter_cm)

        if abs(error) <= threshold:
            direction = "center"
        elif error < 0:
            direction = "left"
        else:
            direction = "right"

        return {
            "color": result.get("color", color),
            "found": True,
            "direction": direction,
            "error": error,
            "error_norm": error_norm,
            "angle_x_deg": angle_x_deg,
            "lateral_cm": lateral_cm,
            "target_x": centre_x,
            "deadzone": threshold,
            "object": target,
            "result": result,
        }

    _CALIBRATION_SEARCH_PATHS = [
        "/opt/robot/calibration/camera_calibration.npz",
    ]

    def load_calibration(self, path=None) -> bool:
        """Load camera calibration from npz file. Searches /opt/robot/calibration/ if path not given.
        Returns True if loaded. Used by pixel_to_angle() and estimate_lateral_cm()."""
        cv2, np = _require_runtime()
        candidates = [Path(path)] if path else [
            Path("/opt/robot/calibration/camera_calibration.npz"),
            Path(__file__).resolve().parent.parent / "calibration" / "camera_calibration.npz",
            Path.home() / "camera_calibration.npz",
        ]
        for p in candidates:
            if not p.exists():
                continue
            try:
                data = np.load(str(p))
                # Try both key naming conventions
                K = data.get("k_array", data.get("mtx_array", None))
                D = data.get("d_array", data.get("dist_array", None))
                if K is None or D is None:
                    continue
                D = D.flatten()
                w, h = self.width, self.height
                new_K, _ = cv2.getOptimalNewCameraMatrix(K, D, (w, h), 1, (w, h))
                map1, map2 = cv2.initUndistortRectifyMap(K, D, None, new_K, (w, h), cv2.CV_16SC2)
                self._cal_K = new_K
                self._cal_D = D
                self._cal_dim = (w, h)
                self._cal_map1 = map1
                self._cal_map2 = map2
                print(f"[vision_lib] calibration loaded: {p.name}")
                return True
            except Exception as e:
                print(f"[vision_lib] calibration load error ({p}): {e}")
        return False

    def _ensure_calibration(self) -> bool:
        if self._cal_K is not None:
            return True
        return self.load_calibration()

    def undistort_frame(self, frame):
        """Undistort a frame using loaded camera calibration. Returns original frame if unavailable."""
        if not self._ensure_calibration():
            return frame
        cv2, _np = _require_runtime()
        return cv2.remap(frame, self._cal_map1, self._cal_map2, cv2.INTER_LINEAR)

    def pixel_to_angle(self, pixel_x: float, pixel_y=None) -> Dict[str, float]:
        """Convert pixel x (and optionally y) to angular offset from camera centre.
        Returns {"angle_x_deg": float, "angle_y_deg": float}.
        Positive angle_x = object is to the RIGHT of centre."""
        import math as _math
        if self._ensure_calibration() and self._cal_K is not None:
            fx = float(self._cal_K[0, 0])
            fy = float(self._cal_K[1, 1])
            cx = float(self._cal_K[0, 2])
            cy = float(self._cal_K[1, 2])
        else:
            fx = fy = self.width / (2 * _math.tan(_math.radians(30)))
            cx = self.width / 2.0
            cy = self.height / 2.0
        angle_x = _math.degrees(_math.atan2(float(pixel_x) - cx, fx))
        angle_y = _math.degrees(_math.atan2(float(pixel_y) - cy, fy)) if pixel_y is not None else 0.0
        return {"angle_x_deg": round(angle_x, 2), "angle_y_deg": round(angle_y, 2)}

    def estimate_lateral_cm(self, pixel_cx: float, pixel_width: float, object_diameter_cm: float = 6.5):
        """Estimate lateral distance in cm from camera centre using object apparent width.
        Requires camera calibration. Returns None if unavailable."""
        if pixel_width <= 0:
            return None
        if not self._ensure_calibration() or self._cal_K is None:
            return None
        import math as _math
        fx = float(self._cal_K[0, 0])
        cx = float(self._cal_K[0, 2])
        depth_cm = fx * float(object_diameter_cm) / float(pixel_width)
        lateral_cm = (float(pixel_cx) - cx) / fx * depth_cm
        return round(lateral_cm, 1)

    def estimate_depth_cm(self, pixel_width: float, object_real_width_cm: float) -> Optional[float]:
        """Estimate forward distance (depth) to an object in cm.

        Uses the pinhole camera model:  depth = fx * real_width / pixel_width

        Works without a calibration file — falls back to a 60° FOV estimate.
        The more accurate the camera calibration and real object size, the better.

        Args:
            pixel_width:          Width of the object bounding box in pixels.
            object_real_width_cm: Real-world width of the object in cm.
                                  e.g. 4.5 for a small block, 6.5 for a football.

        Returns depth in cm, or None if pixel_width is zero.
        """
        import math as _math
        if pixel_width <= 0:
            return None
        if self._ensure_calibration() and self._cal_K is not None:
            fx = float(self._cal_K[0, 0])
        else:
            # Fallback: estimate fx from a ~60° horizontal FOV
            fx = self.width / (2 * _math.tan(_math.radians(30)))
        depth_cm = fx * float(object_real_width_cm) / float(pixel_width)
        return round(depth_cm, 1)

    def calibrate_color(self, color: str, box_size: int = 80, hue_pad: int = 12,
                        sat_pad: int = 70, val_pad: int = 70,
                        show: bool = True, save_path=None, persist: bool = True) -> Dict[str, Any]:
        """Calibrate a colour profile by sampling the centre of the frame.
        Point the camera at the target object so it fills the centre, then call this.
        persist=True updates the profile in memory for immediate use."""
        cv2, np = _require_runtime()
        name = _normalize_color_name(color)
        frame = self._capture_frame()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, w = frame.shape[:2]
        half = max(10, int(box_size) // 2)
        cx, cy = w // 2, h // 2
        x0, y0 = max(0, cx - half), max(0, cy - half)
        x1, y1 = min(w, cx + half), min(h, cy + half)
        roi = hsv[y0:y1, x0:x1]
        if roi.size == 0:
            raise RuntimeError("Calibration ROI was empty")

        median = np.median(roi.reshape(-1, 3), axis=0)
        mh, ms, mv = [int(round(v)) for v in median]
        lower = (mh - int(hue_pad), max(0, ms - int(sat_pad)), max(0, mv - int(val_pad)))
        upper = (mh + int(hue_pad), min(255, ms + int(sat_pad)), min(255, mv + int(val_pad)))

        # Handle hue wrap-around
        lh, uh = lower[0], upper[0]
        if lh < 0:
            ranges = [((0, lower[1], lower[2]), (upper[0], upper[1], upper[2])),
                      ((180 + lh, lower[1], lower[2]), (179, upper[1], upper[2]))]
        elif uh > 179:
            ranges = [((lh, lower[1], lower[2]), (179, upper[1], upper[2])),
                      ((0, lower[1], lower[2]), (uh - 180, upper[1], upper[2]))]
        else:
            ranges = [((max(0, lh), lower[1], lower[2]), (min(179, uh), upper[1], upper[2]))]

        if persist:
            self._profiles[name] = ranges

        annotated = frame.copy()
        cv2.rectangle(annotated, (x0, y0), (x1, y1), (255, 255, 255), 2)
        cv2.putText(annotated, f"{name} HSV~{(mh, ms, mv)}", (10, 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        path = None
        if show:
            info = self.show_image(annotated, save_path=save_path, title=f"Calibrated {name}: {ranges}")
            path = info["path"]
        elif save_path:
            path = self._write_image(annotated, save_path=save_path)

        result = {"color": name, "sample_hsv": (mh, ms, mv), "ranges": ranges,
                  "path": path, "persisted": bool(persist)}
        print(result)
        return result

    def which_object(self, color: str, show: bool = True, save_path=None, min_area=None) -> int:
        """Returns the left-to-right index (1-based) of the largest detected colour object.
        Returns 0 if nothing found. Objects are numbered left to right in the frame."""
        result = self.find_color(color=color, show=show, save_path=save_path, min_area=min_area)
        objects = result.get("objects", [])
        if not objects:
            return 0
        largest = max(objects, key=lambda item: item["area"])
        idx = largest.get("index", 1)
        print(f"{result.get('color', color)} object index: {idx}")
        return int(idx)

    def detect_pose(self, show: bool = True, save_path=None,
                    min_detection_confidence: float = 0.5,
                    min_tracking_confidence: float = 0.5) -> Dict[str, Any]:
        """Detect full body pose using MediaPipe Pose.
        Returns: found, label ("hands_up"|"t_pose"|"left_hand_up"|"right_hand_up"|"neutral"), landmarks dict."""
        cv2, _np = _require_runtime()
        mp = _require_mediapipe_runtime()
        frame_bgr = self._capture_frame()
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        annotated = frame_bgr.copy()

        with mp.solutions.pose.Pose(
            static_image_mode=True,
            min_detection_confidence=float(min_detection_confidence),
            min_tracking_confidence=float(min_tracking_confidence),
        ) as detector:
            result = detector.process(frame_rgb)

        pose_landmarks = getattr(result, "pose_landmarks", None)
        pose_label = "none"
        landmarks_out = {}

        if pose_landmarks is not None:
            mp.solutions.drawing_utils.draw_landmarks(
                annotated, pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)
            key_indices = {
                "nose": 0, "left_shoulder": 11, "right_shoulder": 12,
                "left_elbow": 13, "right_elbow": 14,
                "left_wrist": 15, "right_wrist": 16,
                "left_hip": 23, "right_hip": 24,
            }
            for name, idx in key_indices.items():
                pt = pose_landmarks.landmark[idx]
                landmarks_out[name] = {"x": float(pt.x), "y": float(pt.y),
                                       "z": float(pt.z), "visibility": float(pt.visibility)}

            # Classify pose
            lm = pose_landmarks.landmark
            left_shoulder, right_shoulder = lm[11], lm[12]
            left_wrist, right_wrist = lm[15], lm[16]
            left_elbow, right_elbow = lm[13], lm[14]
            nose = lm[0]

            wrists_above_shoulders = left_wrist.y < left_shoulder.y and right_wrist.y < right_shoulder.y
            wrists_out_wide = (abs(left_wrist.y - left_shoulder.y) < 0.10 and
                               abs(right_wrist.y - right_shoulder.y) < 0.10)
            elbows_out_wide = (abs(left_elbow.y - left_shoulder.y) < 0.12 and
                               abs(right_elbow.y - right_shoulder.y) < 0.12)

            if wrists_above_shoulders:
                pose_label = "hands_up"
            elif wrists_out_wide and elbows_out_wide:
                pose_label = "t_pose"
            elif left_wrist.y < nose.y and right_wrist.y >= right_shoulder.y:
                pose_label = "left_hand_up"
            elif right_wrist.y < nose.y and left_wrist.y >= left_shoulder.y:
                pose_label = "right_hand_up"
            else:
                pose_label = "neutral"

            cv2.putText(annotated, f"pose: {pose_label}", (10, 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

        path = None
        if show:
            info = self.show_image(annotated, save_path=save_path, title=f"Pose: {pose_label}")
            path = info["path"]
        elif save_path:
            path = self._write_image(annotated, save_path=save_path)

        return {"found": bool(pose_landmarks), "label": pose_label,
                "landmarks": landmarks_out, "path": path}

    def show_pose(self, **kwargs): return self.detect_pose(**kwargs)
    def recognize_pose(self, **kwargs): return self.detect_pose(**kwargs)
    def show_color(self, color: str, **kwargs): return self.find_color(color=color, **kwargs)

    def find_tag(self, tag_id: int | None = None, show: bool = True, save_path: Optional[str] = None) -> Dict[str, Any]:
        cv2, _np = _require_runtime()
        frame_bgr = self._capture_frame()
        annotated = frame_bgr.copy()
        detections = []

        detector = None
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        try:
            import apriltag  # type: ignore
            detector = apriltag.Detector()
            results = detector.detect(gray)
            for det in results:
                det_id = int(getattr(det, "tag_id", -1))
                if tag_id is not None and det_id != int(tag_id):
                    continue
                corners = getattr(det, "corners", [])
                if len(corners) == 4:
                    pts = [(int(p[0]), int(p[1])) for p in corners]
                    for i in range(4):
                        cv2.line(annotated, pts[i], pts[(i + 1) % 4], (255, 0, 255), 2)
                center = getattr(det, "center", (0, 0))
                detections.append({"id": det_id, "cx": int(center[0]), "cy": int(center[1])})
        except Exception:
            pass

        path = None
        if show:
            info = self.show_image(annotated, save_path=save_path, title=f"Detected tags: {len(detections)}")
            path = info["path"]
        elif save_path:
            path = self._write_image(annotated, save_path=save_path)

        return {"found": bool(detections), "count": len(detections), "tags": detections, "path": path}


_VISION: Vision | None = None
_VISION_LOCK = threading.Lock()


def get_vision() -> Vision:
    global _VISION
    env_value = os.environ.get("CAM_INDEX")
    with _VISION_LOCK:
        if _VISION is None or getattr(_VISION, "_camera_env_value", None) != env_value:
            _VISION = Vision()
    return _VISION


def install_opencv_capture_fallback() -> bool:
    """TonyPi uses a vendor hardware camera; the OpenCV capture fallback is not applicable."""
    return False


def target_position(*args, **kwargs): return get_vision().target_position(*args, **kwargs)
def locate_object(*args, **kwargs): return get_vision().locate_object(*args, **kwargs)
def detect_pose(*args, **kwargs): return get_vision().detect_pose(*args, **kwargs)
def which_object(*args, **kwargs): return get_vision().which_object(*args, **kwargs)
def calibrate_color(*args, **kwargs): return get_vision().calibrate_color(*args, **kwargs)
def set_color_profile(*args, **kwargs): return get_vision().set_color_profile(*args, **kwargs)
def show_profiles(): return get_vision().show_profiles()
def load_calibration(*args, **kwargs): return get_vision().load_calibration(*args, **kwargs)
