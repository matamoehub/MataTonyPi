# Lesson 4 - Single Color Detection

## Goal

Capture camera frames and detect a single target color with a robot reaction.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## How this lesson works

- students test one color only at first
- the robot should look at a simple target with minimal background clutter
- the result object is more important than speed

## What students will use

- `myRobot.vision.snapshot()`
- `myRobot.vision.find_color(...)`
- `DetectionResult` fields such as `found`, `x`, `y`, and `area`
- one simple reaction move such as `wave()` or `say(...)`

## Suggested practice flow

1. `myRobot.vision.snapshot()`
2. `result = myRobot.vision.find_color("red")`
3. `if result.found:`

## Required flow

1. capture a camera image
2. search for one chosen color
3. print whether the color was found
4. make TonyPi react only if the target is found

## Debugging requirement

- print the full detection result
- keep the head centered before testing color detection
- test with one large colored object before trying smaller targets

## Success criteria

- students can explain what `found` means
- the robot reacts differently when the color is present versus absent
- students can read basic position data from the result

## Challenge ideas

- compare red and blue detection
- tune the classroom setup for more reliable detection
- make TonyPi speak the detected color

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
