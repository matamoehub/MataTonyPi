#!/usr/bin/python3
# coding=utf8

import os
import cv2
import json
import base64
import threading
import time
import urllib.request
import hiwonder.ros_robot_controller_sdk as rrc
import hiwonder.ActionGroupControl as AGC
from hiwonder.Controller import Controller

board = rrc.Board()
ctl = Controller(board)

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-opus-4-5"
MAX_TOK = 300
SYS_PROMPT = ("You are the vision system of a small humanoid robot called TonyPi. "
              "Describe what you see in front of you in 1-2 short sentences, "
              "as if speaking aloud. Be conversational and mention the most interesting thing first.")

_current_frame = None
_thinking = False
_running = False
_frame_lock = threading.Lock()


def init():
    pass


def start():
    global _running
    _running = True


def stop():
    global _running
    _running = False


def exit():
    AGC.runActionGroup('stand_slow')


def _speak(text):
    """Try espeak-ng or piper TTS."""
    safe = text.replace('"', "'").replace('`', "'").replace('$', '')
    try:
        ret = os.system(f'which piper > /dev/null 2>&1')
        if ret == 0:
            os.system(f'echo "{safe}" | piper --output_raw | aplay -r 22050 -f S16_LE -t raw -')
        else:
            os.system(f'espeak-ng "{safe}"')
    except Exception as e:
        print(e)


def _trigger_describe():
    global _thinking

    _thinking = True

    with _frame_lock:
        frame = _current_frame.copy() if _current_frame is not None else None

    if frame is None:
        _thinking = False
        return

    text = "I can't see clearly right now"
    try:
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            print('[SceneDescribe] ANTHROPIC_API_KEY not set')
            text = "I can't see clearly right now"
        else:
            ret, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                raise ValueError('Failed to encode frame')
            b64_str = base64.b64encode(buf.tobytes()).decode('utf-8')

            payload = {
                "model": MODEL,
                "max_tokens": MAX_TOK,
                "system": SYS_PROMPT,
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": b64_str
                            }
                        },
                        {"type": "text", "text": "What do you see?"}
                    ]
                }]
            }

            req = urllib.request.Request(
                API_URL,
                data=json.dumps(payload).encode(),
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                text = data["content"][0]["text"]

    except Exception as e:
        print(f'[SceneDescribe] Error: {e}')
        text = "I can't see clearly right now"

    print(f'[SceneDescribe] {text}')
    _speak(text)
    _thinking = False


def trigger():
    """Non-blocking call to trigger a scene description."""
    if _thinking:
        return
    t = threading.Thread(target=_trigger_describe, daemon=True)
    t.start()


def run(img):
    global _current_frame

    if img is None:
        return img

    with _frame_lock:
        _current_frame = img.copy()

    if _thinking:
        cv2.putText(img, 'Thinking...', (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 200, 255), 2)

    return img
