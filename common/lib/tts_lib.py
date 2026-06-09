#!/usr/bin/env python3
"""TonyPi speech helper."""

from __future__ import annotations

import os

from tonypi_support import available_voices, resolve_voice_name, say, PIPER_VOICE_ENV

__version__ = "1.4.1"


def select_voice(voice: str | None = None, number: int | None = None) -> str:
    """Select the active voice for all future say() calls.

    Args:
        voice:  Voice name e.g. "ryan", "amy", "alan"
        number: Voice number (1-based index of installed voices)

    Returns the resolved voice name and sets it as the default.
    """
    if number is not None:
        resolved = resolve_voice_name(str(number))
    else:
        resolved = resolve_voice_name(voice)
    # Persist so all future say() calls use this voice
    os.environ[PIPER_VOICE_ENV] = resolved
    print(f"[voice] active voice set to: {resolved}")
    return resolved


def select_voice_number(number: int) -> str:
    return select_voice(number=number)


def current_voice() -> str:
    """Return the currently active voice name."""
    return os.environ.get(PIPER_VOICE_ENV, "amy")


__all__ = ["say", "available_voices", "select_voice", "select_voice_number",
           "resolve_voice_name", "current_voice", "__version__"]
