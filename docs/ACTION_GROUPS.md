# TonyPi Action Groups

TonyPi ships with many prebuilt action groups in the vendor `ActionGroups`
folder. The MataTonyPi teaching layer now exposes those directly through
`student_robot_v2`.

## Upstream references

These notes are based on the upstream TonyPi materials:

- Hiwonder TonyPi `ActionGroupDict.py`
- Hiwonder TonyPi action-programming docs
- Hiwonder TonyPi group-control docs

## How Students Can Use Them

```python
from student_robot_v2 import bot

myRobot = bot()

print(myRobot.anim.list_action_groups())
myRobot.anim.show_action_groups()
print(myRobot.anim.catalog())
print(myRobot.anim.dance_moves())

myRobot.anim.run("wave")
myRobot.anim.run("17")
myRobot.anim.run_id(16)
```

## Public Action Group Helpers

- `myRobot.anim.list_action_groups()`
- `myRobot.anim.show_action_groups()`
- `myRobot.anim.catalog()`
- `myRobot.anim.dance_moves()`
- `myRobot.anim.run(name, times=1)`
- `myRobot.anim.run_id(action_id, times=1)`

## Catalog Format

Each catalog item includes:

- `name`: the TonyPi action-group file name
- `id`: the first matching upstream action id, when one exists
- `ids`: all matching upstream ids for that action name
- `category`: a teaching-friendly category such as `dance`, `motion`, `greeting`, `pickup`, or `pose`

## Dance Range

On this TonyPi setup, the raw numbered action-group files `16` through `24`
are treated as dance moves.

Use either of these forms:

```python
myRobot.anim.run("16")
myRobot.anim.run("17")
myRobot.anim.run("24")
```

or:

```python
myRobot.anim.run_id(16)
myRobot.anim.run_id(17)
myRobot.anim.run_id(24)
```

Important:

- `myRobot.anim.run("17")` means "run the action-group file literally named `17`"
- `myRobot.anim.run_id(17)` now prefers the raw `17` action-group file first
- for numbered dance files, `run("17")` is the least ambiguous form

## Named Hiwonder Action Groups

The upstream TonyPi sources and docs explicitly reference a core set of named
action groups. These are the most important documented names to include in
teaching material.

Common named moves:

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

These names are useful because they match the upstream Hiwonder teaching
materials and the vendor action-group conventions.

## Two Action-Group Styles

TonyPi action groups fall into two practical teaching categories:

1. Named action groups, such as `wave`, `bow`, `go_forward`, and `turn_left`
2. Raw numbered action-group files, such as `16`, `17`, `18`, ... `24`

Recommended teaching rule:

- use `myRobot.anim.run("wave")` for named moves
- use `myRobot.anim.run("17")` for numbered dance moves
- use `myRobot.anim.run_id(...)` only when you specifically want numeric-id access

Example:

```python
for item in myRobot.anim.dance_moves():
    print(item)
```

## Notes

- The exact installed action groups depend on the robot image and vendor TonyPi install.
- Some actions are wrapped with named student helpers already, like `wave()`, `bow()`, and walking/turning helpers.
- Everything else is still reachable through `run(...)` and `run_id(...)`.
- Upstream TonyPi documentation for action programming and group-control examples references named moves such as `stand`, `go_forward`, and `bow`, while many classroom robot images also include extra numbered action-group files.
