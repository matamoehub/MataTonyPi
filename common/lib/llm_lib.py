#!/usr/bin/env python3
"""Shared Claude API helper for MataTonyPi libraries.

Both `student_robot_v2.py` (vision.describe()) and `patrol_lib.py`
(patrol summary) make a small one-shot call to the Claude Messages API.
This module centralises the model id so it only needs to change in one
place, plus a tiny helper that wraps the HTTP call the two callers were
each doing independently.
"""
from __future__ import annotations

__version__ = "1.0.0"

import json
import os
import urllib.request
from typing import Any

# Single source of truth for the model id used by every LLM-backed
# student_robot_v2 / patrol_lib feature. Change it here, not at each
# call site.
MODEL = "claude-opus-4-5"

API_URL = "https://api.anthropic.com/v1/messages"


def call_claude(payload: dict[str, Any], api_key: str | None = None, timeout: float = 15.0) -> str:
    """POST a Messages API payload to Claude and return the first text block.

    `payload` should contain at least `messages` (and optionally `system`,
    `max_tokens`, etc.) — `model` is filled in from MODEL if not already
    present. Raises on any failure (missing key, network error, bad
    response shape) — callers are expected to catch and log, same as
    before this helper existed.
    """
    key = api_key if api_key is not None else os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    body = dict(payload)
    body.setdefault("model", MODEL)

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode(),
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
    return data["content"][0]["text"]
