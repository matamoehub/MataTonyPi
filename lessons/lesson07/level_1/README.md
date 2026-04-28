# Lesson 7 - Object Tracking

## Goal

Continuously track a color target and turn body/head toward it.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## How this lesson works

- students repeat detection inside a loop
- the robot should make small corrections instead of one big move
- tracking should stop cleanly if the target disappears

## What students will use

- `for` or `while` loops
- `myRobot.vision.find_color(...)`
- `myRobot.head.*` or `myRobot.motion.turn_*`
- pauses between updates

## Suggested practice flow

1. `for _ in range(5):`
2. `found = myRobot.vision.find_color("yellow")`

## Required flow

1. scan for a target color repeatedly
2. use target position to decide which direction to move or look
3. make small corrections
4. stop tracking if the target is lost

## Debugging requirement

- print each loop step
- print whether the target was found each time
- start with head tracking before adding body movement

## Success criteria

- TonyPi visibly adjusts toward the target
- tracking loop does not run forever without control
- students can explain why small corrections are safer than large ones

## Challenge ideas

- add a timeout when the target is lost
- switch from head-only tracking to body turning
- track one color first, then a second color

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
