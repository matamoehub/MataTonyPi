#!/usr/bin/env python3
"""YOLOv8n object detection library for MataTonyPi."""
from __future__ import annotations
import threading
from typing import Any

_model = None
_model_lock = threading.Lock()
_available: bool | None = None   # None = not yet checked


def is_available() -> bool:
    global _available
    if _available is not None:
        return _available
    try:
        import ultralytics  # noqa: F401
        _available = True
    except Exception:
        _available = False
    return _available


def _get_model():
    global _model
    with _model_lock:
        if _model is None:
            from ultralytics import YOLO
            _model = YOLO("yolov8n.pt")
    return _model


def detect(frame, confidence: float = 0.45) -> list[dict[str, Any]]:
    """
    Run YOLOv8n on a BGR frame.
    Returns list of dicts: {label, confidence, x, y, w, h, cx, cy, area}.
    Returns [] if ultralytics not installed or inference fails.
    """
    if not is_available():
        return []
    try:
        model = _get_model()
        results = model(frame, verbose=False, conf=float(confidence))
        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = (int(v) for v in box.xyxy[0])
                w, h = x2 - x1, y2 - y1
                detections.append({
                    "label":      model.names[int(box.cls[0])],
                    "confidence": float(box.conf[0]),
                    "x": x1, "y": y1, "w": w, "h": h,
                    "cx": x1 + w // 2, "cy": y1 + h // 2,
                    "area": w * h,
                })
        return detections
    except Exception as e:
        print(f"[yolo_lib] detect error: {e}")
        return []


def find_class(frame, class_name: str, confidence: float = 0.45) -> dict[str, Any] | None:
    """
    Find the largest/most-confident instance of class_name in frame.
    Returns the detection dict or None.
    """
    name = str(class_name).strip().lower()
    matches = [d for d in detect(frame, confidence=confidence)
               if d["label"].lower() == name]
    if not matches:
        return None
    return max(matches, key=lambda d: d["confidence"])


def class_names() -> list[str]:
    """Return all 80 COCO class names YOLOv8n can detect."""
    if not is_available():
        return []
    try:
        return list(_get_model().names.values())
    except Exception:
        return []
