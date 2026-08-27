#!/usr/bin/env python3
"""Single public student-facing API for MataTonyPi."""

from __future__ import annotations

__version__ = "1.4.2"

import builtins
from dataclasses import asdict, dataclass
import sys
import threading
import time
import types
from typing import Any

# When this module is loaded via importlib exec_module() without being
# registered in sys.modules first (e.g. inside a workspace shim), Python
# 3.11+ dataclasses.py does sys.modules.get(cls.__module__).__dict__ and
# gets None, raising AttributeError.  Pre-register a stub so @dataclass
# can resolve the lookup.  The shim will overwrite the real names anyway.
if __name__ not in sys.modules:
    sys.modules[__name__] = types.ModuleType(__name__)

import action_group_lib
import controller_lib
import head_lib
import llm_lib
import signal_lib
import tonypi_support as support
import tts_lib
import vision_lib

_lib_errors: dict[str, str] = {}

def _try_import(name: str):
    try:
        import importlib
        return importlib.import_module(name)
    except Exception as exc:
        _lib_errors[name] = str(exc)
        return None

emotion_lib    = _try_import("emotion_lib")
battery_lib    = _try_import("battery_lib")
sensor_lib     = _try_import("sensor_lib")
yolo_lib       = _try_import("yolo_lib")
navigation_lib = _try_import("navigation_lib")
patrol_lib     = _try_import("patrol_lib")
games_lib      = _try_import("games_lib")


@dataclass
class DetectionResult:
    found: bool = False
    label: str = ""
    x: int = 0
    y: int = 0
    area: int = 0
    confidence: float = 0.0
    note: str = "stub"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class _Namespace:
    def __init__(self, owner: "RobotV2"):
        self._owner = owner

    def _log(self, action: str, **kwargs) -> dict[str, Any]:
        return self._owner._log(action, **kwargs)

    def _run_action(self, action: str, candidates, times: int = 1):
        return self._owner._run_named_action(action, candidates, times=times)


class AnimationNamespace(_Namespace):
    def list_action_groups(self):
        return action_group_lib.list_actions()

    def show_action_groups(self):
        actions = action_group_lib.catalog()
        for item in actions:
            action_id = item.get("id")
            prefix = f"[{action_id}] " if action_id else ""
            print(f"{prefix}{item['name']} ({item['category']})")
        return actions

    def run(self, name: str, times: int = 1):
        return self._owner._wrap_call("anim.run", action_group_lib.run, name=str(name), times=max(1, int(times)))

    def run_id(self, action_id: str | int, times: int = 1):
        return self._owner._wrap_call("anim.run_id", action_group_lib.run_id, action_id=action_id, times=max(1, int(times)))

    def catalog(self):
        return action_group_lib.catalog()

    def dance_moves(self):
        return action_group_lib.dances()

    def wave(self):
        return self._run_action("anim.wave", ["wave", ("hello",), ("greet",)])

    def greet(self):
        return self._run_action("anim.greet", ["wave", ("greet",), ("hello",)])

    def dance(self):
        return self._run_action("anim.dance", ["twist", "chest", "left_uppercut", "stepping"])

    def celebrate(self):
        return self._run_action("anim.celebrate", ["left_uppercut", "wave", "twist"])

    def martial_arts(self):
        return self._run_action("anim.martial_arts", ["wing_chun", "toulan_a", "toulan_b"])

    def bow_deep(self):
        return self._run_action("anim.bow_deep", ["jugong", "bow"])

    def catch_ball(self):
        return self._run_action("anim.catch_ball", ["catch_ball_go", "catch_ball"])

    def think(self):
        self._owner.head.look_left()
        self._owner.head.look_right()
        return self._owner.head.center()

    def sad(self):
        return self._owner.pose.bow()

    def yes(self):
        return self._owner.head.nod()

    def no(self):
        return self._owner.head.shake()

    def scan(self):
        return self._owner.head.scan()


class HeadNamespace(_Namespace):
    _H_DELTA = 320
    _V_DELTA = 260

    def _move(self, vertical: int | None = None, horizontal: int | None = None, duration_ms: int = 280):
        return self._owner._set_head(vertical=vertical, horizontal=horizontal, duration_ms=duration_ms)

    def look_left(self):
        return self._owner._wrap_call("head.look_left", head_lib.look_left, delta=self._H_DELTA)

    def look_right(self):
        return self._owner._wrap_call("head.look_right", head_lib.look_right, delta=self._H_DELTA)

    def look_up(self):
        return self._owner._wrap_call("head.look_up", head_lib.look_up, delta=self._V_DELTA)

    def look_down(self):
        return self._owner._wrap_call("head.look_down", head_lib.look_down, delta=self._V_DELTA)

    def center(self):
        return self._owner._wrap_call("head.center", head_lib.center)

    def centre(self):
        """British spelling alias for center()."""
        return self.center()

    def nod(self):
        return self._owner._wrap_call("head.nod", head_lib.nod)

    def shake(self):
        return self._owner._wrap_call("head.shake", head_lib.shake)

    def scan(self):
        return self._owner._wrap_call("head.scan", head_lib.scan)

    def wiggle(self, cycles: int = 2):
        return self._owner._wrap_call("head.wiggle", head_lib.wiggle, cycles=int(cycles))

    def tiny_wiggle(self, seconds: float = 2.0):
        return self._owner._wrap_call("head.tiny_wiggle", head_lib.tiny_wiggle, seconds=float(seconds))

    def glance_left(self):
        return self._owner._wrap_call("head.glance_left", head_lib.glance_left)

    def glance_right(self):
        return self._owner._wrap_call("head.glance_right", head_lib.glance_right)


class ArmsNamespace(_Namespace):
    def left_up(self):
        return self._run_action("arms.left_up", ["lift_left_hand", "left_hand", ("lift", "left")])

    def right_up(self):
        return self._run_action("arms.right_up", ["right_hand", ("right", "hand")])

    def hands_up(self):
        return self._run_action("arms.hands_up", ["go_hand_up", "go_hand_up1", ("go", "hand", "up")])

    def open(self):
        return self._run_action("arms.open", ["lift_left_hand", "left_hand"])

    def close(self):
        return self._run_action("arms.close", ["stand"])

    def center(self):
        return self._run_action("arms.center", ["stand"])

    def grab_pose(self):
        return self._run_action("arms.grab_pose", ["grab_squat_right", "grab_right"])

    def carry_pose(self):
        return self._run_action("arms.carry_pose", ["lift_up", "put_up_object"])

    def release_pose(self):
        return self._run_action("arms.release_pose", ["put_down", "put_down_object"])

    def punch_left(self):
        return self._run_action("arms.punch_left", ["left_uppercut"])

    def punch_right(self):
        return self._run_action("arms.punch_right", ["right_uppercut"])

    def punch(self):
        self._run_action("arms.punch_left", ["left_uppercut"])
        return self._run_action("arms.punch_right", ["right_uppercut"])

    def kick_left(self):
        return self._run_action("arms.kick_left", ["left_kick", "left_shot"])

    def kick_right(self):
        return self._run_action("arms.kick_right", ["right_kick", "right_shot"])


