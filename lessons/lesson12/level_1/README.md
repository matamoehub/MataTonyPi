# Lesson 12 - Pickup and Intelligent Transport

## Goal

Combine detection, approach, pickup, carry, and place-down in one transport flow.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## How this lesson works

- students build a longer behavior chain than in earlier lessons
- the robot should detect, approach, pick up, carry, and place in order
- clear sequencing matters more than full autonomy

## What students will use

- `myRobot.pickup.*`
- `myRobot.vision.find_tag(...)` or other destination logic
- speech or print statements for progress updates
- pauses between stages

## Suggested practice flow

1. `myRobot.pickup.approach_object("block")`
2. `myRobot.pickup.pick_up("block")`
3. `destination = myRobot.vision.find_tag(2)`

## Required flow

1. approach the object
2. perform the pickup
3. carry the object
4. decide where to place it
5. place it down and release

## Debugging requirement

- print each stage name before running it
- test pickup actions one at a time before combining them
- leave enough space and keep objects simple and consistent

## Success criteria

- students can explain the order of the transport pipeline
- TonyPi reaches the release step without skipping earlier steps
- the notebook remains readable even though the behavior is longer

## Challenge ideas

- announce each transport stage with speech
- use tag ids to choose between two drop-off points
- add a recovery branch when the first detection fails

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
