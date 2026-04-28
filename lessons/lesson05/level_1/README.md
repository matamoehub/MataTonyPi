# Lesson 5 - Color Recognition and Reactions

## Goal

Recognize multiple colors and map each color to different behaviors.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## How this lesson works

- students reuse the single-color detection pattern from Lesson 4
- each color should map to a different spoken line or motion
- the main learning goal is decision-making from vision results

## What students will use

- `myRobot.vision.find_color(...)`
- `if` / `elif` branching
- expressive reactions such as `say()`, `wave()`, `bow()`, or `celebrate()`

## Suggested practice flow

1. `for color in ["red", "green", "blue", "yellow"]:`
2. `detected = myRobot.vision.find_color("blue")`

## Required flow

1. choose at least three colors to support
2. test each color one at a time
3. map each color to a different robot response
4. make sure the robot does nothing or says "not found" when no target is present

## Debugging requirement

- print the tested color name before each scan
- print the returned result object
- test colors separately before putting them into a loop

## Success criteria

- students can explain which branch runs for each color
- the robot produces different reactions for different colors
- color detection logic is readable and repeatable

## Challenge ideas

- choose a target color randomly
- give each color a matching personality
- add a score counter for correct detections

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
