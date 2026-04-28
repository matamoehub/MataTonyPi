# Lesson 10 - Tag Detection and Tag Actions

## Goal

Detect AprilTags and trigger different actions per tag id.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## Suggested Practice Flow

1. `for tag_id in [1, 2, 3]:`
2. `tag = myRobot.vision.find_tag(1)`

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
