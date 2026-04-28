# Lesson 6 - Target Position Recognition

## Goal

Use color detection coordinates to decide if a target is left, center, or right.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## Suggested Practice Flow

1. `target = myRobot.vision.find_color("green")`
2. `if target.found:`

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
