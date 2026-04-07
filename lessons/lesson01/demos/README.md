# Lesson 1 demos

This folder contains a teacher-facing demo notebook that runs a mini TonyPi
performance using `student_robot_v2`.

Use it to:

- verify that the lesson loader works
- confirm the robot library is installed correctly
- preview the command flow before students work through the guided notebook
- understand every move, voice line, and vision call used in the show

## Demo notebook

- `Robot_Demo.ipynb`

The demo is split into these stages:

1. Grand entrance
2. Head and arms
3. Movement and poses
4. Vision showcase
5. Pickup story
6. Finale

## Setup commands

The demo starts with:

```python
from lesson_loader import setup
setup(verbose=True)

from student_robot_v2 import bot
import time

myRobot = bot()
myRobot.head.center()
time.sleep(0.5)
```

What this does:

- loads the lesson paths
- creates the TonyPi robot object
- resets the head to the center position before the show begins

## Grand entrance

Commands used:

- `myRobot.head.center()`
- `myRobot.say("Hello everyone. TonyPi is ready to perform.")`
- `myRobot.anim.greet()`
- `myRobot.anim.wave()`
- `myRobot.pose.ready()`

What each move means:

- `head.center()`: place the head in the neutral forward-looking position
- `say(...)`: speak the opening line through the configured TonyPi speech system
- `anim.greet()`: run a greeting-style action group
- `anim.wave()`: wave to the audience
- `pose.ready()`: return to a neat standing pose ready for the next section

## Head and arms

Commands used:

- `myRobot.head.center()`
- `myRobot.head.look_left()`
- `myRobot.head.look_right()`
- `myRobot.head.look_up()`
- `myRobot.head.look_down()`
- `myRobot.head.center()`
- `myRobot.head.nod()`
- `myRobot.head.shake()`
- `myRobot.arms.left_up()`
- `myRobot.arms.right_up()`
- `myRobot.arms.hands_up()`
- `myRobot.arms.open()`
- `myRobot.arms.close()`
- `myRobot.arms.center()`

What each move means:

- `look_left()`: turn the head to the robot's left
- `look_right()`: turn the head to the robot's right
- `look_up()`: tilt the head upward
- `look_down()`: tilt the head downward
- `nod()`: short yes-style head motion
- `shake()`: short no-style head motion
- `left_up()`: raise the left arm
- `right_up()`: raise the right arm
- `hands_up()`: lift both arms
- `open()`: open the arms or hands into a wider pose
- `close()`: close the arms or hands back in
- `center()`: return the arms to a centered resting pose

## Movement and poses

Commands used:

- `myRobot.head.center()`
- `myRobot.pose.bow()`
- `myRobot.stand()`
- `myRobot.motion.walk_forward(steps=1)`
- `myRobot.motion.walk_backward(steps=1)`
- `myRobot.motion.turn_left(steps=1)`
- `myRobot.motion.turn_right(steps=1)`
- `myRobot.motion.step_left(steps=1)`
- `myRobot.motion.step_right(steps=1)`
- `myRobot.anim.dance()`
- `myRobot.motion.stop()`

What each move means:

- `pose.bow()`: perform a bowing pose
- `stand()`: stand upright again
- `walk_forward(steps=1)`: take one forward walking step sequence
- `walk_backward(steps=1)`: take one backward step sequence
- `turn_left(steps=1)`: turn left once
- `turn_right(steps=1)`: turn right once
- `step_left(steps=1)`: sidestep left
- `step_right(steps=1)`: sidestep right
- `anim.dance()`: run a dance-style action group
- `motion.stop()`: stop active movement

## Vision showcase

Commands used:

- `myRobot.head.center()`
- `myRobot.vision.find_color("blue")`
- `myRobot.vision.find_object("cube")`
- `myRobot.vision.find_face()`
- `myRobot.vision.find_tag(7)`
- `myRobot.vision.track_color("blue")`
- `myRobot.vision.track_face()`
- `myRobot.vision.scan_for("blue")`
- `myRobot.vision.snapshot()`

What each move means:

- `find_color("blue")`: look for a blue object in the camera frame
- `find_object("cube")`: attempt object detection for a cube
- `find_face()`: look for a human face
- `find_tag(7)`: look for AprilTag id `7`
- `track_color("blue")`: run the blue color tracking path
- `track_face()`: run the face tracking path
- `scan_for("blue")`: scan for a supported target, here blue
- `snapshot()`: capture and display a camera image

Notes:

- the head is centered before vision starts so the robot is not looking down
- some vision features depend on camera setup and installed packages on the robot
- `find_object("cube")` may still be a placeholder depending on the current backend

## Pickup story

Commands used:

- `myRobot.head.center()`
- `myRobot.say("I found a cube. I will bring it over.")`
- `myRobot.pickup.approach_object("cube")`
- `myRobot.pickup.pick_up("cube")`
- `myRobot.pickup.carry()`
- `myRobot.pickup.place_down()`
- `myRobot.pickup.release()`

What each move means:

- `approach_object("cube")`: move into a pickup-style approach
- `pick_up("cube")`: perform a pickup action sequence
- `carry()`: switch to a carry posture or carry-style action group
- `place_down()`: place the object down
- `release()`: release the grasp

Note:

- this section is a story-style demo and may rely on action-group approximations rather than full object-aware pickup logic

## Finale

Commands used:

- `myRobot.head.center()`
- `myRobot.say("Thank you for watching my TonyPi show.")`
- `myRobot.anim.think()`
- `myRobot.anim.yes()`
- `myRobot.anim.celebrate()`
- `myRobot.voice.celebrate()`
- `myRobot.home()`

