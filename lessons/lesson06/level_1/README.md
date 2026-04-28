# Lesson 6 - Target Position Recognition

## Goal

Use color detection coordinates to decide if a target is left, center, or right.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## How this lesson works

- students use the `x` position from a color-detection result
- the image is divided into simple regions: left, center, and right
- the robot should react differently based on where the target appears

## What students will use

- `myRobot.vision.find_color(...)`
- `result.x`
- left/center/right threshold values
- one simple reaction per region

## Suggested practice flow

1. `target = myRobot.vision.find_color("green")`
2. `if target.found:`

## Required flow

1. detect a colored target
2. print the target coordinates
3. classify the target as left, center, or right
4. make TonyPi announce or gesture based on the region

## Debugging requirement

- print the `x` value every time a target is found
- test with the object clearly on the left, middle, and right
- keep threshold numbers visible in the notebook so they can be tuned

## Success criteria

- students can explain how the thresholds work
- the robot gives different responses in different regions
- center is not confused with left or right most of the time

## Challenge ideas

- add a far-left and far-right category
- change the head direction based on the region
- use the result to decide which way to turn next

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
