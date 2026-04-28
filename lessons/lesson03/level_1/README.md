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

## Action Groups To Teach First

TonyPi supports two useful action-group styles:

1. named action groups from the upstream Hiwonder materials
2. raw numbered action-group files on the robot

### Named Hiwonder action groups

These are the most important documented upstream names:

- `stand`
- `go_forward`
- `back`
- `back_fast`
- `left_move_fast`
- `right_move_fast`
- `turn_left`
- `turn_right`
- `wave`
- `bow`
- `squat`
- `chest`
- `twist`
- `stepping`
- `weightlifting`

Examples:

```python
myRobot.anim.run("stand")
myRobot.anim.run("go_forward")
myRobot.anim.run("turn_left")
myRobot.anim.run("wave")
myRobot.anim.run("bow")
myRobot.anim.run("twist")
```

### Dance action groups

On this TonyPi classroom setup, the numbered files `16` through `24` are dance
moves.

Examples:

```python
myRobot.anim.run("16")
myRobot.anim.run("17")
myRobot.anim.run("18")
myRobot.anim.run("24")
```

You can also use:

```python
myRobot.anim.run_id(16)
myRobot.anim.run_id(17)
```

But for the numbered dance files, `run("17")` is the safest form because it
directly targets the raw action-group filename.

## Recommended Lesson 3 Teaching Order

1. Start with `myRobot.anim.show_action_groups()`
2. Test one named move like `myRobot.anim.run("wave")`
3. Test one named motion like `myRobot.anim.run("turn_left")`
4. Test one numbered dance move like `myRobot.anim.run("17")`
5. Combine action groups with speech for a short performance

## Reference

See:

- `docs/ACTION_GROUPS.md`

That document explains the difference between named action groups and numbered
dance files in more detail.
