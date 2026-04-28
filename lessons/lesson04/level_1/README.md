# Lesson 4 - Single Color Detection

## Goal

Capture camera frames and detect a single target color with a robot reaction.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## Suggested Practice Flow

1. `myRobot.vision.snapshot()`
2. `result = myRobot.vision.find_color("red")`
3. `if result.found:`

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
