# MataTonyPi Lesson Structure

This lesson plan is based on the upstream Hiwonder TonyPi documentation and
the programs listed in the TonyPi `Functions/` directory.

## Upstream Sources Used

- TonyPi docs index:
  - action programming course
  - AI vision projects
  - intelligent transport course
- TonyPi upstream program mapping:
  - `Color_Warning.py`
  - `ColorDetect.py`
  - `ColorPositionRecognition.py`
  - `ColorTrack.py`
  - `Follow.py`
  - `KickBall.py`
  - `VisualPatrol.py`
  - `Tag_Detect.py`
  - `ApriltagDetect.py`
  - `FaceDetect.py`
  - `Transport.py`

## Design Goals

- Use one public student library: `student_robot_v2`
- Match the classroom packaging style of `MataTurboPi`
- Match the expressive, action-group-heavy teaching style needed for a humanoid robot
- Put the full “wow factor” up front in the demo lesson
- Keep object detection, pickup, and transport as core learning goals
- Include Piper TTS from the start through `myRobot.say(...)`

## Recommended Lesson Sequence

### Lesson 1 - Robot Demo

Purpose:
- Show students everything TonyPi can do in one guided notebook

Demo notebook should showcase:
- `myRobot.say("...")` with Piper TTS
- waving
- bowing
- dancing
- head left/right/up/down
- yes/no reactions
- walking and turning
- color detection snapshot
- object tracking
- line follow preview
- tag recognition reaction
- face greeting
- pickup preview
- transport preview

Suggested lesson assets:
- `lessons/lesson01/demos/Robot_Demo.ipynb`
- `lessons/lesson01/level_1/Lesson01.ipynb`

Upstream references:
- action group programming
- AI vision overview
- intelligent transport demo

### Lesson 2 - Talking, Head Movement, and Gestures

Purpose:
- Make TonyPi feel alive and approachable

Student focus:
- `say()`
- `head.look_left()`
- `head.look_right()`
- `head.nod()`
- `head.shake()`
- `arms.hands_up()`
- `anim.greet()`

Upstream references:
- action groups
- app control examples

### Lesson 3 - Action Groups and Performances

Purpose:
- Introduce prebuilt motion sequences and student-made performances

Student focus:
- running named actions
- combining actions with speech
- building a short performance sequence

Upstream references:
- call action group
- action group programming
- integrate action groups
- call action group using command

### Lesson 4 - Single Color Detection

Purpose:
- Introduce the camera and simple color detection

Student focus:
- detect one color
- understand lighting and threshold sensitivity
- trigger a reaction when color is found

Upstream references:
- `Functions/Color_Warning.py`

### Lesson 5 - Color Recognition and Reactions

Purpose:
- Recognize multiple colors and respond differently

Student focus:
- `vision.find_color("red")`
- react with nod / shake / speech
- map color to action

Upstream references:
- `Functions/ColorDetect.py`

### Lesson 6 - Target Position Recognition

Purpose:
- Move from “what color is it?” to “where is it?”

Student focus:
- get object position
- read x/y location
- decide left / right / centered

Upstream references:
- `Functions/ColorPositionRecognition.py`

### Lesson 7 - Object Tracking

Purpose:
- Follow a moving colored target

Student focus:
- head tracking
- body tracking
- responsive movement based on vision

Upstream references:
- `Functions/ColorTrack.py`
- `Functions/Follow.py`

### Lesson 8 - Auto Shooting

Purpose:
- Use vision plus body alignment to approach and kick a ball

Student focus:
- locate target
- approach
- align
- trigger kick action

Upstream references:
- `Functions/KickBall.py`

### Lesson 9 - Line Follow

Purpose:
- Follow a colored or dark line reliably

Student focus:
- tune target color
- keep body aligned to track
- compare line logic with object tracking logic

Upstream references:
- `Functions/VisualPatrol.py`

### Lesson 10 - Tag Detection and Tag Actions

Purpose:
- Detect AprilTags and react with different actions

Student focus:
- identify tag IDs
- trigger different motions per tag
- build a tag-controlled performance

Upstream references:
- `Functions/Tag_Detect.py`
- `Functions/ApriltagDetect.py`

### Lesson 11 - Face Detect and Greeting

Purpose:
- Make TonyPi socially interactive

Student focus:
- detect face
- wave and greet
- combine looking + speaking + gesture

Upstream references:
- `Functions/FaceDetect.py`

### Lesson 12 - Pickup and Intelligent Transport

Purpose:
- Combine vision, movement, gripping, and destination logic

Student focus:
- detect object color
- approach object
- pick up object
- find matching destination tag
- place object down

Upstream references:
- `Functions/Transport.py`
- transport course in the docs

## Bundle Structure

Recommended directory layout:

```text
lessons/
  lesson01/
    lesson.json
    demos/
    level_1/
  lesson02/
    lesson.json
    level_1/
  lesson03/
    lesson.json
    level_1/
  lesson04/
    lesson.json
    level_1/
  lesson05/
    lesson.json
    level_1/
  lesson06/
    lesson.json
    level_1/
  lesson07/
    lesson.json
    level_1/
  lesson08/
    lesson.json
    level_1/
  lesson09/
    lesson.json
    level_1/
  lesson10/
    lesson.json
    level_1/
  lesson11/

## README Standard

Each lesson `level_1/README.md` should include enough context for a teacher or
student to understand the notebook before running it.

Minimum sections:

- `Goal`
- `Quick Start`
- `How this lesson works`
- `What students will use`
- `Suggested practice flow`
- `Required flow`
- `Debugging requirement`
- `Success criteria`
- `Challenge ideas`
- `V2 API focus`

Practical rules:

- write the README as a teaching guide, not a placeholder
- explain the algorithm or control flow, not just the API call names
- state what should happen when detection fails
- include at least one debugging requirement that forces students to inspect runtime values
- include success criteria that can be tested in the classroom
- include challenge ideas that extend the lesson without changing its core goal

Examples of stronger documentation patterns:

- explain why a lesson uses loops, thresholds, or pauses
- explain what values from a result object matter
- explain the safe order of operations for movement tasks
- distinguish preview/demo behavior from fully autonomous behavior
    lesson.json
    level_1/
  lesson12/
    lesson.json
    level_1/
```

## V2 API Emphasis by Lesson

- Lessons 1-3:
  - `say`, `anim`, `head`, `arms`, `pose`
- Lessons 4-7:
  - `vision`
- Lessons 8-9:
  - `motion` + `vision`
- Lessons 10-11:
  - `vision` + `anim` + `say`
- Lesson 12:
  - `pickup` + `vision` + `motion`

## Demo Design Notes

The demo should feel like a show, not a test script.

Recommended flow:
1. Wake up and stand
2. Introduce itself using Piper TTS
3. Look around with the head
4. Wave hello
5. Perform one or two action-group motions
6. Show movement by walking and turning
7. Show color detection on a target
8. Track a target briefly
9. React to an AprilTag
10. Greet a face
11. Pick up an object
12. End with a short celebration and spoken goodbye

This should be the strongest “all capabilities” notebook in the library.
