#!/usr/bin/env python3
"""Games library for MataTonyPi — Simon Says."""
from __future__ import annotations
__version__ = "1.0.0"
import random
import threading
import time
from typing import Any
from tonypi_support import run_action, get_board, get_controller, head_center

COLOURS = ["red", "green", "blue"]
TONE_MAP = {"red": 1200, "green": 1600, "blue": 900}

_difficulty = 2   # 1=4 rounds 5s, 2=8 rounds 5s, 3=8 rounds 3s
_game_thread: threading.Thread | None = None
_stop_event = threading.Event()
_detected_colour: str | None = None
_colour_lock = threading.Lock()

DIFFICULTY = {
    1: {"max_rounds": 4, "timeout": 5},
    2: {"max_rounds": 8, "timeout": 5},
    3: {"max_rounds": 8, "timeout": 3},
}


def set_difficulty(level: int):
    global _difficulty
    _difficulty = max(1, min(3, int(level)))


def update_detected_colour(colour: str | None):
    """Called by run(img) each frame to report the detected colour."""
    with _colour_lock:
        global _detected_colour
        _detected_colour = colour


def _buzz(freq, on_s, off_s=0.05, repeat=1):
    board = get_board()
    if board:
        try: board.set_buzzer(int(freq), float(on_s), float(off_s), int(repeat))
        except Exception as e: print(f"[games_lib] buzzer: {e}")


def _nod():
    ctl = get_controller()
    if ctl is None:
        return
    cv, ch = head_center()
    try:
        ctl.set_pwm_servo_pulse(1, cv + 200, 200); time.sleep(0.25)
        ctl.set_pwm_servo_pulse(1, cv - 120, 200); time.sleep(0.25)
        ctl.set_pwm_servo_pulse(1, cv, 200)
    except Exception as e:
        print(f"[games_lib] nod error: {e}")


def _play_sequence(sequence: list[str]):
    for colour in sequence:
        freq = TONE_MAP[colour]
        _buzz(freq, 0.3, 0.2, 1)
        time.sleep(0.55)


def _wait_for_colour(target: str, timeout: float) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline and not _stop_event.is_set():
        with _colour_lock:
            detected = _detected_colour
        if detected == target:
            return True
        time.sleep(0.1)
    return False


def _run_game():
    cfg = DIFFICULTY[_difficulty]
    max_rounds = cfg["max_rounds"]
    timeout = cfg["timeout"]
    sequence: list[str] = []
    score = 0

    _buzz(1500, 0.15, 0.1, 2)
    run_action("stand")
    time.sleep(1.0)

    for round_num in range(1, max_rounds + 1):
        if _stop_event.is_set():
            break
        sequence.append(random.choice(COLOURS))
        print(f"[games_lib] Round {round_num}: {sequence}")
        _play_sequence(sequence)
        time.sleep(0.5)

        success = True
        for step, target in enumerate(sequence):
            if _stop_event.is_set():
                success = False; break
            print(f"[games_lib] Waiting for: {target}")
            got_it = _wait_for_colour(target, timeout)
            if got_it:
                _buzz(1800, 0.1, 0.05, 1)
                _nod()
                time.sleep(0.3)
                score += 1
            else:
                _buzz(600, 0.3, 0.1, 2)
                run_action("stand")
                print(f"[games_lib] Game over! Score: {score}")
                success = False; break

        if not success:
            return

    # Won!
    print(f"[games_lib] Complete! Score: {score}")
    _buzz(1800, 0.1, 0.1, 3)
    run_action("wave")


def start_game() -> dict[str, Any]:
    global _game_thread
    if _game_thread and _game_thread.is_alive():
        return {"ok": False, "note": "Game already running"}
    _stop_event.clear()
    _game_thread = threading.Thread(target=_run_game, daemon=True, name="SimonSays")
    _game_thread.start()
    return {"ok": True, "difficulty": _difficulty}


def stop_game():
    _stop_event.set()
    return {"ok": True}


def is_running() -> bool:
    return _game_thread is not None and _game_thread.is_alive()
