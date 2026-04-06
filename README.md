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
See [ACTION_GROUPS.md](./docs/ACTION_GROUPS.md) for direct TonyPi action-group access and dance move notes.

## Current Lessons

The repo currently includes these student-facing lessons:

### Lesson 1 - TonyPi Show Starter

Path: `lessons/lesson01`

Summary:
- introduces the `student_robot_v2` API
- covers speech, head movement, arms, poses, and walking
- demonstrates color, face, tag, snapshot, and hand-recognition vision calls
- introduces pickup-style commands
- ends with a remixable mini performance

Included notebooks:
- `lessons/lesson01/level_1/Lesson01.ipynb`
- `lessons/lesson01/demos/Robot_Demo.ipynb`

### Lesson 13 - Rock Paper Scissors

Path: `lessons/lesson13`

Summary:
- uses `myRobot.vision.recognize_hands(show=True)` to read player gestures
- lets TonyPi choose rock, paper, or scissors
- compares the player move and robot move
- reacts with TonyPi speech and expressive poses
- works as a foundation for scorekeeping and multi-round classroom games

Included notebooks:
- `lessons/lesson13/level_1/Lesson13.ipynb`

## Planned Lesson Arc

The wider lesson sequence is based on the upstream TonyPi tutorial structure and
its main program folders under `Functions/` and the action programming course.

1. Lesson 1 - TonyPi Show Starter
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
13. Lesson 13 - Rock Paper Scissors

See [LESSON_STRUCTURE.md](./docs/LESSON_STRUCTURE.md) for the broader mapping plan.

## Lesson Notes

- Lesson 1 is the best starting point for bringing up a new TonyPi robot or checking the student API.
- Lesson 13 depends on hand recognition and works best when MediaPipe is available on the robot image.
- Vision support is strongest today for colors, faces, tags, snapshots, and hand recognition.
- Object detection and fully autonomous pickup are still being expanded.

## Integration Notes

- `robot-classroom` should sync this repo into `LESSONS_DIR/matatonypi`.
- `robot-console` should assign lessons using the `matatonypi` robot type.
- `robot_ops_web` should run with `ROBOT_TYPE=TonyPi` or `ROBOT_TYPE=MataTonyPi`
  and use the TonyPi profile for branding and admin/runtime behavior.
