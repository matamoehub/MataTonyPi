# MataTonyPi

Student-friendly TonyPi lessons and libraries for Matamoe robots.

`MataTonyPi` is designed to sit beside the vendor TonyPi install, not replace it.
The Hiwonder `TonyPi` directory stays untouched. This repo provides the
Matamoe teaching layer, lesson content, and the single public V2 API used by
students in Jupyter.

## Design Rules

- Keep vendor TonyPi code unchanged.
- Expose one student-facing library only: `student_robot_v2.py`.
- Make the experience expressive from the start: talking, head motion, arm
  gestures, action-group animation, object detection, and pickup tasks.
- Match the `MataTurboPi` lesson flow so `robot-console`, `robot-classroom`,
  and `robot_ops_web` can treat it the same way.

## Expected Robot Layout

```text
/opt/robot/
  TonyPi/          # vendor install, leave alone
  MataTonyPi/      # this repo
  common/lib/      # optional runtime copy/symlink of shared lesson libs
```

## Repository Layout

```text
common/
  lib/
    bootstrap.py
    student_robot_v2.py

docs/
  API.md
  ROADMAP.md

lessons/
  lesson01/
  lib/
```

## Student API

Students should only need:

```python
from student_robot_v2 import bot

myRobot = bot()
myRobot.say("Hello everyone")
myRobot.anim.wave()
myRobot.head.look_left()
target = myRobot.vision.find_object("red")
if target.found:
    myRobot.pickup.pick_up("red")
```

See [API.md](./docs/API.md) for the full proposed surface.

## Lesson Arc

The planned sequence is based on the upstream TonyPi tutorial structure and
its main program folders under `Functions/` and the action programming course.

1. Lesson 1 - Robot Demo
2. Lesson 2 - Talking, head movement, and gestures
3. Lesson 3 - Action groups and performances
4. Lesson 4 - Single color detection
5. Lesson 5 - Color recognition and reactions
6. Lesson 6 - Target position recognition
7. Lesson 7 - Object tracking
8. Lesson 8 - Auto shooting
9. Lesson 9 - Line follow
10. Lesson 10 - Tag detection and tag actions
11. Lesson 11 - Face detect and greeting
12. Lesson 12 - Pickup and intelligent transport

See [LESSON_STRUCTURE.md](./docs/LESSON_STRUCTURE.md) for the full mapping.

## Integration Notes

- `robot-classroom` should sync this repo into `LESSONS_DIR/matatonypi`.
- `robot-console` should assign lessons using the `matatonypi` robot type.
- `robot_ops_web` should run with `ROBOT_TYPE=TonyPi` or `ROBOT_TYPE=MataTonyPi`
  and use the TonyPi profile for branding and admin/runtime behavior.
