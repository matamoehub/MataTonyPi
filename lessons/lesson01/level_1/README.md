# Lesson 1 - TonyPi Show Starter

## Goal

Introduce students to TonyPi's main commands, then help them build a short robot performance with personality.

## What students will use

- connect to the lesson robot with `lesson_header`
- make TonyPi talk and greet the class
- move the head, arms, and body through simple actions
- try walking, turning, and stopping
- inspect color, face, tag, snapshot, and hand-recognition results
- run pickup-style actions
- combine several commands into a short robot performance

## Success criteria

- Students can run TonyPi speech, animation, head, arm, pose, and motion commands.
- Students can read supported TonyPi vision results and understand that object-aware pickup is still a later lesson topic.
- Students can remix the final routine into their own short performance.

## Library Rule

Students only use:

```python
from student_robot_v2 import bot
```

They should not import vendor TonyPi modules directly.

## Teaching Note

This robot build supports color detection, face detection, tag lookup,
snapshots, and MediaPipe hand recognition. Object detection and fully
autonomous pickup are still simplified, which is fine for Lesson 1 because the
goal is to learn the public API shape and build confidence using it.
