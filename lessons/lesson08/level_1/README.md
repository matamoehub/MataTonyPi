# Lesson 8 - Auto Shooting

## Goal

Combine vision and movement to approach a ball target and trigger a kick-style action.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## Suggested Practice Flow

1. `ball = myRobot.vision.find_color("red")`
2. `if ball.found:`

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
