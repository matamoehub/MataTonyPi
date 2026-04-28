# Lesson 3 - Action Groups and Performances

## Goal

Use prebuilt action groups and speech to choreograph short performances.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## Suggested Practice Flow

1. `print(myRobot.anim.list_action_groups()[:12])`
2. `myRobot.anim.wave(); myRobot.say("Welcome to our show!")`
3. `myRobot.anim.dance(); myRobot.anim.celebrate()`
4. `myRobot.anim.run("bow")`

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
