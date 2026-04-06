#!/usr/bin/env python3
"""Single public student-facing API for MataTonyPi."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import time
from typing import Any

import action_group_lib
import head_lib
import tonypi_support as support
import tts_lib
import vision_lib


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
        self._log("vision.find_object", name=str(name))
        return DetectionResult(found=False, label=str(name), note="Object detection backend not implemented yet")

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
        return DetectionResult(found=True, label=f"tag:{int(tag_id)}", x=int(tag["cx"]), y=int(tag["cy"]), area=0, confidence=1.0, note=result.get("path", ""))

    def track_color(self, name: str):
        return vision_lib.get_vision().find_color(str(name), show=True)

    def track_face(self):
        self._prepare_face_capture()
        return vision_lib.get_vision().find_face(show=True)

    def snapshot(self):
        return vision_lib.get_vision().snapshot(show=True)

    def scan_for(self, name: str):
        if str(name).lower() == "face":
            self._prepare_face_capture()
            return vision_lib.get_vision().find_face(show=True)
        return vision_lib.get_vision().find_color(str(name), show=True)


class PickupNamespace(_Namespace):
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
        self.tts = self.voice

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
            "namespaces": ["anim", "head", "arms", "pose", "motion", "vision", "pickup", "voice"],
        }

    def home(self):
        self.head.center()
        return self.pose.stand()

    def stand(self):
        return self.pose.stand()

    def sit(self):
        return self.pose.sit()


def bot(verbose: bool = True) -> RobotV2:
    return RobotV2(verbose=verbose)


__all__ = ["DetectionResult", "RobotV2", "bot"]