class PoseNamespace(_Namespace):
    def ready(self):
        return self._run_action("pose.ready", ["stand", ("ready",)])

    def neutral(self):
        return self._run_action("pose.neutral", ["stand", ("home",)])

    def bow(self):
        return self._run_action("pose.bow", ["bow"])

    def stand(self):
        return self._run_action("pose.stand", ["stand"])

    def sit(self):
        return self._run_action("pose.sit", ["squat", "squat_down"])

    def carry(self):
        return self._run_action("pose.carry", ["lift_up", "put_up_object"])


class MotionNamespace(_Namespace):
    def _steps(self, action: str, candidates, steps: int = 1):
        return self._owner._run_named_action(action, candidates, times=max(1, int(steps)))

    def walk_forward(self, steps: int = 1):
        return self._steps("motion.walk_forward", ["go_forward", ("forward",)], steps=steps)

    def walk_backward(self, steps: int = 1):
        return self._steps("motion.walk_backward", ["back", "go_back", ("backward",)], steps=steps)

    def walk_fast(self, steps: int = 1):
        return self._steps("motion.walk_fast", ["go_forward_fast", "go_forward"], steps=steps)

    def turn_left(self, steps: int = 1):
        return self._steps("motion.turn_left", ["turn_left_small_step", "turn_left"], steps=steps)

    def turn_right(self, steps: int = 1):
        return self._steps("motion.turn_right", ["turn_right_small_step", "turn_right"], steps=steps)

    def turn_left_fast(self, steps: int = 1):
        return self._steps("motion.turn_left_fast", ["turn_left_fast", "turn_left"], steps=steps)

    def turn_right_fast(self, steps: int = 1):
        return self._steps("motion.turn_right_fast", ["turn_right_fast", "turn_right"], steps=steps)

    def step_left(self, steps: int = 1):
        return self._steps("motion.step_left", ["left_move", "left_move_fast"], steps=steps)

    def step_right(self, steps: int = 1):
        return self._steps("motion.step_right", ["right_move", "right_move_fast"], steps=steps)

    def creep(self, steps: int = 1):
        return self._steps("motion.creep", ["creep_forward", "go_forward"], steps=steps)

    def approach(self):
        return self.walk_forward(steps=1)

    def stop(self):
        return self._owner.stop()


