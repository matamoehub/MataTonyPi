# Lesson 11 - Face Detect and Greeting

## Goal

Detect faces and respond with greetings, gestures, and tracking behavior.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## How this lesson works

- students scan for a person in front of the robot
- if a face is found, TonyPi should greet and react
- face detection should be tested before adding extra motion

## What students will use

- `myRobot.vision.find_face()`
- `myRobot.say(...)`
- `myRobot.anim.greet()` or `myRobot.anim.wave()`
- optional `myRobot.vision.track_face()`

## Suggested practice flow

1. `face = myRobot.vision.find_face()`
2. `if face.found:`

## Required flow

1. detect a face
2. print or speak whether a face was found
3. greet the detected person
4. optionally track the face after greeting

## Debugging requirement

- keep the head centered or slightly raised before face tests
- print the full face result object
- test in good lighting first

## Success criteria

- TonyPi greets when a face is visible
- no-face cases are handled cleanly
- students can explain what the face detection result contains

## Challenge ideas

- use different greetings for first detection versus repeat detection
- add a celebration if more than one face is found later
- make TonyPi look curious before greeting

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
