#!/usr/bin/env python3
"""TonyPi action-group helpers."""

from __future__ import annotations

from tonypi_support import action_name_for_id, list_action_groups, resolve_action_name, run_action, stop_actions


def list_actions() -> list[str]:
    return list_action_groups()


def run(name: str, times: int = 1):
    return run_action(name, times=times)


def run_id(action_id: str | int, times: int = 1):
    name = action_name_for_id(action_id)
    if name is None:
        raise RuntimeError(f"Unknown TonyPi action id: {action_id}")
    return run_action(name, times=times)


def run_best(candidates, times: int = 1):
    name = resolve_action_name(candidates)
    if name is None:
        raise RuntimeError(f"No TonyPi action found for candidates: {candidates}")
    return run_action(name, times=times)


def stop():
    stop_actions()

