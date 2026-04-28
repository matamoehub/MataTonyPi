# Lesson 10 - Tag Detection and Tag Actions

## Goal

Detect AprilTags and trigger different actions per tag id.

## Quick Start

```python
from lesson_header import *
print(myRobot.status())
```

## How this lesson works

- students scan for known tag ids
- each tag id should map to a different robot response
- the lesson is about perception plus branching logic

## What students will use

- `myRobot.vision.find_tag(tag_id)`
- loops over several ids
- `if` / `elif` logic
- action groups or voice responses

## Suggested practice flow

1. `for tag_id in [1, 2, 3]:`
2. `tag = myRobot.vision.find_tag(1)`

## Required flow

1. decide which tag ids the notebook supports
2. detect one tag at a time
3. trigger a different robot action per tag
4. handle the "no tag found" case clearly

## Debugging requirement

- print the tag id being tested
- print the returned result
- test with one visible tag before trying multiple branches

## Success criteria

- TonyPi performs different reactions for different tag ids
- students can explain how the decision logic works
- no-tag cases do not crash the notebook flow

## Challenge ideas

- use speech to announce the detected tag
- add a default action for unknown tags
- build a tag-driven mini game or dance selector

## V2 API focus

Use the single `myRobot` object and its sub-namespaces (`anim`, `head`, `arms`, `motion`, `vision`, `pickup`) for every activity.
