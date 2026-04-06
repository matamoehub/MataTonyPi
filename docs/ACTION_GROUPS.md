# TonyPi Action Groups

TonyPi ships with many prebuilt action groups in the vendor `ActionGroups`
folder. The MataTonyPi teaching layer now exposes those directly through
`student_robot_v2`.

## How Students Can Use Them

```python
from student_robot_v2 import bot

myRobot = bot()

print(myRobot.anim.list_action_groups())
myRobot.anim.show_action_groups()
print(myRobot.anim.catalog())
print(myRobot.anim.dance_moves())

myRobot.anim.run("wave")
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

On this TonyPi setup, action ids `16` through `24` are treated as dance moves.

Example:

```python
for item in myRobot.anim.dance_moves():
    print(item)
```

## Notes

- The exact installed action groups depend on the robot image and vendor TonyPi install.
- Some actions are wrapped with named student helpers already, like `wave()`, `bow()`, and walking/turning helpers.
- Everything else is still reachable through `run(...)` and `run_id(...)`.
