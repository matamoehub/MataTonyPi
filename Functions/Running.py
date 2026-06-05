#!/usr/bin/python3
# coding=utf8

import time

# --- Import all function modules (vendor files may not be present in dev) ---
try:
    from Functions import RemoteControl
except Exception:
    RemoteControl = None

try:
    from Functions import ColorDetect
except Exception:
    ColorDetect = None

try:
    from Functions import FaceDetect
except Exception:
    FaceDetect = None

try:
    from Functions import VisualPatrol
except Exception:
    VisualPatrol = None

try:
    from Functions import AutoBalance
except Exception:
    AutoBalance = None

try:
    from Functions import KickBall
except Exception:
    KickBall = None

try:
    from Functions import BodyController
except Exception:
    BodyController = None

try:
    from Functions import FaceTrack
except Exception:
    FaceTrack = None

try:
    from Functions import GestureControl
except Exception:
    GestureControl = None

try:
    from Functions import SpeedDetect
except Exception:
    SpeedDetect = None

try:
    from Functions import ObstacleAvoid
except Exception:
    ObstacleAvoid = None

try:
    from Functions import ArmControl
except Exception:
    ArmControl = None

# New modules (Tasks 1-9)
try:
    from Functions import EmotionExpress
except Exception:
    EmotionExpress = None

try:
    from Functions import BatteryGuard
except Exception:
    BatteryGuard = None

try:
    from Functions import SceneDescribe
except Exception:
    SceneDescribe = None

try:
    from Functions import Follow
except Exception:
    Follow = None

try:
    from Functions import SimonSays
except Exception:
    SimonSays = None

try:
    from Functions import TagNav
except Exception:
    TagNav = None

try:
    from Functions import PatrolLog
except Exception:
    PatrolLog = None

# Start battery monitoring at module level
if BatteryGuard is not None:
    try:
        BatteryGuard.start_monitoring()
    except Exception as e:
        print(f'[Running] BatteryGuard start_monitoring error: {e}')

# Function ID → module mapping
FUNCTIONS = {
    1:  RemoteControl,
    2:  ColorDetect,
    3:  FaceDetect,
    4:  VisualPatrol,
    5:  AutoBalance,
    6:  KickBall,
    7:  BodyController,
    8:  FaceTrack,
    9:  GestureControl,
    10: SpeedDetect,
    11: ObstacleAvoid,
    12: ArmControl,
    13: EmotionExpress,
    14: SceneDescribe,
    15: Follow,
    16: SimonSays,
    17: TagNav,
    18: PatrolLog,
}

_current_func_id = None
_current_module = None


def loadFunc(func_id: int):
    """
    Load and start a function by ID.
    Returns (True, 'ok') on success or (False, reason) on failure.
    """
    global _current_func_id, _current_module

    # Battery check
    if BatteryGuard is not None:
        try:
            if BatteryGuard.is_critical():
                return False, 'Battery critical — charge before continuing'
        except Exception as e:
            print(f'[Running] BatteryGuard check error: {e}')

    if func_id < 1 or func_id > 18:
        return False, f'Invalid function ID: {func_id} (valid: 1-18)'

    module = FUNCTIONS.get(func_id)
    if module is None:
        return False, f'Function {func_id} module not available'

    # Stop and unload current function
    unloadFunc()

    # Init and start new function
    try:
        if hasattr(module, 'init'):
            module.init()
        if hasattr(module, 'start'):
            module.start()
    except Exception as e:
        print(f'[Running] Error starting function {func_id}: {e}')
        return False, str(e)

    _current_func_id = func_id
    _current_module = module
    print(f'[Running] Loaded function {func_id}: {module.__name__ if hasattr(module, "__name__") else func_id}')
    return True, 'ok'


def unloadFunc():
    """Stop and unload the currently running function."""
    global _current_func_id, _current_module

    if _current_module is None:
        return

    try:
        if hasattr(_current_module, 'stop'):
            _current_module.stop()
        if hasattr(_current_module, 'exit'):
            _current_module.exit()
    except Exception as e:
        print(f'[Running] Error stopping function {_current_func_id}: {e}')

    _current_func_id = None
    _current_module = None


def getCurrentFunc():
    """Return the currently loaded function ID, or None."""
    return _current_func_id


def runFrame(img):
    """Pass a camera frame to the currently loaded function's run()."""
    if _current_module is None:
        return img
    try:
        if hasattr(_current_module, 'run'):
            return _current_module.run(img)
    except Exception as e:
        print(f'[Running] run() error in function {_current_func_id}: {e}')
    return img


def init():
    pass


def start():
    pass


def stop():
    unloadFunc()


def exit():
    unloadFunc()


def run(img):
    return runFrame(img)
