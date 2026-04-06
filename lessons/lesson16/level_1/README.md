# Lesson 16 - Two-Robot Performance Cues

## Goal

Use named cues so one TonyPi can trigger another during a shared speaking and
movement routine.

## What students will use

- `myRobot.team.start_server()`
- `myRobot.team.signal(host, cue, payload=None)`
- `myRobot.team.wait_for(cue, timeout=None)`
- `myRobot.team.server_status()`
- `myRobot.team.local_ip()`

## Teaching Note

This lesson works best with two notebooks open at once, one on each robot. The
partner robot starts the cue server. The leader robot sends named cues to the
partner robot, and the partner responds with speech or movement when they
arrive.