class VisionNamespace(_Namespace):
    _COLOR_NAMES = {"red", "green", "blue", "yellow", "r", "g", "b", "y"}

    def _prepare_face_capture(self):
        self._owner.head.look_up()
        time.sleep(0.18)

    def find_color(self, name: str) -> DetectionResult:
        result = vision_lib.get_vision().find_color(str(name), show=True)
        objects = result.get("objects", [])
        if not objects:
            self._log("vision.find_color", name=str(name))
            return DetectionResult(found=False, label=str(name), note="No matching color found")
        obj = max(objects, key=lambda item: item["area"])
        self._log("vision.find_color", name=str(name))
        return DetectionResult(found=True, label=str(name), x=int(obj["cx"]), y=int(obj["cy"]), area=int(obj["area"]), confidence=1.0, note=result.get("path", ""))

    def find_object(self, name: str) -> DetectionResult:
        """Find a specific object by class name using YOLOv8n.
        Shows annotated frame in Jupyter with a box around the detected object."""
        if yolo_lib is None or not yolo_lib.is_available():
            return DetectionResult(found=False, label=str(name),
                                   note="YOLOv8n not available — pip install ultralytics")
        import cv2
        vis = vision_lib.get_vision()
        frame = vis._capture_frame()
        det = yolo_lib.find_class(frame, str(name))
        annotated = frame.copy()
        if det is not None:
            x1, y1 = det["x"], det["y"]
            x2, y2 = x1 + det["w"], y1 + det["h"]
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label_text = f"{det['label']} {det['confidence']:.0%}"
            cv2.putText(annotated, label_text, (x1, max(y1 - 8, 12)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
        title = f"Looking for: {name}  —  {'✓ Found!' if det else '✗ Not found'}"
        info = vis.show_image(annotated, title=title)
        self._log("vision.find_object", name=str(name))
        if det is None:
            return DetectionResult(found=False, label=str(name), note="Not detected")
        return DetectionResult(found=True, label=det["label"],
                               x=det["cx"], y=det["cy"], area=det["area"],
                               confidence=det["confidence"], note=info.get("path", ""))

    def find_face(self) -> DetectionResult:
        self._prepare_face_capture()
        result = vision_lib.get_vision().find_face(show=True)
        faces = result.get("faces", [])
        self._log("vision.find_face")
        if not faces:
            note = str(result.get("note") or "No face found")
            return DetectionResult(found=False, label="face", note=note)
        face = faces[0]
        backend = str(result.get("backend") or "")
        path = str(result.get("path") or "")
        detail = f"{backend}:{path}" if backend and path else (backend or path)
        return DetectionResult(found=True, label="face", x=int(face["cx"]), y=int(face["cy"]), area=int(face["w"] * face["h"]), confidence=float(face.get("score", 1.0)), note=detail)

    def find_tag(self, tag_id: int) -> DetectionResult:
        result = vision_lib.get_vision().find_tag(tag_id=int(tag_id), show=True)
        tags = result.get("tags", [])
        self._log("vision.find_tag", tag_id=int(tag_id))
        if not tags:
            return DetectionResult(found=False, label=f"tag:{int(tag_id)}", note="No matching tag found")
        tag = tags[0]
        detection_result = DetectionResult(found=True, label=f"tag:{int(tag_id)}", x=int(tag["cx"]), y=int(tag["cy"]), area=0, confidence=1.0, note=result.get("path", ""))
        if navigation_lib is not None:
            navigation_lib.update_tag_map(int(tag_id), int(tag["cx"]), int(tag["cy"]), 0.0)
        return detection_result

    def recognize_hands(self, show: bool = True):
        return vision_lib.get_vision().recognize_hands(show=show)

    def track_color(self, name: str):
        color_name = str(name).strip().lower()
        if color_name not in self._COLOR_NAMES:
            self._log("vision.track_color", name=str(name))
            return {"found": False, "label": str(name), "note": "TonyPi color tracking currently supports red, green, blue, or yellow"}
        return vision_lib.get_vision().find_color(str(name), show=True)

    def track_face(self):
        self._prepare_face_capture()
        return vision_lib.get_vision().find_face(show=True)

    def move_towards_color(self, color: str, steps: int = 1, deadzone: int = 50,
                           push: bool = False, show: bool = False, min_area=None):
        """Take one step to line TonyPi up with the largest object of a colour.
        Steps sideways (step_left / step_right) until the object is centred, then
        walks forward when centred if push=True. Call it repeatedly in a loop to
        home in on a target. Returns the target_position() decision dict with an
        extra 'moved' key: "left" | "right" | "forward" | None."""
        decision = vision_lib.get_vision().target_position(
            color=str(color), deadzone=int(deadzone), show=show, min_area=min_area)
        direction = decision.get("direction")
        decision["moved"] = None
        n = max(1, int(steps))
        if direction == "left":
            self._owner.motion.step_left(steps=n)
            decision["moved"] = "left"
        elif direction == "right":
            self._owner.motion.step_right(steps=n)
            decision["moved"] = "right"
        elif direction == "center" and push:
            self._owner.motion.walk_forward(steps=n)
            decision["moved"] = "forward"
        self._log("vision.move_towards_color", color=str(color), moved=decision["moved"])
        return decision

    def snapshot(self):
        return vision_lib.get_vision().snapshot(show=True)

    def scan_for(self, name: str):
        target = str(name).strip().lower()
        if target == "face":
            self._prepare_face_capture()
            return vision_lib.get_vision().find_face(show=True)
        if target in self._COLOR_NAMES:
            return vision_lib.get_vision().find_color(str(name), show=True)
        self._log("vision.scan_for", name=str(name))
        return {
            "found": False,
            "label": str(name),
            "note": "TonyPi scan_for currently supports face or colors: red, green, blue, yellow",
        }

    def detect_objects(self, confidence: float = 0.45) -> list:
        """Detect all objects in frame using YOLOv8n.
        Shows annotated frame in Jupyter with boxes around every detected object."""
        if yolo_lib is None or not yolo_lib.is_available():
            self._log("vision.detect_objects")
            return []
        import cv2
        vis = vision_lib.get_vision()
        frame = vis._capture_frame()
        detections = yolo_lib.detect(frame, confidence=float(confidence))
        annotated = frame.copy()
        for det in detections:
            x1, y1 = det["x"], det["y"]
            x2, y2 = x1 + det["w"], y1 + det["h"]
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 200, 255), 2)
            label_text = f"{det['label']} {det['confidence']:.0%}"
            cv2.putText(annotated, label_text, (x1, max(y1 - 8, 12)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 2)
        vis.show_image(annotated, title=f"Detected {len(detections)} object(s)")
        self._log("vision.detect_objects", count=len(detections))
        return detections

    def find_faces(self) -> list:
        """Detect ALL faces (not just one). Returns list of DetectionResult."""
        self._prepare_face_capture()
        result = vision_lib.get_vision().find_face(show=True)
        faces = result.get("faces", [])
        self._log("vision.find_faces", count=len(faces))
        return [
            DetectionResult(found=True, label="face",
                            x=int(f["cx"]), y=int(f["cy"]),
                            area=int(f["w"] * f["h"]),
                            confidence=float(f.get("score", 1.0)))
            for f in faces
        ]

    def describe(self) -> str:
        """Describe the scene using Claude API. Returns description string."""
        import os, base64
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return "I can't see clearly right now — ANTHROPIC_API_KEY not set"
        self._log("vision.describe")
        try:
            import cv2
            frame = vision_lib.get_vision()._capture_frame()
            ok, buf = cv2.imencode(".jpg", frame)
            if not ok:
                return "I can't see clearly right now"
            b64 = base64.b64encode(buf.tobytes()).decode()
            payload = {
                "max_tokens": 200,
                "system": ("You are the vision system of a small humanoid robot called TonyPi. "
                           "Describe what you see in 1-2 short sentences, conversationally."),
                "messages": [{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64",
                     "media_type": "image/jpeg", "data": b64}},
                    {"type": "text", "text": "What do you see?"}
                ]}],
            }
            return llm_lib.call_claude(payload, api_key=api_key)
        except Exception as e:
            print(f"[student_robot_v2] vision.describe error: {e}")
            return "I can't see clearly right now"

    def object_classes(self) -> list:
        """List all 80 COCO object classes YOLOv8n can detect."""
        return yolo_lib.class_names() if yolo_lib else []

    def yolo_available(self) -> bool:
        return yolo_lib is not None and yolo_lib.is_available()

    def target_position(self, color: str, deadzone: int = 50):
        """Find largest colour object; returns direction left/center/right/lost + pixel error."""
        return vision_lib.get_vision().target_position(color=str(color), deadzone=int(deadzone), show=True)

    def locate_object(self, color: str, deadzone: int = 50, object_diameter_cm=None):
        """Like target_position but adds angle_x_deg, lateral_cm, normalised error."""
        kwargs = {"color": str(color), "deadzone": int(deadzone), "show": True}
        if object_diameter_cm is not None:
            kwargs["object_diameter_cm"] = float(object_diameter_cm)
        return vision_lib.get_vision().locate_object(**kwargs)

    def detect_pose(self):
        """Detect full body pose: hands_up, t_pose, left_hand_up, right_hand_up, neutral."""
        return vision_lib.get_vision().detect_pose(show=True)

    def which_object(self, color: str) -> int:
        """Returns left-to-right index of largest colour object (1-based), 0 if not found."""
        return vision_lib.get_vision().which_object(color=str(color), show=True)

    def calibrate_color(self, color: str, box_size: int = 80):
        """Calibrate colour by sampling the centre of the frame. Point at target object first."""
        return vision_lib.get_vision().calibrate_color(color=str(color), box_size=int(box_size), show=True)

    def set_color_profile(self, color: str, lower_hsv, upper_hsv=None):
        """Set custom HSV colour profile."""
        return vision_lib.get_vision().set_color_profile(color=str(color), lower_hsv=lower_hsv, upper_hsv=upper_hsv)

    def show_profiles(self):
        """Print all colour profiles."""
        return vision_lib.get_vision().show_profiles()

    def load_calibration(self, path=None) -> bool:
        """Load camera calibration npz file for angular + lateral measurements."""
        return vision_lib.get_vision().load_calibration(path=path)

    def estimate_distance(self, pixel_width: float, object_real_width_cm: float) -> float:
        """Estimate forward distance to an object in cm using its pixel width and known real size.
        Works without calibration (uses FOV estimate as fallback).
        Example: myRobot.vision.estimate_distance(result.w, 4.5) for a 4.5cm wide block."""
        depth = vision_lib.get_vision().estimate_depth_cm(
            pixel_width=float(pixel_width),
            object_real_width_cm=float(object_real_width_cm)
        )
        return depth if depth is not None else -1.0


class PickupNamespace(_Namespace):
    _COLOUR_NAMES = {"red", "green", "blue", "yellow", "r", "g", "b", "y"}

    def find(self, name: str) -> DetectionResult:
        """Look for an object before picking up.
        Shows a raw snapshot first ("here's what I can see"), then runs
        detection and shows an annotated frame with boxes around any matches.
        Uses colour detection for red/green/blue/yellow, YOLOv8n for everything else.
        Returns a DetectionResult so you can check result.found before acting."""
        target = str(name).strip().lower()
        vis = vision_lib.get_vision()

        # Show raw snapshot first so the student can see exactly what the robot sees
        print(f"[pickup.find] Looking for: {name}")
        vis.snapshot(show=True)

        if target in self._COLOUR_NAMES:
            result = vis.find_color(target, show=True)
            objects = result.get("objects", [])
            self._log("pickup.find", name=target, method="colour")
            if not objects:
                return DetectionResult(found=False, label=target, note="No matching colour found")
            obj = max(objects, key=lambda item: item["area"])
            return DetectionResult(found=True, label=target,
                                   x=int(obj["cx"]), y=int(obj["cy"]),
                                   area=int(obj["area"]), confidence=1.0,
                                   note=result.get("path", ""))
        # General object — use YOLOv8n
        self._log("pickup.find", name=name, method="yolo")
        return self._owner.vision.find_object(name)

    def approach_object(self, name: str):
        return self._run_action("pickup.approach_object", ["go_forward_one_step", "go_forward_one_small_step", "go_forward"])

    def pick_up(self, name: str):
        return self._run_action("pickup.pick_up", ["grab_squat_right", "grab_right", "catch_ball"])

    def grab(self):
        return self._run_action("pickup.grab", ["grab_squat_right", "grab_right"])

    def lift_to_chest(self) -> dict:
        """Pick up from the floor and hold at chest height instead of raising above head.

        Runs the move_up action group to grab the object, then immediately
        moves the arm servos to a comfortable chest-carry position.

        Servo positions (tunable via keyword args in future):
          Shoulder pulse ~600 = arms raised to chest level
          Elbow pulse    ~380 = elbows bent forward to cradle the object
        """
        import time as _time
        # Step 1 — run the floor pickup sequence
        result = self._owner._wrap_call("pickup.lift_to_chest", support.run_action, name="move_up", times=1)

        # Step 2 — immediately re-position arms to chest carry height
        # move_up finishes with arms raised above head; we pull them back down to chest
        _time.sleep(0.3)
        board = support.get_board()
        if board is not None:
            try:
                board.bus_servo_set_position(600, [
                    [7,  600],   # left shoulder  — chest level
                    [6,  380],   # left elbow     — bent forward to hold object
                    [15, 600],   # right shoulder — chest level
                    [14, 380],   # right elbow    — bent forward to hold object
                ])
            except Exception as exc:
                result["chest_carry_note"] = str(exc)
        else:
            result["chest_carry_note"] = "board unavailable — servo adjustment skipped"

        return result

    def carry(self):
        return self._run_action("pickup.carry", ["lift_up", "put_up_object"])

    def place_down(self):
        return self._run_action("pickup.place_down", ["put_down", "put_down_object", "put_down2"])

    def release(self):
        return self._run_action("pickup.release", ["put_down", "put_down2"])

    def grab_and_lift(self):
        """Squat, grab and stand in one move — full floor pickup sequence."""
        return self._run_action("pickup.grab_and_lift", ["grab_squat_up_right", "grab_squat_up_left", "move_up"])

    def transport(self, name: str):
        return self._run_action("pickup.transport", ["go_forward", "go_forward_one_step"])


