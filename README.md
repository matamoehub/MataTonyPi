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

### Lessons 2-12 - Core TonyPi Curriculum

Paths: `lessons/lesson02` through `lessons/lesson12`

These lessons now cover the planned V2 progression:
- Lesson 2: talking, head movement, and gestures
- Lesson 3: action groups and performances
- Lesson 4: single color detection
- Lesson 5: multi-color recognition and reactions
- Lesson 6: target position recognition
- Lesson 7: object tracking
- Lesson 8: auto shooting flow (approach + kick sequence)
- Lesson 9: line follow logic
- Lesson 10: tag detection and tag-triggered actions
- Lesson 11: face detection and greeting behavior
- Lesson 12: pickup and intelligent transport flow

Each lesson includes a Level 1 notebook (`LessonXX.ipynb`), lesson metadata (`lesson.json`), and loader/header files that initialize the V2 `myRobot` object.

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

### Lesson 14 - Multi-Control Robot Team

Path: `lessons/lesson14`

Summary:
- uses the robot-console TonyPi multi-control APIs
- configures one TonyPi as the server and the others as clients
- tests synchronized action-group execution across multiple robots
- uses the full TonyPi action-group catalog and dance id range
- supports classroom team performances

Included notebooks:
- `lessons/lesson14/level_1/Lesson14.ipynb`

### Lesson 15 - Wireless Joystick Control

Path: `lessons/lesson15`

Summary:
- introduces the TonyPi wireless controller button map
- documents the normal buttons, dance buttons, and controller modes
- shows how the controller lessons connect to the student API
- helps students test movement, gestures, and dances with the joystick

Included notebooks:
- `lessons/lesson15/level_1/Lesson15.ipynb`

### Lesson 16 - Two-Robot Performance Cues

Path: `lessons/lesson16`

This lesson:
- shows how a partner TonyPi can start a cue server
- shows how a leader TonyPi can send named cues
- helps students build a duet where robots speak and move in sequence

Key file:
- `lessons/lesson16/level_1/Lesson16.ipynb`

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
14. Lesson 14 - Multi-Control Robot Team
15. Lesson 15 - Wireless Joystick Control
16. Lesson 16 - Two-Robot Performance Cues

See [LESSON_STRUCTURE.md](./docs/LESSON_STRUCTURE.md) for the broader mapping plan.

## Lesson Notes

- Lesson 1 is the best starting point for bringing up a new TonyPi robot or checking the student API.
- Lesson 13 depends on hand recognition and works best when MediaPipe is available on the robot image.
- Lesson 14 depends on the robot-console and robot_ops_web TonyPi multi-control APIs.
- Lesson 15 focuses on the wireless joystick and the upstream TonyPi button layout.
- Lesson 16 focuses on cue-based performances where one TonyPi can trigger another.
- Vision support is strongest today for colors, faces, tags, snapshots, and hand recognition.
- Object detection and fully autonomous pickup are still being expanded.

## Integration Notes

- `robot-classroom` should sync this repo into `LESSONS_DIR/matatonypi`.
- `robot-console` should assign lessons using the `matatonypi` robot type.
- `robot_ops_web` should run with `ROBOT_TYPE=TonyPi` or `ROBOT_TYPE=MataTonyPi`
  and use the TonyPi profile for branding and admin/runtime behavior.
