#!/usr/bin/env python3
from __future__ import annotations

"""TonyPi notebook-friendly camera and vision helper."""

import copy
import os
import tempfile
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
        capture_index = self._discover_camera_index()
        cap = self._open_capture(capture_index)
        if not cap.isOpened():
            raise RuntimeError(f"TonyPi camera failed to open on index {capture_index}")
        if self.warmup_s > 0:
            time.sleep(self.warmup_s)

        frame = None
        for _ in range(6):
            ok, maybe = cap.read()
            if ok and maybe is not None:
                frame = maybe
        cap.release()
        if frame is None:
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

        path = None
        if show:
            info = self.show_image(annotated, save_path=save_path, title=f"Detected {name} objects: {len(objects)}")
            path = info["path"]
        elif save_path:
            path = self._write_image(annotated, save_path=save_path)

        return {"color": name, "found": bool(objects), "count": len(objects), "objects": objects, "path": path}

    def detect_faces(self, show: bool = True, save_path: Optional[str] = None, min_confidence: float = 0.5) -> Dict[str, Any]:
        cv2, _np = _require_runtime()
        mp = _require_mediapipe_runtime()
        frame_bgr = self._capture_frame()
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        annotated = frame_bgr.copy()
        h, w = annotated.shape[:2]
        faces: List[Dict[str, Any]] = []

        with mp.solutions.face_detection.FaceDetection(model_selection=0, min_detection_confidence=float(min_confidence)) as detector:
            result = detector.process(frame_rgb)

        detections = getattr(result, "detections", None) or []
        for idx, detection in enumerate(detections, start=1):
            bbox = detection.location_data.relative_bounding_box
            x = _clamp_pixel(bbox.xmin * w, w - 1)
            y = _clamp_pixel(bbox.ymin * h, h - 1)
            bw = max(1, _clamp_pixel(bbox.width * w, w))
            bh = max(1, _clamp_pixel(bbox.height * h, h))
            face = {"index": idx, "x": x, "y": y, "w": bw, "h": bh, "cx": int(x + bw / 2), "cy": int(y + bh / 2), "score": float(detection.score[0])}
            faces.append(face)
            cv2.rectangle(annotated, (x, y), (x + bw, y + bh), (0, 255, 0), 2)

        path = None
        if show:
            info = self.show_image(annotated, save_path=save_path, title=f"Detected faces: {len(faces)}")
            path = info["path"]
        elif save_path:
            path = self._write_image(annotated, save_path=save_path)

        return {"found": bool(faces), "count": len(faces), "faces": faces, "path": path}

    def find_face(self, show: bool = True, save_path: Optional[str] = None) -> Dict[str, Any]:
        return self.detect_faces(show=show, save_path=save_path)

    def recognize_hands(self, show: bool = True, save_path: Optional[str] = None, max_hands: int = 2) -> Dict[str, Any]:
        cv2, _np = _require_runtime()
        mp = _require_mediapipe_runtime()
        frame_bgr = self._capture_frame()
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        annotated = frame_bgr.copy()
        hands_found: List[Dict[str, Any]] = []

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
            mp.solutions.drawing_utils.draw_landmarks(annotated, landmarks, mp.solutions.hands.HAND_CONNECTIONS)
            hands_found.append({"index": idx, "handedness": handedness_label})

        path = None
        if show:
            info = self.show_image(annotated, save_path=save_path, title=f"Detected hands: {len(hands_found)}")
            path = info["path"]
        elif save_path:
            path = self._write_image(annotated, save_path=save_path)

        return {"found": bool(hands_found), "count": len(hands_found), "hands": hands_found, "path": path}

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


def get_vision() -> Vision:
    global _VISION
    env_value = os.environ.get("CAM_INDEX")
    if _VISION is None or getattr(_VISION, "_camera_env_value", None) != env_value:
        _VISION = Vision()
    return _VISION
