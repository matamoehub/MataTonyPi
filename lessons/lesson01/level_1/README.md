# Lesson 1 - TonyPi Show Starter

## Goal

Introduce students to TonyPi's main commands, then help them build a short robot performance with personality.

## Quick Start

Students begin with:

```python
from lesson_header import *

print(myRobot.status())
```

`lesson_header` loads the lesson environment and creates:

```python
from student_robot_v2 import bot

myRobot = bot()
```

## How To Use TonyPi

Most commands follow the same pattern:

```python
myRobot.say("Hello everyone")
myRobot.anim.wave()
myRobot.head.look_left()
myRobot.motion.walk_forward(steps=1)
```

TonyPi is organized into short command groups called namespaces.

## Top-Level Commands

Use these when you want simple robot-wide actions.

### `myRobot.say(text, block=True, voice=None)`

Make TonyPi speak.

```python
myRobot.say("Hello everyone")
myRobot.say("I can use the Amy voice", voice="amy")
```

### `myRobot.status()`

Show robot and backend information.

```python
print(myRobot.status())
```

### `myRobot.home()`

Return TonyPi to a calm finishing position.

```python
myRobot.home()
```

### `myRobot.stop()`

Stop active movement flow.

```python
myRobot.stop()
```

### `myRobot.stand()` and `myRobot.sit()`

Move into common body poses.

```python
myRobot.stand()
myRobot.sit()
```

## Animation Commands

Use `myRobot.anim` for expressive built-in robot actions.

### Available functions

- `myRobot.anim.wave()`
- `myRobot.anim.greet()`
- `myRobot.anim.dance()`
- `myRobot.anim.celebrate()`
- `myRobot.anim.think()`
- `myRobot.anim.sad()`
- `myRobot.anim.yes()`
- `myRobot.anim.no()`
- `myRobot.anim.scan()`

### Example

```python
myRobot.anim.greet()
myRobot.anim.wave()
myRobot.anim.celebrate()
```

## Head Commands

Use `myRobot.head` to look around.

### Available functions

- `myRobot.head.look_left()`
- `myRobot.head.look_right()`
- `myRobot.head.look_up()`
- `myRobot.head.look_down()`
- `myRobot.head.center()`
- `myRobot.head.nod()`
- `myRobot.head.shake()`
- `myRobot.head.scan()`

### Example

```python
myRobot.head.center()
myRobot.head.look_left()
myRobot.head.look_right()
myRobot.head.center()
```

## Arm Commands

Use `myRobot.arms` for hand and arm poses.

### Available functions

- `myRobot.arms.left_up()`
- `myRobot.arms.right_up()`
- `myRobot.arms.hands_up()`
- `myRobot.arms.open()`
- `myRobot.arms.close()`
- `myRobot.arms.center()`
- `myRobot.arms.grab_pose()`
- `myRobot.arms.carry_pose()`
- `myRobot.arms.release_pose()`

### Example

```python
myRobot.arms.open()
myRobot.arms.close()
myRobot.arms.hands_up()
myRobot.arms.center()
```

## Pose Commands

Use `myRobot.pose` for full-body posture changes.

### Available functions

- `myRobot.pose.ready()`
- `myRobot.pose.neutral()`
- `myRobot.pose.bow()`
- `myRobot.pose.stand()`
- `myRobot.pose.sit()`
- `myRobot.pose.carry()`

### Example

```python
myRobot.pose.ready()
myRobot.pose.bow()
myRobot.pose.stand()
```

## Motion Commands

Use `myRobot.motion` for walking and turning.

### Available functions

- `myRobot.motion.walk_forward(steps=1)`
- `myRobot.motion.walk_backward(steps=1)`
- `myRobot.motion.turn_left(steps=1)`
- `myRobot.motion.turn_right(steps=1)`
- `myRobot.motion.step_left(steps=1)`
- `myRobot.motion.step_right(steps=1)`
- `myRobot.motion.approach()`
- `myRobot.motion.stop()`

### Example

```python
myRobot.motion.walk_forward(steps=1)
myRobot.motion.turn_left(steps=1)
myRobot.motion.step_right(steps=1)
myRobot.motion.stop()
```

## Vision Commands

Use `myRobot.vision` to inspect what the camera sees.

### Available functions

- `myRobot.vision.find_color(name)`
- `myRobot.vision.find_object(name)`
- `myRobot.vision.find_face()`
- `myRobot.vision.recognize_hands(show=True)`
- `myRobot.vision.find_tag(tag_id)`
- `myRobot.vision.track_color(name)`
- `myRobot.vision.track_face()`
- `myRobot.vision.snapshot()`
- `myRobot.vision.scan_for(name)`

### Example

```python
print(myRobot.vision.find_color("blue").to_dict())
print(myRobot.vision.find_face().to_dict())
print(myRobot.vision.find_tag(1).to_dict())
print(myRobot.vision.recognize_hands(show=True))
print(myRobot.vision.scan_for("blue"))
myRobot.vision.snapshot()
```

### Current classroom support

- `find_color`, `track_color`, and `scan_for` currently support: `red`, `green`, `blue`, and `yellow`
- `find_face()` and `track_face()` work with the robot's face-detection backend
- `recognize_hands(show=True)` works when MediaPipe is available on the robot image
- `find_object(name)` is still a placeholder for a future object-recognition lesson

## Pickup Commands

Use `myRobot.pickup` for the pickup flow taught later in the course.

### Available functions

- `myRobot.pickup.approach_object(name)`
- `myRobot.pickup.pick_up(name)`
- `myRobot.pickup.grab()`
- `myRobot.pickup.carry()`
- `myRobot.pickup.place_down()`
- `myRobot.pickup.release()`
- `myRobot.pickup.transport(name)`

### Example

```python
myRobot.pickup.approach_object("block")
myRobot.pickup.pick_up("block")
myRobot.pickup.carry()
myRobot.pickup.place_down()
myRobot.pickup.release()
```

## Voice Commands

Use `myRobot.voice` for voice-specific helpers.

### Available functions

- `myRobot.voice.say(text, block=True, voice=None)`
- `myRobot.voice.speak(text, block=True, voice=None)`
- `myRobot.voice.voices()`
- `myRobot.voice.show_voices()`
- `myRobot.voice.select(voice=None, number=None)`
- `myRobot.voice.select_voice(voice=None, number=None)`
- `myRobot.voice.select_voice_number(number)`
- `myRobot.voice.greet()`
- `myRobot.voice.celebrate()`
- `myRobot.voice.think()`

### Example

```python
print(myRobot.voice.voices())
myRobot.voice.select_voice("amy")
myRobot.voice.say("Hello from TonyPi")
```

## Success Criteria

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

This robot build supports color detection, face detection, tag lookup, snapshots, and MediaPipe hand recognition. Object detection and fully autonomous pickup are still simplified, which is fine for Lesson 1 because the goal is to learn the public API shape and build confidence using it.
