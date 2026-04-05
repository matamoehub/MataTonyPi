#!/usr/bin/env python3
"""Single public student-facing API for MataTonyPi."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


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


class AnimationNamespace(_Namespace):
    def wave(self):
        return self._log("anim.wave")

    def greet(self):
        return self._log("anim.greet")

    def dance(self):
        return self._log("anim.dance")

    def celebrate(self):
        return self._log("anim.celebrate")

    def think(self):
        return self._log("anim.think")

    def sad(self):
        return self._log("anim.sad")

    def yes(self):
        return self._log("anim.yes")

    def no(self):
        return self._log("anim.no")

    def scan(self):
        return self._log("anim.scan")


class HeadNamespace(_Namespace):
    def look_left(self):
        return self._log("head.look_left")

    def look_right(self):
        return self._log("head.look_right")

    def look_up(self):
        return self._log("head.look_up")

    def look_down(self):
        return self._log("head.look_down")

    def center(self):
        return self._log("head.center")

    def nod(self):
        return self._log("head.nod")

    def shake(self):
        return self._log("head.shake")

    def scan(self):
        return self._log("head.scan")


class ArmsNamespace(_Namespace):
    def left_up(self):
        return self._log("arms.left_up")

    def right_up(self):
        return self._log("arms.right_up")

    def hands_up(self):
        return self._log("arms.hands_up")

    def open(self):
        return self._log("arms.open")

    def close(self):
        return self._log("arms.close")

    def center(self):
        return self._log("arms.center")

    def grab_pose(self):
        return self._log("arms.grab_pose")

    def carry_pose(self):
        return self._log("arms.carry_pose")

    def release_pose(self):
        return self._log("arms.release_pose")


class PoseNamespace(_Namespace):
    def ready(self):
        return self._log("pose.ready")

    def neutral(self):
        return self._log("pose.neutral")

    def bow(self):
        return self._log("pose.bow")

    def stand(self):
        return self._log("pose.stand")

    def sit(self):
        return self._log("pose.sit")

    def carry(self):
        return self._log("pose.carry")


class MotionNamespace(_Namespace):
    def walk_forward(self, steps: int = 1):
        return self._log("motion.walk_forward", steps=int(steps))

    def walk_backward(self, steps: int = 1):
        return self._log("motion.walk_backward", steps=int(steps))

    def turn_left(self, steps: int = 1):
        return self._log("motion.turn_left", steps=int(steps))

    def turn_right(self, steps: int = 1):
        return self._log("motion.turn_right", steps=int(steps))

    def step_left(self, steps: int = 1):
        return self._log("motion.step_left", steps=int(steps))

    def step_right(self, steps: int = 1):
        return self._log("motion.step_right", steps=int(steps))

    def approach(self):
        return self._log("motion.approach")

    def stop(self):
        return self._owner.stop()


class VisionNamespace(_Namespace):
    def find_color(self, name: str) -> DetectionResult:
        self._log("vision.find_color", name=str(name))
        return DetectionResult(found=False, label=str(name), note="Vision backend not connected yet")

    def find_object(self, name: str) -> DetectionResult:
        self._log("vision.find_object", name=str(name))
        return DetectionResult(found=False, label=str(name), note="Object detection backend not connected yet")

    def find_face(self) -> DetectionResult:
        self._log("vision.find_face")
        return DetectionResult(found=False, label="face", note="Face detection backend not connected yet")

    def find_tag(self, tag_id: int) -> DetectionResult:
        self._log("vision.find_tag", tag_id=int(tag_id))
        return DetectionResult(found=False, label=f"tag:{int(tag_id)}", note="AprilTag backend not connected yet")

    def track_color(self, name: str):
        return self._log("vision.track_color", name=str(name))

    def track_face(self):
        return self._log("vision.track_face")

    def snapshot(self):
        return self._log("vision.snapshot")

    def scan_for(self, name: str):
        return self._log("vision.scan_for", name=str(name))


class PickupNamespace(_Namespace):
    def approach_object(self, name: str):
        return self._log("pickup.approach_object", name=str(name))

    def pick_up(self, name: str):
        return self._log("pickup.pick_up", name=str(name))

    def grab(self):
        return self._log("pickup.grab")

    def carry(self):
        return self._log("pickup.carry")

    def place_down(self):
        return self._log("pickup.place_down")

    def release(self):
        return self._log("pickup.release")

    def transport(self, name: str):
        return self._log("pickup.transport", name=str(name))


class VoiceNamespace(_Namespace):
    def say(self, text: str, block: bool = True):
        return self._owner.say(text=text, block=block)

    def greet(self):
        return self._log("voice.greet")

    def celebrate(self):
        return self._log("voice.celebrate")

    def think(self):
        return self._log("voice.think")


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

    def _log(self, action: str, **kwargs) -> dict[str, Any]:
        payload = {"ok": True, "action": action, "kwargs": kwargs, "backend": "stub"}
        if self.verbose:
            print(f"[student_robot_v2] {action} {kwargs}".rstrip())
        return payload

    def say(self, text: str, block: bool = True):
        return self._log("say", text=str(text), block=bool(block))

    def stop(self):
        return self._log("stop")

    def status(self):
        return {
            "robot": "MataTonyPi",
            "backend": "stub",
            "namespaces": ["anim", "head", "arms", "pose", "motion", "vision", "pickup", "voice"],
        }

    def home(self):
        return self._log("home")

    def stand(self):
        return self.pose.stand()

    def sit(self):
        return self.pose.sit()


def bot(verbose: bool = True) -> RobotV2:
    return RobotV2(verbose=verbose)


__all__ = ["DetectionResult", "RobotV2", "bot"]
