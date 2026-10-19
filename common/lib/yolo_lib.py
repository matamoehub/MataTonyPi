#!/usr/bin/env python3
"""YOLO object detection library for MataTonyPi.

Ported from MataTurboPi's vision_lib.py YOLO upgrade: yolo26n nano is now
the primary model (pre-installed on the robot at a fixed path), with the
older yolov8n.pt kept as a graceful-degrade fallback for any robot not yet
provisioned with yolo26n, and an internet download of yolo26n as the last
resort. Override with the YOLO_MODEL env var for advanced use.
"""
from __future__ import annotations
__version__ = "1.2.0"
import os
import threading
from pathlib import Path
from typing import Any

_model = None
_model_lock = threading.Lock()
_available: bool | None = None   # None = not yet checked

# yolo26n nano — pre-installed on the robot at a fixed path, tried first.
_YOLO_MODEL_NAME = "yolo26n.pt"
_YOLO_MODEL_SEARCH_PATHS = [
    Path("/opt/robot/models/yolo26n.pt"),          # pre-installed by ops
    Path(__file__).resolve().parent.parent / "models" / "yolo26n.pt",  # repo copy
    Path.home() / ".config" / "Ultralytics" / "yolo26n.pt",  # ultralytics cache
]
_DEFAULT_YOLO_MODEL = os.environ.get("YOLO_MODEL", _YOLO_MODEL_NAME)

# Older model some robots were provisioned with before the yolo26n upgrade.
# yolo26n.pt requires internet to auto-download if it's not pre-installed —
# this fallback keeps detection working on a robot where that's
# unavailable. yolov8n.pt is a real, different (lower-accuracy) architecture,
# not a stand-in for yolo26n — this is a deliberate degrade-gracefully
# fallback, not something to rename/pretend is yolo26n.
_YOLO_FALLBACK_MODEL_NAME = "yolov8n.pt"
_YOLO_FALLBACK_SEARCH_PATHS = [
    Path("/opt/robot/models/yolov8n.pt"),
    Path(__file__).resolve().parent.parent / "models" / "yolov8n.pt",
    Path.home() / ".config" / "Ultralytics" / "yolov8n.pt",
]


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
    """Load YOLO26 nano lazily.

    Checks pre-installed paths first (/opt/robot/models/yolo26n.pt), then
    the older yolov8n.pt some robots were provisioned with before the
    yolo26n upgrade (lower accuracy, but works with zero internet), and
    only as a last resort falls back to an internet download of yolo26n.
    """
    global _model
    with _model_lock:
        if _model is not None:
            return _model
        # ultralytics imports matplotlib.pyplot on load which triggers the
        # Jupyter inline backend and crashes with a version mismatch:
        #   AttributeError: 'RcParams' object has no attribute '_get'
        # Force a non-interactive backend before the import to avoid this.
        try:
            import matplotlib
            matplotlib.use("Agg")
        except Exception:
            pass
        from ultralytics import YOLO

        # Loading (not just finding the file) can fail on its own: a yolo26n.pt
        # checkpoint can use newer architecture blocks (e.g. C3k2) than the
        # installed ultralytics package supports, raising AttributeError deep
        # inside torch's unpickling — that's a version mismatch, not a missing
        # file, so it must also fall through to the older yolov8n.pt rather
        # than crashing detect() outright.
        for p in _YOLO_MODEL_SEARCH_PATHS:
            if not p.exists():
                continue
            try:
                _model = YOLO(str(p))
            except Exception as e:
                print(f"[yolo_lib] failed to load {p} ({e}) — trying older {_YOLO_FALLBACK_MODEL_NAME}")
                continue
            print(f"[yolo_lib] YOLO26 nano loaded from {p}")
            return _model
        # yolo26n.pt missing or failed to load — try the older yolov8n.pt
        # before reaching for the internet, so detection still works.
        for p in _YOLO_FALLBACK_SEARCH_PATHS:
            if not p.exists():
                continue
            try:
                _model = YOLO(str(p))
            except Exception as e:
                print(f"[yolo_lib] failed to load fallback {p} ({e})")
                continue
            print(
                f"[yolo_lib] using older {_YOLO_FALLBACK_MODEL_NAME} from {p} "
                "(lower accuracy; ask ops to install a working yolo26n.pt for the full upgrade)"
            )
            return _model
        # Neither pre-installed model loaded — download (requires internet, first run only)
        print(f"[yolo_lib] downloading {_YOLO_MODEL_NAME} (first use only)...")
        _model = YOLO(_DEFAULT_YOLO_MODEL)
        print("[yolo_lib] YOLO26 nano ready")
    return _model


def detect(frame, confidence: float = 0.45) -> list[dict[str, Any]]:
    """
    Run YOLO26n on a BGR frame.
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
    """Return all COCO class names the loaded model can detect (yolo26n or
    the yolov8n fallback -- both trained on the same 80 COCO classes)."""
    if not is_available():
        return []
    try:
        return list(_get_model().names.values())
    except Exception:
        return []
