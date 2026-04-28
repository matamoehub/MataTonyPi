# Lesson 2 - Talking, Head Movement, and Gestures

## Goal

Use speech, head movement, and simple gestures to make TonyPi expressive and responsive.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## How this lesson works

- students stay close to the robot and test short expressive commands
- the focus is personality, not navigation
- every action should be followed by a short pause so the robot can finish the move

## What students will use

- `myRobot.say(...)`
- `myRobot.head.*`
- `myRobot.arms.*`
- `myRobot.anim.greet()`

## Suggested practice flow

1. `myRobot.say("Hello, I am TonyPi!")`
2. `myRobot.head.look_left(); myRobot.head.look_right(); myRobot.head.center()`
3. `myRobot.head.nod(); myRobot.head.shake()`
4. `myRobot.arms.hands_up(); myRobot.anim.greet()`

## Required flow

1. make TonyPi introduce itself with speech
2. make TonyPi look in different directions
3. compare yes-style and no-style head gestures
4. finish with one arm gesture and one greeting animation

## Debugging requirement

- use `print()` so students can see which command they just ran
- if a motion looks wrong, rerun that single command on its own
- reset with `myRobot.head.center()` before trying the next head test

## Success criteria

- TonyPi can say a short line
- head movement commands are visibly different
- students can combine one voice line and one gesture into a short reaction

## Challenge ideas

- create a shy version and a confident version of the same greeting
- add pauses to improve timing
- make TonyPi answer a yes/no question with gestures only

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