What each move means:

- `anim.think()`: thoughtful expression using head movement
- `anim.yes()`: yes-style gesture
- `anim.celebrate()`: celebratory full-body action
- `voice.celebrate()`: short celebration phrase
- `home()`: return the robot to its home pose

## Performance pacing

The demo uses a small helper:

```python
def pause(seconds=0.35):
    time.sleep(seconds)
```

Why it is there:

- gives each move time to finish
- makes the performance easier to watch
- prevents head, arm, and walking motions from feeling rushed

## Tips for teachers

- run the demo with enough space around the robot for walking and turning
- keep the head centered before starting vision-related cells
- if speech is silent, check the configured audio device and Piper playback path
- if a movement looks wrong, test the command on its own before running the full show
- use the stage sections one at a time when debugging

## Full Command Reference

This section lists the full TonyPi student API with short examples that are
useful when extending the demo.

### Start here

```python
from student_robot_v2 import bot

myRobot = bot()
print(myRobot.status())
```

### Top-level commands

```python
myRobot.say("Hello everyone")
myRobot.stop()
print(myRobot.status())
myRobot.home()
myRobot.stand()
myRobot.sit()
```

### Animation commands

```python
myRobot.anim.wave()
myRobot.anim.greet()
myRobot.anim.dance()
myRobot.anim.celebrate()
myRobot.anim.think()
myRobot.anim.sad()
myRobot.anim.yes()
myRobot.anim.no()
myRobot.anim.scan()
```

### Action-group commands

These give direct access to installed TonyPi action groups.

```python
print(myRobot.anim.list_action_groups())
myRobot.anim.show_action_groups()
print(myRobot.anim.catalog())
print(myRobot.anim.dance_moves())
myRobot.anim.run("wave")
myRobot.anim.run_id(16)
```

### Head commands

```python
myRobot.head.look_left()
myRobot.head.look_right()
myRobot.head.look_up()
myRobot.head.look_down()
myRobot.head.center()
myRobot.head.nod()
myRobot.head.shake()
myRobot.head.scan()
```

### Arm commands

```python
myRobot.arms.left_up()
myRobot.arms.right_up()
myRobot.arms.hands_up()
myRobot.arms.open()
myRobot.arms.close()
myRobot.arms.center()
myRobot.arms.grab_pose()
myRobot.arms.carry_pose()
myRobot.arms.release_pose()
```

### Pose commands

```python
myRobot.pose.ready()
myRobot.pose.neutral()
myRobot.pose.bow()
myRobot.pose.stand()
myRobot.pose.sit()
myRobot.pose.carry()
```

### Movement commands

```python
myRobot.motion.walk_forward(steps=1)
myRobot.motion.walk_backward(steps=1)
myRobot.motion.turn_left(steps=1)
myRobot.motion.turn_right(steps=1)
myRobot.motion.step_left(steps=1)
myRobot.motion.step_right(steps=1)
myRobot.motion.approach()
myRobot.motion.stop()
```

### Vision commands

```python
print(myRobot.vision.find_color("blue").to_dict())
print(myRobot.vision.find_object("cube").to_dict())
print(myRobot.vision.find_face().to_dict())
print(myRobot.vision.find_tag(7).to_dict())
print(myRobot.vision.recognize_hands(show=True))
print(myRobot.vision.track_color("blue"))
print(myRobot.vision.track_face())
print(myRobot.vision.scan_for("blue"))
print(myRobot.vision.snapshot())
```

Vision notes:

- `find_color("blue")`, `find_face()`, and `snapshot()` are the most useful demo checks
- `find_object("cube")` may still be limited depending on the backend
- `find_tag(7)` depends on AprilTag support being available on the robot image
- `recognize_hands(show=True)` depends on MediaPipe support

### Pickup commands

```python
myRobot.pickup.approach_object("cube")
myRobot.pickup.pick_up("cube")
myRobot.pickup.grab()
myRobot.pickup.carry()
myRobot.pickup.place_down()
myRobot.pickup.release()
myRobot.pickup.transport("cube")
```

### Voice commands

```python
myRobot.voice.say("Hello from TonyPi")
myRobot.voice.greet()
myRobot.voice.celebrate()
myRobot.voice.think()
print(myRobot.voice.voices())
print(myRobot.voice.select_voice("amy"))
print(myRobot.voice.select_voice_number(1))
```

### Controller commands

These are reference helpers for the TonyPi wireless controller layout.

```python
print(myRobot.controller.buttons())
myRobot.controller.show_buttons()
print(myRobot.controller.dance_buttons())
myRobot.controller.show_dance_buttons()
print(myRobot.controller.modes())
print(myRobot.controller.summary())
```

### Team cue commands

Use these when two or more TonyPi robots are performing together.

```python
print(myRobot.team.local_ip())
print(myRobot.team.start_server())
print(myRobot.team.server_status())
print(myRobot.team.signal("192.168.50.62", "entrance"))
print(myRobot.team.broadcast(["192.168.50.62", "192.168.50.63"], "bow"))
print(myRobot.team.wait_for("entrance", timeout=30))
print(myRobot.team.cues())
print(myRobot.team.stop_server())
```

### Quick demo remix example

```python
myRobot.head.center()
myRobot.say("Welcome to my custom show.")
myRobot.anim.wave()
myRobot.motion.turn_left(steps=1)
myRobot.motion.turn_right(steps=1)
myRobot.anim.celebrate()
myRobot.home()
```
