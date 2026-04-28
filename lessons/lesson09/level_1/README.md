# Lesson 9 - Line Follow

## Goal

Tune camera target detection for patrol lines and maintain alignment.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## Suggested Practice Flow

1. `line = myRobot.vision.find_color("blue")`
2. `if line.found:`

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
