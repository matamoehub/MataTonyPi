# Lesson 2 - Talking, Head Movement, and Gestures

## Goal

Use speech, head movement, and simple gestures to make TonyPi expressive and responsive.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## Suggested Practice Flow

1. `myRobot.say("Hello, I am TonyPi!")`
2. `myRobot.head.look_left(); myRobot.head.look_right(); myRobot.head.center()`
3. `myRobot.head.nod(); myRobot.head.shake()`
4. `myRobot.arms.hands_up(); myRobot.anim.greet()`

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
