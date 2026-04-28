# Lesson 12 - Pickup and Intelligent Transport

## Goal

Combine detection, approach, pickup, carry, and place-down in one transport flow.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## Suggested Practice Flow

1. `myRobot.pickup.approach_object("block")`
2. `myRobot.pickup.pick_up("block")`
3. `destination = myRobot.vision.find_tag(2)`

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
