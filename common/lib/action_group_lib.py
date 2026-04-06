#!/usr/bin/env python3
"""TonyPi action-group helpers."""

from __future__ import annotations

from tonypi_support import action_group_catalog, action_name_for_id, dance_action_groups, list_action_groups, resolve_action_name, run_action, sleep, stop_actions


ARM_SETTLE_S = 0.18


def _maybe_settle(name: str) -> None:
    token = str(name).lower()
    if any(part in token for part in ("wave", "bow", "hand", "arm", "grab", "carry", "release", "pickup", "greet")):
        sleep(ARM_SETTLE_S)


def list_actions() -> list[str]:
    return list_action_groups()


def catalog() -> list[dict[str, object]]:
    return action_group_catalog()


def dances() -> list[dict[str, object]]:
    return dance_action_groups()


def run(name: str, times: int = 1):
    result = run_action(name, times=times)
    _maybe_settle(name)
    return result


def run_id(action_id: str | int, times: int = 1):
    name = action_name_for_id(action_id)
    if name is None:
        raise RuntimeError(f"Unknown TonyPi action id: {action_id}")
    result = run_action(name, times=times)
    _maybe_settle(name)
    return result


def run_best(candidates, times: int = 1):
    name = resolve_action_name(candidates)
    if name is None:
        raise RuntimeError(f"No TonyPi action found for candidates: {candidates}")
    result = run_action(name, times=times)
    _maybe_settle(name)
    return result


def stop():
    stop_actions()
