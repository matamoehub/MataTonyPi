#!/usr/bin/python3
# coding=utf8

import os
import cv2
import time
import base64
import asyncio
import threading
import hiwonder.ros_robot_controller_sdk as rrc
import hiwonder.ActionGroupControl as AGC
from hiwonder.Controller import Controller

board = rrc.Board()
ctl = Controller(board)

try:
    from google import genai
    from google.genai import types as genai_types
    _GENAI_AVAILABLE = True
except Exception:
    _GENAI_AVAILABLE = False

MODEL = "gemini-2.0-flash-live-001"
SYSTEM_PROMPT = """You are TonyPi, a friendly humanoid robot. You can see through your camera and hear through your microphone.
You respond to questions conversationally and can physically act on requests.
When asked to do something physical, use the available tools.
Keep spoken responses under 2 sentences — you are a robot, not a lecturer."""

_current_frame = None
_frame_lock = threading.Lock()
_stop_event = threading.Event()
_running = False
_session_thread = None

# Direction → action group mapping
_WALK_MAP = {
    'forward': 'go_forward',
    'back': 'back_fast',
    'backward': 'back_fast',
    'left': 'left_move',
    'right': 'right_move',
}
_TURN_MAP = {
    'left': 'turn_left',
    'right': 'turn_right',
}
_BUZZ_PATTERNS = {
    'short': (1500, 0.1, 0.05, 1),
    'long': (1000, 0.5, 0.2, 1),
    'happy': (1800, 0.1, 0.05, 2),
    'sad': (600, 0.4, 0.1, 1),
}


def _tool_walk(direction: str = 'forward', steps: int = 1):
    ag = _WALK_MAP.get(direction.lower(), 'go_forward')
    for _ in range(max(1, steps)):
        try:
            AGC.runActionGroup(ag)
        except Exception as e:
            print(e)
    return f'Walked {direction} {steps} step(s)'


def _tool_turn(direction: str = 'right', times: int = 1):
    ag = _TURN_MAP.get(direction.lower(), 'turn_right')
    for _ in range(max(1, times)):
        try:
            AGC.runActionGroup(ag)
        except Exception as e:
            print(e)
    return f'Turned {direction} {times} time(s)'


def _tool_run_emotion(emotion: str = 'happy'):
    try:
        from Functions import EmotionExpress
        EmotionExpress.express(emotion)
        return f'Expressing {emotion}'
    except Exception as e:
        print(e)
        return f'EmotionExpress unavailable: {e}'


def _tool_wave():
    try:
        AGC.runActionGroup('wave')
        return 'Waving'
    except Exception as e:
        print(e)
        return f'Wave failed: {e}'


def _tool_look_at(pan_angle: int = 0, tilt_angle: int = 0):
    pan_pulse = int(1500 + pan_angle * 4)
    tilt_pulse = int(1500 - tilt_angle * 4)
    pan_pulse = max(500, min(2500, pan_pulse))
    tilt_pulse = max(500, min(2500, tilt_pulse))
    try:
        ctl.set_pwm_servo_pulse(2, pan_pulse, 500)
        ctl.set_pwm_servo_pulse(1, tilt_pulse, 500)
        return f'Looking at pan={pan_angle}, tilt={tilt_angle}'
    except Exception as e:
        print(e)
        return f'Look failed: {e}'


def _tool_buzz(pattern: str = 'short'):
    if pattern == 'sos':
        # SOS: 3 short, 3 long, 3 short
        try:
            for _ in range(3):
                board.set_buzzer(1000, 0.1, 0.1, 1)
                time.sleep(0.25)
            for _ in range(3):
                board.set_buzzer(1000, 0.5, 0.2, 1)
                time.sleep(0.8)
            for _ in range(3):
                board.set_buzzer(1000, 0.1, 0.1, 1)
                time.sleep(0.25)
        except Exception as e:
            print(e)
        return 'SOS pattern'
    params = _BUZZ_PATTERNS.get(pattern.lower(), _BUZZ_PATTERNS['short'])
    try:
        board.set_buzzer(*params)
    except Exception as e:
        print(e)
    return f'Buzz: {pattern}'


def _tool_describe_scene():
    try:
        from Functions import SceneDescribe
        SceneDescribe.trigger()
        return 'Scene description triggered'
    except Exception as e:
        print(e)
        return f'SceneDescribe unavailable: {e}'


def _tool_get_battery():
    try:
        from Functions import BatteryGuard
        pct = BatteryGuard.get_percentage()
        return f'Battery: {pct}%'
    except Exception as e:
        print(e)
        return f'BatteryGuard unavailable: {e}'


_TOOL_HANDLERS = {
    'walk': _tool_walk,
    'turn': _tool_turn,
    'run_emotion': _tool_run_emotion,
    'wave': _tool_wave,
    'look_at': _tool_look_at,
    'buzz': _tool_buzz,
    'describe_scene': _tool_describe_scene,
    'get_battery': _tool_get_battery,
}