class VoiceNamespace(_Namespace):
    def say(self, text: str, block: bool = True, voice: str | None = None):
        return self._owner.say(text=text, block=block, voice=voice)

    def speak(self, text: str, block: bool = True, voice: str | None = None):
        return self.say(text=text, block=block, voice=voice)

    def voices(self):
        return tts_lib.available_voices(installed_only=True)

    def show_voices(self):
        voices = tts_lib.available_voices(installed_only=True)
        current = tts_lib.current_voice() if hasattr(tts_lib, "current_voice") else "?"
        print(f"Active voice: {current}")
        print("Installed voices:")
        for i, v in enumerate(voices, 1):
            marker = " ◀ active" if v == current else ""
            print(f"  {i}. {v}{marker}")
        return voices

    def current_voice(self) -> str:
        """Return the currently active voice name."""
        if hasattr(tts_lib, "current_voice"):
            return tts_lib.current_voice()
        return "amy"

    def select(self, voice: str | None = None, number: int | None = None):
        return tts_lib.select_voice(voice=voice, number=number)

    def select_voice(self, voice: str | None = None, number: int | None = None):
        return self.select(voice=voice, number=number)

    def select_voice_number(self, number: int):
        return self.select(number=number)

    def greet(self):
        return self.say("Hello everyone.")

    def celebrate(self):
        return self.say("Yay. Great job.")

    def think(self):
        return self.say("Hmm. Let me think.")


class ControllerNamespace(_Namespace):
    def buttons(self):
        return controller_lib.buttons()

    def show_buttons(self):
        mapping = controller_lib.buttons()
        for button, action in mapping.items():
            print(f"{button}: {action}")
        return mapping

    def dance_buttons(self):
        return controller_lib.dance_buttons()

    def show_dance_buttons(self):
        mapping = controller_lib.dance_buttons()
        for button, action in mapping.items():
            print(f"{button}: {action}")
        return mapping

    def modes(self):
        return controller_lib.modes()

    def summary(self):
        return controller_lib.summary()


class TeamNamespace(_Namespace):
    def local_ip(self):
        return signal_lib.local_ip()

    def start_server(self, port: int = 8765):
        return self._owner._wrap_call("team.start_server", signal_lib.start_server, port=int(port))

    def stop_server(self):
        return self._owner._wrap_call("team.stop_server", signal_lib.stop_server)

    def server_status(self):
        return signal_lib.status()

    def signal(self, host: str, cue: str, payload: Any = None, port: int = 8765, timeout: float = 5.0):
        return self._owner._wrap_call(
            "team.signal",
            signal_lib.send,
            host=str(host),
            cue=str(cue),
            payload=payload,
            port=int(port),
            timeout=float(timeout),
        )

    def broadcast(self, hosts: list[str], cue: str, payload: Any = None, port: int = 8765, timeout: float = 5.0):
        host_list = [str(host).strip() for host in hosts if str(host).strip()]
        return self._owner._wrap_call(
            "team.broadcast",
            signal_lib.broadcast,
            hosts=host_list,
            cue=str(cue),
            payload=payload,
            port=int(port),
            timeout=float(timeout),
        )

    def wait_for(self, cue: str, timeout: float | None = None):
        kwargs = {"cue": str(cue)}
        if timeout is not None:
            kwargs["timeout"] = float(timeout)
        return self._owner._wrap_call("team.wait_for", signal_lib.wait_for, **kwargs)

    def cues(self):
        return signal_lib.cue_history()


class EmotionNamespace(_Namespace):
    def express(self, emotion: str):
        if emotion_lib is None:
            return self._log("emotion.express", emotion=emotion)
        return self._owner._wrap_call("emotion.express", emotion_lib.express, emotion=str(emotion))

    def happy(self):    return self.express("happy")
    def sad(self):      return self.express("sad")
    def excited(self):  return self.express("excited")
    def confused(self): return self.express("confused")
    def greet(self):    return self.express("greet")

    def is_busy(self) -> bool:
        return emotion_lib.is_busy() if emotion_lib else False

    def available(self) -> list:
        return emotion_lib.available() if emotion_lib else []


class BatteryNamespace(_Namespace):
    def voltage(self) -> float:
        return battery_lib.get_voltage() if battery_lib else 0.0

    def percentage(self) -> int:
        return battery_lib.get_percentage() if battery_lib else 0

    def is_critical(self) -> bool:
        return battery_lib.is_critical() if battery_lib else False

    def is_low(self) -> bool:
        return battery_lib.is_low() if battery_lib else False

    def status(self) -> dict:
        if battery_lib is None:
            return self._log("battery.status")
        return {"voltage": self.voltage(), "percentage": self.percentage(),
                "is_low": self.is_low(), "is_critical": self.is_critical()}


class SensorsNamespace(_Namespace):
    def distance(self) -> int:
        """ToF distance in mm. Returns -1 if unavailable."""
        return sensor_lib.get_distance() if sensor_lib else -1

    def imu(self) -> dict:
        if sensor_lib is None:
            return self._log("sensors.imu")
        return sensor_lib.get_imu()

    def buzz(self, freq_hz: int, on_secs: float = 0.1, off_secs: float = 0.05, repeat: int = 1):
        if sensor_lib is None:
            return self._log("sensors.buzz", freq_hz=freq_hz)
        return sensor_lib.buzz(freq_hz=int(freq_hz), on_secs=float(on_secs),
                               off_secs=float(off_secs), repeat=int(repeat))

    def buzz_pattern(self, pattern: str):
        if sensor_lib is None:
            return self._log("sensors.buzz_pattern", pattern=pattern)
        return sensor_lib.buzz_pattern(str(pattern))

    def init_distance_sensor(self) -> bool:
        if sensor_lib is None:
            return False
        return sensor_lib.init_tof()


