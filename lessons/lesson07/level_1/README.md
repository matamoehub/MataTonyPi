# Lesson 7 - Object Tracking

## Goal

Continuously track a color target and turn body/head toward it.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## Suggested Practice Flow

1. `for _ in range(5):`
2. `found = myRobot.vision.find_color("yellow")`

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