_TOOL_DECLARATIONS = [
    {
        "name": "walk",
        "description": "Walk in a direction",
        "parameters": {
            "type": "object",
            "properties": {
                "direction": {"type": "string", "enum": ["forward", "back", "left", "right"]},
                "steps": {"type": "integer", "description": "Number of steps"}
            },
            "required": ["direction"]
        }
    },
    {
        "name": "turn",
        "description": "Turn the robot",
        "parameters": {
            "type": "object",
            "properties": {
                "direction": {"type": "string", "enum": ["left", "right"]},
                "times": {"type": "integer", "description": "Number of turns"}
            },
            "required": ["direction"]
        }
    },
    {
        "name": "run_emotion",
        "description": "Express an emotion",
        "parameters": {
            "type": "object",
            "properties": {
                "emotion": {"type": "string", "enum": ["happy", "sad", "excited", "confused", "greet"]}
            },
            "required": ["emotion"]
        }
    },
    {
        "name": "wave",
        "description": "Wave hello",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "look_at",
        "description": "Move head to look in a direction",
        "parameters": {
            "type": "object",
            "properties": {
                "pan_angle": {"type": "integer", "description": "Horizontal angle -90 to 90"},
                "tilt_angle": {"type": "integer", "description": "Vertical angle -90 to 90"}
            }
        }
    },
    {
        "name": "buzz",
        "description": "Play buzzer pattern",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "enum": ["short", "long", "happy", "sad", "sos"]}
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "describe_scene",
        "description": "Describe what the robot sees",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_battery",
        "description": "Get battery percentage",
        "parameters": {"type": "object", "properties": {}}
    },
]


def _dispatch_tool(name: str, args: dict) -> str:
    handler = _TOOL_HANDLERS.get(name)
    if handler is None:
        return f'Unknown tool: {name}'
    try:
        return handler(**args)
    except Exception as e:
        print(f'[AIBrain] Tool error ({name}): {e}')
        return f'Error: {e}'


def _frame_to_b64_jpeg() -> str:
    with _frame_lock:
        frame = _current_frame
    if frame is None:
        return ''
    try:
        ret, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        if not ret:
            return ''
        return base64.b64encode(buf.tobytes()).decode('utf-8')
    except Exception as e:
        print(e)
        return ''


async def _run_session():
    if not _GENAI_AVAILABLE:
        print('[AIBrain] google-genai not available')
        return

    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        print('[AIBrain] GEMINI_API_KEY not set')
        return

    try:
        client = genai.Client(api_key=api_key)

        tools = [genai_types.Tool(function_declarations=_TOOL_DECLARATIONS)]

        config = genai_types.LiveConnectConfig(
            response_modalities=["TEXT"],
            system_instruction=SYSTEM_PROMPT,
            tools=tools,
        )

        async with client.aio.live.connect(model=MODEL, config=config) as session:
            print('[AIBrain] Connected to Gemini Live')
            last_frame_time = 0.0

            while not _stop_event.is_set():
                now = time.time()

                # Send camera frame every 2 seconds
                if now - last_frame_time >= 2.0:
                    b64 = _frame_to_b64_jpeg()
                    if b64:
                        try:
                            await session.send(
                                input=genai_types.LiveClientRealtimeInput(
                                    media_chunks=[genai_types.Blob(mime_type='image/jpeg', data=b64)]
                                )
                            )
                        except Exception as e:
                            print(f'[AIBrain] Frame send error: {e}')
                    last_frame_time = now

                # Receive any pending responses
                try:
                    async for response in session.receive():
                        if hasattr(response, 'server_content') and response.server_content:
                            sc = response.server_content
                            if hasattr(sc, 'model_turn') and sc.model_turn:
                                for part in sc.model_turn.parts:
                                    if hasattr(part, 'text') and part.text:
                                        print(f'[AIBrain] {part.text}')
                                    if hasattr(part, 'function_call') and part.function_call:
                                        fc = part.function_call
                                        result = _dispatch_tool(fc.name, dict(fc.args))
                                        print(f'[AIBrain] Tool {fc.name} -> {result}')
                                        await session.send(
                                            input=genai_types.LiveClientToolResponse(
                                                function_responses=[genai_types.FunctionResponse(
                                                    name=fc.name,
                                                    response={"result": result}
                                                )]
                                            )
                                        )
                except asyncio.TimeoutError:
                    pass
                except Exception as e:
                    print(f'[AIBrain] Receive error: {e}')

                await asyncio.sleep(0.1)

    except Exception as e:
        print(f'[AIBrain] Session error: {e}')


def _session_thread_fn():
    asyncio.run(_run_session())


def init():
    pass


def start():
    global _running, _session_thread
    _running = True
    _stop_event.clear()

    if not _GENAI_AVAILABLE:
        print('[AIBrain] google-genai not installed — AIBrain disabled')
        return

    if _session_thread is None or not _session_thread.is_alive():
        _session_thread = threading.Thread(target=_session_thread_fn, daemon=True)
        _session_thread.start()


def stop():
    global _running
    _running = False
    _stop_event.set()


def exit():
    _stop_event.set()
    AGC.runActionGroup('stand_slow')


def run(img):
    global _current_frame
    if img is None:
        return img
    with _frame_lock:
        _current_frame = img.copy()
    return img