class NavigationNamespace(_Namespace):
    def go_to_tag(self, tag_id: int, timeout: float = 10.0):
        if navigation_lib is None:
            return self._log("navigation.go_to_tag", tag_id=tag_id)
        return navigation_lib.navigate_to_tag(int(tag_id), timeout=float(timeout))

    def stop(self):
        if navigation_lib:
            navigation_lib.stop_navigation()
            navigation_lib.stop_follow()
        return self._log("navigation.stop")

    def follow_person(self):
        if navigation_lib is None:
            return self._log("navigation.follow_person")
        return self._owner._wrap_call("navigation.follow_person", navigation_lib.follow_person)

    def get_tag_map(self) -> dict:
        return navigation_lib.get_tag_map() if navigation_lib else {}

    def update_tag(self, tag_id: int, cx: int, cy: int, area: float):
        """Called internally by vision.find_tag to keep the map fresh."""
        if navigation_lib:
            navigation_lib.update_tag_map(int(tag_id), int(cx), int(cy), float(area))


class PatrolNamespace(_Namespace):
    def start(self):
        if patrol_lib is None:
            return self._log("patrol.start")
        return patrol_lib.start()

    def stop(self) -> dict:
        if patrol_lib is None:
            return self._log("patrol.stop")
        return patrol_lib.stop()

    def log(self) -> list:
        return patrol_lib.get_log() if patrol_lib else []

    def update_frame(self, frame):
        if patrol_lib:
            patrol_lib.update_frame(frame)


