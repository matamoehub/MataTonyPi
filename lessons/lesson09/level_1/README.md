# Lesson 9 - Line Follow

## Goal

Tune camera target detection for patrol lines and maintain alignment.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## How this lesson works

- students treat the line like a vision target that must stay centered
- the robot should make repeated small corrections
- tuning matters more than flashy movement

## What students will use

- `myRobot.vision.find_color(...)`
- position-based steering logic
- repeated movement corrections
- clear debug output

## Suggested practice flow

1. `line = myRobot.vision.find_color("blue")`
2. `if line.found:`

## Required flow

1. detect the line color
2. decide whether the line is left, center, or right
3. correct the robot position
4. repeat the process while keeping the line in view

## Debugging requirement

- print detection coordinates on every step
- test with a short straight line first
- reduce movement size if the robot over-corrects

## Success criteria

- TonyPi can stay aligned with the line for several corrections
- students can explain which values drive left/right adjustment
- the robot does not lose the line immediately after one correction

## Challenge ideas

- tune for faster correction
- handle gaps or weak detections more gracefully
- compare head movement versus body movement strategies

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
