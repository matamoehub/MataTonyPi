# MataTonyPi V2 API

`MataTonyPi` exposes one public student-facing library:

```python
from student_robot_v2 import bot
```

The returned robot object should feel playful, readable, and consistent across
all lessons.

## Core Usage

```python
from student_robot_v2 import bot

myRobot = bot()
myRobot.say("Hello")
myRobot.anim.wave()
myRobot.head.look_left()
myRobot.motion.walk_forward(steps=1)
result = myRobot.vision.find_object("red")
if result.found:
    myRobot.pickup.pick_up("red")
```

## Top-Level Methods

- `bot(verbose=True)`
- `myRobot.say(text, block=True)`
- `myRobot.stop()`
- `myRobot.status()`
- `myRobot.home()`
- `myRobot.stand()`
- `myRobot.sit()`

## Namespaces

### `myRobot.anim`

- `list_action_groups()`
- `show_action_groups()`
- `run(name, times=1)`
- `run_id(action_id, times=1)`
- `catalog()`
- `dance_moves()`
- `wave()`
- `greet()`
- `dance()`
- `celebrate()`
- `think()`
- `sad()`
- `yes()`
- `no()`
- `scan()`

### `myRobot.head`

- `look_left()`
- `look_right()`
- `look_up()`
- `look_down()`
- `center()`
- `nod()`
- `shake()`
- `scan()`

### `myRobot.arms`

- `left_up()`
- `right_up()`
- `hands_up()`
- `open()`
- `close()`
- `center()`
- `grab_pose()`
- `carry_pose()`
- `release_pose()`

### `myRobot.pose`

- `ready()`
- `neutral()`
- `bow()`
- `stand()`
- `sit()`
- `carry()`

### `myRobot.motion`

- `walk_forward(steps=1)`
- `walk_backward(steps=1)`
- `turn_left(steps=1)`
- `turn_right(steps=1)`
- `step_left(steps=1)`
- `step_right(steps=1)`
- `approach()`
- `stop()`

### `myRobot.vision`

- `find_color(name)`
- `find_object(name)`
- `find_face()`
- `recognize_hands(show=True)`
- `find_tag(tag_id)`
- `track_color(name)`
- `track_face()`
- `snapshot()`
- `scan_for(name)`

Vision calls should return a simple result object with fields like:

- `found`
- `label`
- `x`
- `y`
- `area`
- `confidence`

### `myRobot.pickup`

- `approach_object(name)`
- `pick_up(name)`
- `grab()`
- `carry()`
- `place_down()`
- `release()`
- `transport(name)`

### `myRobot.voice`

- `say(text, block=True)`
- `greet()`
- `celebrate()`
- `think()`

### `myRobot.controller`

- `buttons()`
- `show_buttons()`
- `dance_buttons()`
- `show_dance_buttons()`
- `modes()`
- `summary()`

## Public API Rules

- Students import only `student_robot_v2`.
- Method names stay short and descriptive.
- Behind the scenes we can split implementation into helper modules later, but
  those remain private.
- Expressive actions should be available before advanced autonomous tasks.
- All installed TonyPi action groups should remain reachable through `myRobot.anim.run(...)` or `myRobot.anim.run_id(...)` even if they are not wrapped by a named helper yet.