class HelpNamespace:
    """Callable help system — myRobot.help() or myRobot.help.vision() etc."""

    _W = 60

    def __call__(self):
        """Print all available namespaces."""
        print("=" * self._W)
        print("  MataTonyPi — Quick Reference")
        print("  Call myRobot.help.<namespace>() for details")
        print("-" * self._W)
        namespaces = [
            ("myRobot.help.vision()",     "camera, colour, YOLO, face, hands, pose"),
            ("myRobot.help.pickup()",     "find, approach, grab, lift, carry, place"),
            ("myRobot.help.head()",       "look, nod, shake, scan, wiggle, glance"),
            ("myRobot.help.motion()",     "walk, turn, step"),
            ("myRobot.help.arms()",       "raise, open, close, grab pose"),
            ("myRobot.help.pose()",       "stand, sit, bow, neutral, ready"),
            ("myRobot.help.anim()",       "action groups, dance, wave, run by name/id"),
            ("myRobot.help.emotion()",    "happy, sad, excited, confused, greet"),
            ("myRobot.help.voice()",      "say, greet, celebrate, select voice"),
            ("myRobot.help.battery()",    "voltage, percentage, is_low, is_critical"),
            ("myRobot.help.sensors()",    "distance (ToF), imu, buzzer"),
            ("myRobot.help.navigation()", "go_to_tag, follow_person, stop"),
            ("myRobot.help.team()",       "multi-robot cues, signal, broadcast"),
            ("myRobot.help.games()",      "Simon Says colour memory game"),
            ("myRobot.help.patrol()",     "autonomous patrol with obstacle log"),
        ]
        for call, desc in namespaces:
            print(f"  {call:<35} {desc}")
        print("-" * self._W)
        print("  myRobot.status()    full backend status")
        print("  myRobot.versions()  library version table")
        print("  myRobot.diagnose()  hardware diagnostic")
        print("=" * self._W)

    def all(self):
        """Print every command across all namespaces."""
        self.vision()
        self.pickup()
        self.head()
        self.motion()
        self.arms()
        self.pose()
        self.anim()
        self.emotion()
        self.voice()
        self.battery()
        self.sensors()
        self.navigation()
        self.team()
        self.games()
        self.patrol()

    def _header(self, title: str):
        print("=" * self._W)
        print(f"  {title}")
        print("-" * self._W)

    def _footer(self):
        print("=" * self._W)

    def _line(self, call: str, desc: str):
        print(f"  {call:<42} # {desc}")

    def vision(self):
        self._header("myRobot.vision — Camera & Detection")
        self._line('myRobot.vision.snapshot()',                   'take a photo, show in Jupyter')
        self._line('myRobot.vision.find_color("red")',            'find red blob, show annotated frame')
        self._line('myRobot.vision.find_object("cup")',           'find named object via YOLO')
        self._line('myRobot.vision.detect_objects()',             'detect all objects via YOLO')
        self._line('myRobot.vision.detect_objects(confidence=0.3)','lower threshold = more detections')
        self._line('myRobot.vision.find_face()',                  'detect a face')
        self._line('myRobot.vision.find_faces()',                 'detect all faces')
        self._line('myRobot.vision.recognize_hands()',            'detect hands + gestures')
        self._line('myRobot.vision.detect_pose()',                'body pose: hands_up, t_pose ...')
        self._line('myRobot.vision.find_tag(1)',                  'find AprilTag ID 1')
        self._line('myRobot.vision.target_position("red")',       'direction: left / center / right / lost')
        self._line('myRobot.vision.locate_object("red")',         'target_position + angle + depth')
        self._line('myRobot.vision.which_object("red")',          'index of largest object (L to R)')
        self._line('myRobot.vision.estimate_distance(px_w, 4.5)','depth in cm from pixel width + real size')
        self._line('myRobot.vision.calibrate_color("red")',       'calibrate colour from frame centre')
        self._line('myRobot.vision.set_color_profile("red",...)', 'set custom HSV range')
        self._line('myRobot.vision.show_profiles()',              'print all colour profiles')
        self._line('myRobot.vision.object_classes()',             'list all 80 YOLO class names')
        self._line('myRobot.vision.yolo_available()',             'True if YOLO installed')
        self._line('myRobot.vision.describe()',                   'AI scene description (Claude API)')
        self._footer()

    def pickup(self):
        self._header("myRobot.pickup — Object Pickup")
        self._line('myRobot.pickup.find("red")',          'snapshot + detect red → DetectionResult')
        self._line('myRobot.pickup.find("cup")',          'snapshot + detect cup via YOLO')
        self._line('myRobot.pickup.approach_object("red")','walk toward object')
        self._line('myRobot.pickup.pick_up("red")',       'run grab action sequence')
        self._line('myRobot.pickup.grab_and_lift()',      'squat + grab + stand in one move')
        self._line('myRobot.pickup.lift_to_chest()',      'pick up + hold at chest height')
        self._line('myRobot.pickup.grab()',               'grab (no name needed)')
        self._line('myRobot.pickup.carry()',              'arms into carry posture')
        self._line('myRobot.pickup.place_down()',         'set object down')
        self._line('myRobot.pickup.release()',            'open hand')
        self._line('myRobot.pickup.transport("red")',     'carry and walk')
        self._footer()

    def head(self):
        self._header("myRobot.head — Head Movement")
        self._line('myRobot.head.look_left()',      'pan left')
        self._line('myRobot.head.look_right()',     'pan right')
        self._line('myRobot.head.look_up()',        'tilt up')
        self._line('myRobot.head.look_down()',      'tilt down (use before floor pickup)')
        self._line('myRobot.head.center()',         'return to centre')
        self._line('myRobot.head.centre()',         'same as center() (British spelling)')
        self._line('myRobot.head.nod()',            'nod yes')
        self._line('myRobot.head.shake()',          'shake no')
        self._line('myRobot.head.scan()',           'look left then right then centre')
        self._line('myRobot.head.wiggle(cycles=2)', 'friendly left-right wiggle')
        self._line('myRobot.head.glance_left()',    'quick look left then back')
        self._line('myRobot.head.glance_right()',   'quick look right then back')
        self._line('myRobot.head.tiny_wiggle(2)',   'subtle wiggle for 2 seconds')
        self._footer()

    def motion(self):
        self._header("myRobot.motion — Walking & Turning")
        self._line('myRobot.motion.walk_forward(steps=1)',  'walk forward')
        self._line('myRobot.motion.walk_backward(steps=1)', 'walk backward')
        self._line('myRobot.motion.walk_fast(steps=1)',     'fast walk forward')
        self._line('myRobot.motion.turn_left(steps=1)',     'turn left')
        self._line('myRobot.motion.turn_right(steps=1)',    'turn right')
        self._line('myRobot.motion.turn_left_fast()',       'fast turn left')
        self._line('myRobot.motion.turn_right_fast()',      'fast turn right')
        self._line('myRobot.motion.step_left(steps=1)',     'side step left')
        self._line('myRobot.motion.step_right(steps=1)',    'side step right')
        self._line('myRobot.motion.creep(steps=1)',         'slow stealth creep forward')
        self._line('myRobot.motion.approach()',             'one step forward')
        self._line('myRobot.motion.stop()',                 'stop all motion')
        self._footer()

    def arms(self):
        self._header("myRobot.arms — Arm Poses")
        self._line('myRobot.arms.left_up()',      'raise left arm')
        self._line('myRobot.arms.right_up()',     'raise right arm')
        self._line('myRobot.arms.hands_up()',     'raise both arms')
        self._line('myRobot.arms.open()',         'open arms wide')
        self._line('myRobot.arms.close()',        'close/fold arms in')
        self._line('myRobot.arms.center()',       'arms to neutral/sides')
        self._line('myRobot.arms.grab_pose()',    'arms into grab position')
        self._line('myRobot.arms.carry_pose()',   'arms into carry position')
        self._line('myRobot.arms.release_pose()', 'open arms to release')
        self._line('myRobot.arms.punch_left()',   'fast left uppercut')
        self._line('myRobot.arms.punch_right()',  'fast right uppercut')
        self._line('myRobot.arms.punch()',        'left then right uppercut')
        self._line('myRobot.arms.kick_left()',    'left kick')
        self._line('myRobot.arms.kick_right()',   'right kick')
        self._footer()

    def pose(self):
        self._header("myRobot.pose — Body Poses")
        self._line('myRobot.pose.stand()',   'stand upright — most common reset')
        self._line('myRobot.pose.ready()',   'stand, arms slightly out')
        self._line('myRobot.pose.neutral()', 'stand, relaxed home position')
        self._line('myRobot.pose.bow()',     'bow forward')
        self._line('myRobot.pose.sit()',     'sit / squat down')
        self._line('myRobot.pose.carry()',   'carry posture')
        self._footer()

    def anim(self):
        self._header("myRobot.anim — Action Groups & Animation")
        self._line('myRobot.anim.wave()',                     'wave hello')
        self._line('myRobot.anim.dance()',                    'do a dance move')
        self._line('myRobot.anim.celebrate()',                'celebrate with uppercut')
        self._line('myRobot.anim.martial_arts()',             'wing chun sequence')
        self._line('myRobot.anim.bow_deep()',                 'deep formal bow')
        self._line('myRobot.anim.catch_ball()',               'ball catching sequence')
        self._line('myRobot.anim.run("wave")',                'run action group by name')
        self._line('myRobot.anim.run("go_forward", times=3)', 'run action group N times')
        self._line('myRobot.anim.run("17")',                  'run numbered dance (16–24)')
        self._line('myRobot.anim.run_id(16)',                 'run action group by numeric ID')
        self._line('myRobot.anim.show_action_groups()',       'print all installed action groups')
        self._line('myRobot.anim.list_action_groups()',       'return list of action group names')
        self._line('myRobot.anim.dance_moves()',              'return dance action groups only')
        self._footer()

    def emotion(self):
        self._header("myRobot.emotion — Emotions")
        self._line('myRobot.emotion.happy()',          'raise arms + bob head + cheerful beep')
        self._line('myRobot.emotion.sad()',            'drop arms + tilt head + low buzz')
        self._line('myRobot.emotion.excited()',        'wave + rapid high beeps')
        self._line('myRobot.emotion.confused()',       'head tilts left/right + mid beep')
        self._line('myRobot.emotion.greet()',          'wave + short beep')
        self._line('myRobot.emotion.express("happy")', 'express emotion by name')
        self._line('myRobot.emotion.is_busy()',        'True if currently expressing')
        self._line('myRobot.emotion.available()',      'list of emotion names')
        self._footer()

    def voice(self):
        self._header("myRobot.voice — Speech")
        self._line('myRobot.voice.say("Hello!")',           'speak (waits until done)')
        self._line('myRobot.voice.say("Hi", block=False)',  'speak in background')
        self._line('myRobot.voice.greet()',                 'say "Hello everyone."')
        self._line('myRobot.voice.celebrate()',             'say "Yay. Great job."')
        self._line('myRobot.voice.think()',                 'say "Hmm. Let me think."')
        self._line('myRobot.voice.show_voices()',            'list installed voices + show active')
        self._line('myRobot.voice.current_voice()',         'print the active voice name')
        self._line('myRobot.voice.select("ryan")',          'switch voice by name (persists)')
        self._line('myRobot.voice.select_voice_number(2)',  'switch voice by number (persists)')
        self._footer()

    def battery(self):
        self._header("myRobot.battery — Battery")
        self._line('myRobot.battery.percentage()',  'battery level 0–100')
        self._line('myRobot.battery.voltage()',     'battery voltage e.g. 11.4')
        self._line('myRobot.battery.is_low()',      'True if below 10.5V')
        self._line('myRobot.battery.is_critical()', 'True if below 10.0V')
        self._line('myRobot.battery.status()',      'dict with all battery info')
        self._footer()

    def sensors(self):
        self._header("myRobot.sensors — Sensors")
        self._line('myRobot.sensors.distance()',             'ToF distance in mm (-1 if no sensor)')
        self._line('myRobot.sensors.init_distance_sensor()', 'start ToF sensor')
        self._line('myRobot.sensors.imu()',                  'accelerometer data dict')
        self._line('myRobot.sensors.buzz(1800)',             'beep at 1800Hz for 0.1s')
        self._line('myRobot.sensors.buzz(1800, 0.3)',        'beep at 1800Hz for 0.3s')
        self._line('myRobot.sensors.buzz_pattern("happy")',  'named: happy sad sos short long')
        self._footer()

    def navigation(self):
        self._header("myRobot.navigation — Navigation")
        self._line('myRobot.navigation.go_to_tag(1)',      'walk to AprilTag ID 1')
        self._line('myRobot.navigation.go_to_tag(2, timeout=15)', 'with 15s timeout')
        self._line('myRobot.navigation.follow_person()',   'follow a person (YOLO + ToF)')
        self._line('myRobot.navigation.stop()',            'stop navigation or following')
        self._line('myRobot.navigation.get_tag_map()',     'last seen position of each tag')
        self._footer()

    def team(self):
        self._header("myRobot.team — Multi-Robot")
        self._line('myRobot.team.local_ip()',                              'this robot\'s IP address')
        self._line('myRobot.team.start_server()',                          'start cue server')
        self._line('myRobot.team.stop_server()',                           'stop cue server')
        self._line('myRobot.team.signal("192.168.1.42", cue="go")',        'send cue to one robot')
        self._line('myRobot.team.broadcast(["1.42","1.43"], cue="start")', 'send to many robots')
        self._line('myRobot.team.wait_for("go")',                          'block until cue arrives')
        self._line('myRobot.team.wait_for("go", timeout=10)',              'wait up to 10 seconds')
        self._line('myRobot.team.cues()',                                  'list received cues')
        self._footer()

    def games(self):
        self._header("myRobot.games — Games")
        self._line('myRobot.games.simon_says()',             'start Simon Says (default difficulty 2)')
        self._line('myRobot.games.simon_says(difficulty=1)', 'easy: 4 rounds, 5s timeout')
        self._line('myRobot.games.simon_says(difficulty=2)', 'medium: 8 rounds, 5s timeout')
        self._line('myRobot.games.simon_says(difficulty=3)', 'hard: 8 rounds, 3s timeout')
        self._line('myRobot.games.stop_game()',              'stop current game')
        self._line('myRobot.games.is_game_running()',        'True if game in progress')
        self._footer()

    def patrol(self):
        self._header("myRobot.patrol — Autonomous Patrol")
        self._line('myRobot.patrol.start()',         'begin patrol + obstacle logging')
        self._line('myRobot.patrol.stop()',          'stop, save JSON log, optional AI summary')
        self._line('myRobot.patrol.log()',           'current obstacle log list')
        self._footer()


