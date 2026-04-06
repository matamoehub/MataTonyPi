#!/usr/bin/env python3
"""TonyPi speech helper."""

from __future__ import annotations

from tonypi_support import available_voices, resolve_voice_name, say


def select_voice(voice: str | None = None, number: int | None = None) -> str:
    if number is not None:
        return resolve_voice_name(str(number))
    return resolve_voice_name(voice)


def select_voice_number(number: int) -> str:
    return select_voice(number=number)


__all__ = ["say", "available_voices", "select_voice", "select_voice_number", "resolve_voice_name"]
