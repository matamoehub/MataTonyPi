# Lesson 5 - Color Recognition and Reactions

## Goal

Recognize multiple colors and map each color to different behaviors.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## Suggested Practice Flow

1. `for color in ["red", "green", "blue", "yellow"]:`
2. `detected = myRobot.vision.find_color("blue")`

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
