# Lesson 8 - Auto Shooting

## Goal

Combine vision and movement to approach a ball target and trigger a kick-style action.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## How this lesson works

- students combine detection and movement into one short behavior chain
- the robot should align first, then move forward, then kick
- this lesson is about sequencing, not full field play

## What students will use

- `myRobot.vision.find_color(...)`
- `myRobot.motion.*`
- an action-group or animation for the final kick-style move
- printed state updates

## Suggested practice flow

1. `ball = myRobot.vision.find_color("red")`
2. `if ball.found:`

## Required flow

1. detect the ball target
2. decide whether TonyPi needs to turn or sidestep first
3. move forward only when alignment is good enough
4. trigger the final kick-style action

## Debugging requirement

- print the ball position before every movement decision
- test approach steps separately from the kick action
- keep enough floor space around the robot

## Success criteria

- TonyPi approaches the ball in a controlled way
- students can explain the order: detect, align, move, kick
- the final action is triggered only after approach logic runs

## Challenge ideas

- add spoken feedback like "left", "right", or "kick"
- tune separate thresholds for far, mid, and close
- try a slower but more reliable alignment strategy

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
