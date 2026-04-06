# Lesson 1 - TonyPi Feature Tour

## Goal

Introduce students to the full `student_robot_v2` API through a guided robot tour.

## What students should do

- connect to the lesson robot with `lesson_header`
- make TonyPi talk and greet the class
- move the head, arms, and body through simple actions
- try walking, turning, and stopping
- inspect vision results from the classroom API
- run pickup-style actions
- combine several commands into a short robot performance

## Library Rule

Students only use:

```python
from student_robot_v2 import bot
```

They should not import vendor TonyPi modules directly.

## Teaching Note

The current vision and pickup backends are still stubbed, so students will see
logged actions and placeholder detection results. That is fine for Lesson 1:
the goal here is to learn the public API shape and build confidence using it.
