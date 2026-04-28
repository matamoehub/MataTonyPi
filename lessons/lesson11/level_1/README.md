# Lesson 11 - Face Detect and Greeting

## Goal

Detect faces and respond with greetings, gestures, and tracking behavior.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## Suggested Practice Flow

1. `face = myRobot.vision.find_face()`
2. `if face.found:`

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