class GamesNamespace(_Namespace):
    def simon_says(self, difficulty: int = 2):
        if games_lib is None:
            return self._log("games.simon_says")
        games_lib.set_difficulty(int(difficulty))
        return games_lib.start_game()

    def stop_game(self):
        return games_lib.stop_game() if games_lib else self._log("games.stop")

    def is_game_running(self) -> bool:
        return games_lib.is_running() if games_lib else False

    def set_difficulty(self, level: int):
        if games_lib:
            games_lib.set_difficulty(int(level))


class RobotV2:
    def __init__(self, verbose: bool = True):
        self.verbose = bool(verbose)
        self.anim = AnimationNamespace(self)
        self.head = HeadNamespace(self)
        self.arms = ArmsNamespace(self)
        self.pose = PoseNamespace(self)
        self.motion = MotionNamespace(self)
        self.vision = VisionNamespace(self)
        self.pickup = PickupNamespace(self)
        self.voice = VoiceNamespace(self)
        self.controller = ControllerNamespace(self)
        self.team = TeamNamespace(self)
        self.tts = self.voice
        self.emotion    = EmotionNamespace(self)
        self.battery    = BatteryNamespace(self)
        self.sensors    = SensorsNamespace(self)
        self.navigation = NavigationNamespace(self)
        self.patrol     = PatrolNamespace(self)
        self.games      = GamesNamespace(self)
        self.help       = HelpNamespace()
        if battery_lib is not None:
            try:
                battery_lib.start_monitoring()
            except Exception:
                pass

    def _backend_name(self) -> str:
        return "tonypi" if support.vendor_available() else "stub"

    def _log(self, action: str, **kwargs) -> dict[str, Any]:
        payload = {"ok": True, "action": action, "kwargs": kwargs, "backend": self._backend_name()}
        if self.verbose:
            print(f"[student_robot_v2] {action} {kwargs}".rstrip())
        return payload

    def _run_named_action(self, action: str, candidates, times: int = 1):
        resolved = support.resolve_action_name(candidates)
        if resolved is None:
            payload = self._log(action, candidates=list(candidates), times=int(times))
            payload["ok"] = False
            payload["note"] = "TonyPi action group unavailable"
            return payload
        try:
            result = action_group_lib.run(resolved, times=max(1, int(times)))
            payload = self._log(action, resolved=resolved, times=int(times))
            payload["resolved"] = resolved
            payload["result"] = result
            return payload
        except Exception as exc:
            payload = self._log(action, resolved=resolved, times=int(times))
            payload["ok"] = False
            payload["note"] = str(exc)
            return payload

    def _set_head(self, vertical: int | None = None, horizontal: int | None = None, duration_ms: int = 300):
        try:
            result = support.set_head(vertical=vertical, horizontal=horizontal, duration_ms=duration_ms)
            payload = self._log("head.move", **result)
            payload["result"] = result
            return payload
        except Exception as exc:
            payload = self._log("head.move", vertical=vertical, horizontal=horizontal, duration_ms=int(duration_ms))
            payload["ok"] = False
            payload["note"] = str(exc)
            return payload

    def _wrap_call(self, action: str, fn, **kwargs):
        try:
            result = fn(**kwargs)
            payload = self._log(action, **kwargs)
            payload["result"] = result
            return payload
        except Exception as exc:
            payload = self._log(action, **kwargs)
            payload["ok"] = False
            payload["note"] = str(exc)
            return payload

    def say(self, text: str, block: bool = True, voice: str | None = None):
        try:
            result = tts_lib.say(text=text, voice=voice, block=block)
            payload = self._log("say", text=str(text), block=bool(block), voice=voice)
            payload["result"] = result
            return payload
        except Exception as exc:
            payload = self._log("say", text=str(text), block=bool(block), voice=voice)
            payload["ok"] = False
            payload["note"] = str(exc)
            return payload

    def stop(self):
        support.stop_actions()
        return self._log("stop")

    def versions(self) -> dict[str, str]:
        """Print a formatted table of all library versions with ✓/✗ status and return the dict."""
        import importlib
        _LIBS = [
            "student_robot_v2", "vision_lib", "tonypi_support",
            "action_group_lib", "head_lib", "tts_lib", "signal_lib", "camera_lib",
            "emotion_lib", "battery_lib", "sensor_lib", "yolo_lib",
            "navigation_lib", "patrol_lib", "games_lib",
        ]
        result = {}
        for name in _LIBS:
            if name == "student_robot_v2":
                result[name] = __version__
                continue
            try:
                mod = importlib.import_module(name)
                result[name] = getattr(mod, "__version__", "—")
            except Exception:
                result[name] = "not installed"

        W = 46
        print("=" * W)
        print("  MataTonyPi — Library Versions")
        print("-" * W)
        for name, ver in result.items():
            ok = ver != "not installed"
            icon = "✓" if ok else "✗"
            err = f"  ← {_lib_errors.get(name, '')}" if not ok else ""
            print(f"  {icon}  {name:<22} {ver}{err}")
        print("=" * W)
        return result

    def show_versions(self):
        """Alias for versions() — prints and returns the version table."""
        return self.versions()

    def status(self):
        """Print a human-readable status of every backend and return a dict."""
        W = 46
        print("=" * W)
        print("  MataTonyPi — Status")
        print(f"  student_robot_v2: {__version__}")
        print("-" * W)

        def _line(label, mod, key=None):
            if mod is not None:
                print(f"  ✓  {label:<18} ready")
            else:
                err = _lib_errors.get(key or label, "import failed")
                print(f"  ✗  {label:<18} unavailable  ← {err}")

        _line("vision_lib",    vision_lib,    "vision_lib")
        _line("tts_lib",       tts_lib,       "tts_lib")
        _line("emotion_lib",   emotion_lib,   "emotion_lib")
        _line("battery_lib",   battery_lib,   "battery_lib")
        _line("sensor_lib",    sensor_lib,    "sensor_lib")
        _line("yolo_lib",      yolo_lib,      "yolo_lib")
        _line("navigation_lib",navigation_lib,"navigation_lib")
        _line("patrol_lib",    patrol_lib,    "patrol_lib")
        _line("games_lib",     games_lib,     "games_lib")

        yolo_ok = yolo_lib is not None and yolo_lib.is_available()
        print(f"  {'✓' if yolo_ok else '✗'}  {'YOLO model':<18} {'ready (yolov8n)' if yolo_ok else 'not installed  ← pip install ultralytics'}")

        vendor_ok = support.vendor_available()
        ag_count = len(support.list_action_groups())
        print(f"  {'✓' if vendor_ok else '✗'}  {'vendor TonyPi':<18} {'found' if vendor_ok else 'not found'}")
        print(f"  {'✓' if ag_count else '✗'}  {'action groups':<18} {ag_count} found")

        if _lib_errors:
            print("-" * W)
            print("  Load errors:")
            for name in sorted(_lib_errors):
                print(f"    {name}: {_lib_errors[name]}")
        print("=" * W)

        return {
            "robot": "MataTonyPi",
            "version": __version__,
            "backend": self._backend_name(),
            "vendor_root": str(support.resolve_vendor_root()),
            "action_groups_found": ag_count,
            "dance_action_groups": len(support.dance_action_groups()),
            "yolo_available": yolo_ok,
            "battery_pct": self.battery.percentage(),
            "tof_distance_mm": self.sensors.distance(),
            "lib_errors": dict(_lib_errors),
        }

    def diagnose(self) -> dict:
        """Full hardware diagnostic — run before class to confirm the robot is ready.

        Tests:
          1. head    — nod + center
          2. camera  — capture frame + show in Jupyter
          3. voice   — say "Ready"
          4. buzzer  — two-tone confirmation beep
          5. ToF     — read distance sensor
          6. battery — read voltage
          7. YOLO    — check ultralytics + model file
          8. actions — confirm action groups are loaded

        Prints a ✓/✗ pass/fail table. Returns dict of results.
        """
        import time as _time

        results: dict = {}

        def _pass(name, detail):
            results[name] = {"ok": True, "detail": detail}

        def _fail(name, detail):
            results[name] = {"ok": False, "detail": detail}

        W = 46
        print("=" * W)
        print("  ROBOT DIAGNOSTIC — MataTonyPi")
        print(f"  student_robot_v2 {__version__}  |  vision_lib {getattr(vision_lib, '__version__', '?')}")
        print(f"  backend: {self._backend_name()}")
        print("-" * W)

        # 1. Head servos
        try:
            self.head.nod()
            _time.sleep(0.1)
            self.head.center()
            _pass("head", "nod + center OK")
        except Exception as e:
            _fail("head", str(e))

        # 2. Camera
        try:
            vis = vision_lib.get_vision()
            frame = vis._capture_frame()
            h, w = frame.shape[:2]
            vis.show_image(frame, title="Diagnostic — camera frame")
            _pass("camera", f"{w}×{h} frame captured")
        except Exception as e:
            _fail("camera", str(e))

        # 3. Voice
        try:
            self.say("Ready.", block=True)
            _pass("voice", 'said "Ready."')
        except Exception as e:
            _fail("voice", str(e))

        # 4. Buzzer
        try:
            board = support.get_board()
            if board is None:
                raise RuntimeError("Board unavailable")
            board.set_buzzer(1000, 0.15, 0.05, 1)
            _time.sleep(0.25)
            board.set_buzzer(1200, 0.15, 0.05, 1)
            _pass("buzzer", "two-tone beep")
        except Exception as e:
            _fail("buzzer", str(e))

        # 5. ToF distance sensor
        try:
            if sensor_lib is None:
                raise RuntimeError(_lib_errors.get("sensor_lib", "sensor_lib not loaded"))
            dist = sensor_lib.get_distance()
            if dist == -1:
                _fail("ToF sensor", "no reading — sensor not initialised or not connected")
            else:
                _pass("ToF sensor", f"{dist} mm")
        except Exception as e:
            _fail("ToF sensor", str(e))

        # 6. Battery
        try:
            if battery_lib is None:
                raise RuntimeError(_lib_errors.get("battery_lib", "battery_lib not loaded"))
            v = battery_lib.get_voltage()
            pct = battery_lib.get_percentage()
            if v < battery_lib.WARN_V:
                _fail("battery", f"{v:.2f}V ({pct}%) — LOW, please charge")
            else:
                _pass("battery", f"{v:.2f}V ({pct}%)")
        except Exception as e:
            _fail("battery", str(e))

        # 7. YOLO
        try:
            from ultralytics import YOLO as _YOLO  # noqa: F401
            from pathlib import Path as _Path
            model_paths = [
                _Path("/opt/robot/models/yolov8n.pt"),
                _Path.home() / ".config" / "Ultralytics" / "yolov8n.pt",
            ]
            found = next((p for p in model_paths if p.exists()), None)
            if found:
                _pass("YOLO", f"yolov8n.pt at {found}")
            else:
                _fail("YOLO", "ultralytics installed but yolov8n.pt not found — run: python3 -c \"from ultralytics import YOLO; YOLO('yolov8n.pt')\"")
        except ImportError:
            _fail("YOLO", "not installed — run: pip install ultralytics")
        except Exception as e:
            _fail("YOLO", str(e))

        # 8. Action groups
        try:
            ag = support.list_action_groups()
            if not ag:
                _fail("action groups", "none found — check vendor TonyPi install")
            else:
                _pass("action groups", f"{len(ag)} loaded")
        except Exception as e:
            _fail("action groups", str(e))

        # Summary
        print("-" * W)
        for name, r in results.items():
            icon = "✓" if r["ok"] else "✗"
            print(f"  {icon}  {name:<14}  {r['detail']}")
        print("-" * W)
        passed = sum(1 for r in results.values() if r["ok"])
        total = len(results)
        if passed == total:
            print(f"  RESULT:  {passed}/{total} — READY FOR CLASS ✓")
        else:
            failed = [n for n, r in results.items() if not r["ok"]]
            print(f"  RESULT:  {passed}/{total} — CHECK: {', '.join(failed)}")
        print("=" * W)
        return results

    def home(self):
        self.head.center()
        return self.pose.stand()

    def stand(self):
        return self.pose.stand()

    def sit(self):
        return self.pose.sit()


_LOCK_KEY = "__mata_tonypi_bot_lock__"
_SINGLETON_KEY = "__mata_tonypi_bot__"


def _get_lock() -> threading.Lock:
    lock = getattr(builtins, _LOCK_KEY, None)
    if lock is None:
        lock = threading.Lock()
        setattr(builtins, _LOCK_KEY, lock)
    return lock


def bot(verbose: bool = True) -> RobotV2:
    with _get_lock():
        inst = getattr(builtins, _SINGLETON_KEY, None)
        if inst is None:
            inst = RobotV2(verbose=verbose)
            setattr(builtins, _SINGLETON_KEY, inst)
        return inst


__all__ = ["DetectionResult", "RobotV2", "bot", "__version__"]
