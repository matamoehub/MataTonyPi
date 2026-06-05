#!/usr/bin/env python3
"""Single public student-facing API for MataTonyPi."""

from __future__ import annotations

__version__ = "1.3.0"

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
import signal_lib
import tonypi_support as support
import tts_lib
import vision_lib

try:
    import emotion_lib
except Exception:
    emotion_lib = None

try:
    import battery_lib
except Exception:
    battery_lib = None

try:
    import sensor_lib
except Exception:
    sensor_lib = None

try:
    import yolo_lib
except Exception:
    yolo_lib = None

try:
    import navigation_lib
except Exception:
    navigation_lib = None

try:
    import patrol_lib
except Exception:
    patrol_lib = None

try:
    import games_lib
except Exception:
    games_lib = None


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
        return self._run_action("anim.dance", ["dance", "twist", ("happy",), ("celebrate",)])

    def celebrate(self):
        return self._run_action("anim.celebrate", ["dance", "wave", "twist", ("celebrate",)])

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
        return self._run_action("arms.left_up", [("left", "hand", "up"), ("left", "arm", "up"), ("raise", "left")])

    def right_up(self):
        return self._run_action("arms.right_up", [("right", "hand", "up"), ("right", "arm", "up"), ("raise", "right")])

    def hands_up(self):
        return self._run_action("arms.hands_up", [("hands", "up"), ("raise", "hands"), ("both", "hands", "up")])

    def open(self):
        return self._run_action("arms.open", [("open", "hand"), ("open", "arm"), ("open",)])

    def close(self):
        return self._run_action("arms.close", [("close", "hand"), ("close", "arm"), ("close",)])

    def center(self):
        return self._run_action("arms.center", [("stand",), ("home", "arm"), ("center", "arm")])

    def grab_pose(self):
        return self._run_action("arms.grab_pose", [("grab",), ("pickup",), ("pick",)])

    def carry_pose(self):
        return self._run_action("arms.carry_pose", [("carry",), ("hold",)])

    def release_pose(self):
        return self._run_action("arms.release_pose", [("release",), ("place",), ("put", "down")])


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
        return self._run_action("pose.sit", ["sit", ("squat",), ("rest",)])

    def carry(self):
        return self._run_action("pose.carry", [("carry",), ("hold",)])


class MotionNamespace(_Namespace):
    def _steps(self, action: str, candidates, steps: int = 1):
        return self._owner._run_named_action(action, candidates, times=max(1, int(steps)))

    def walk_forward(self, steps: int = 1):
        return self._steps("motion.walk_forward", ["go_forward", ("forward",)], steps=steps)

    def walk_backward(self, steps: int = 1):
        return self._steps("motion.walk_backward", ["back", "go_back", ("backward",)], steps=steps)

    def turn_left(self, steps: int = 1):
        return self._steps("motion.turn_left", ["turn_left_small_step", "turn_left", ("left", "turn")], steps=steps)

    def turn_right(self, steps: int = 1):
        return self._steps("motion.turn_right", ["turn_right_small_step", "turn_right", ("right", "turn")], steps=steps)

    def step_left(self, steps: int = 1):
        return self._steps("motion.step_left", ["left_move", "left_move_large", ("left", "move")], steps=steps)

    def step_right(self, steps: int = 1):
        return self._steps("motion.step_right", ["right_move", "right_move_large", ("right", "move")], steps=steps)

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
        import os, base64, urllib.request, json
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
                "model": "claude-opus-4-5",
                "max_tokens": 200,
                "system": ("You are the vision system of a small humanoid robot called TonyPi. "
                           "Describe what you see in 1-2 short sentences, conversationally."),
                "messages": [{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64",
                     "media_type": "image/jpeg", "data": b64}},
                    {"type": "text", "text": "What do you see?"}
                ]}],
            }
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps(payload).encode(),
                headers={"x-api-key": api_key, "anthropic-version": "2023-06-01",
                         "content-type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())["content"][0]["text"]
        except Exception as e:
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
        return self._run_action("pickup.approach_object", [("approach",), ("pickup",), ("transport",)])

    def pick_up(self, name: str):
        return self._run_action("pickup.pick_up", [("pick",), ("pickup",), ("grab",)])

    def grab(self):
        return self._run_action("pickup.grab", [("grab",), ("pickup",)])

    def carry(self):
        return self._run_action("pickup.carry", [("carry",), ("transport",)])

    def place_down(self):
        return self._run_action("pickup.place_down", [("place",), ("put", "down"), ("release",)])

    def release(self):
        return self._run_action("pickup.release", [("release",), ("open", "hand")])

    def transport(self, name: str):
        return self._run_action("pickup.transport", [("transport",), ("carry",)])


class VoiceNamespace(_Namespace):
    def say(self, text: str, block: bool = True, voice: str | None = None):
        return self._owner.say(text=text, block=block, voice=voice)

    def speak(self, text: str, block: bool = True, voice: str | None = None):
        return self.say(text=text, block=block, voice=voice)

    def voices(self):
        return tts_lib.available_voices(installed_only=True)

    def show_voices(self):
        return self.voices()

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

    def status(self):
        return {
            "robot": "MataTonyPi",
            "backend": self._backend_name(),
            "vendor_root": str(support.resolve_vendor_root()),
            "action_groups_found": len(support.list_action_groups()),
            "dance_action_groups": len(support.dance_action_groups()),
            "yolo_available": yolo_lib is not None and yolo_lib.is_available(),
            "battery_pct": self.battery.percentage(),
            "tof_distance_mm": self.sensors.distance(),
            "namespaces": [
                "anim", "head", "arms", "pose", "motion", "vision",
                "pickup", "voice", "controller", "team",
                "emotion", "battery", "sensors", "navigation", "patrol", "games",
            ],
        }

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


__all__ = ["DetectionResult", "RobotV2", "bot"]
