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
- `myRobot.say(text, block=True, voice=None)`
- `myRobot.stop()`
- `myRobot.status()` — human-readable status of every backend, returns a dict
- `myRobot.versions()` — print + return a table of all library versions
- `myRobot.show_versions()` — alias for `versions()`
- `myRobot.diagnose()` — full hardware diagnostic (head, camera, voice,
  buzzer, ToF, battery, YOLO, action groups); prints a ✓/✗ table and
  returns a dict of results
- `myRobot.home()`
- `myRobot.stand()`
- `myRobot.sit()`
- `myRobot.help()` — print all namespaces; `myRobot.help.<namespace>()` for
  details on one namespace; `myRobot.help.all()` prints every command

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
- `martial_arts()`
- `bow_deep()`
- `catch_ball()`
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
- `centre()` — British spelling alias for `center()`
- `nod()`
- `shake()`
- `scan()`
- `wiggle(cycles=2)`
- `tiny_wiggle(seconds=2.0)`
- `glance_left()`
- `glance_right()`

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
- `punch_left()`
- `punch_right()`
- `punch()`
- `kick_left()`
- `kick_right()`

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
- `walk_fast(steps=1)`
- `turn_left(steps=1)`
- `turn_right(steps=1)`
- `turn_left_fast(steps=1)`
- `turn_right_fast(steps=1)`
- `step_left(steps=1)`
- `step_right(steps=1)`
- `creep(steps=1)`
- `approach()`
- `stop()`

### `myRobot.vision`

- `find_color(name)`
- `find_object(name)` — find a specific object by class name via YOLO26n
- `detect_objects(confidence=0.45)` — detect every object in frame via YOLO26n
- `find_face()`
- `find_faces()` — detect all faces (not just one), returns a list of results
- `recognize_hands(show=True)`
- `detect_pose()` — full body pose: `hands_up`, `t_pose`, `left_hand_up`,
  `right_hand_up`, `neutral`
- `find_tag(tag_id)`
- `track_color(name)`
- `track_face()`
- `move_towards_color(color, steps=1, deadzone=50, push=False, show=False, object_diameter_cm=None)` —
  step sideways to centre a colour, optionally walk forward when centred
- `target_position(color, deadzone=50)` — direction left/center/right/lost + pixel error
- `locate_object(color, deadzone=50, object_diameter_cm=None)` — like
  `target_position` but adds `angle_x_deg`, `lateral_cm`, normalised error
- `which_object(color)` — left-to-right index (1-based) of the largest colour
  object, `0` if not found
- `calibrate_color(color, box_size=80)` — calibrate a colour from the centre
  of the frame
- `set_color_profile(color, lower_hsv, upper_hsv=None)` — set a custom HSV
  colour profile
- `show_profiles()` — print all colour profiles
- `load_calibration(path=None)` — load a camera calibration `.npz` file for
  angular + lateral measurements
- `estimate_distance(pixel_width, object_real_width_cm)` — estimate forward
  distance to an object in cm from its pixel width and known real size
- `object_classes()` — list all 80 COCO object classes YOLO26n can detect
- `yolo_available()` — `True` if YOLO26n is installed
- `describe()` — AI scene description via the Claude API; returns a
  fallback string ("I can't see clearly right now") if the API key is
  missing or the call fails
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

- `find(name)` — snapshot + detect (colour or YOLO) before picking up,
  returns a `DetectionResult`
- `approach_object(name)`
- `pick_up(name)`
- `grab_and_lift()` — squat, grab, and stand in one move (full floor pickup
  sequence)
- `lift_to_chest()` — pick up from the floor and hold at chest height
  instead of raising above head
- `grab()`
- `carry()`
- `place_down()`
- `release()`
- `transport(name)`

### `myRobot.voice`

- `say(text, block=True, voice=None)`
- `speak(text, block=True, voice=None)` — alias for `say()`
- `voices()` — list installed voice names
- `show_voices()` — print installed voices with the active one marked
- `current_voice()` — return the active voice name
- `select(voice=None, number=None)` — switch voice by name or number
- `select_voice(voice=None, number=None)` — alias for `select()`
- `select_voice_number(number)`
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

### `myRobot.team`

- `local_ip()`
- `start_server(port=8765)`
- `stop_server()`
- `server_status()`
- `signal(host, cue, payload=None, port=8765, timeout=5.0)`
- `broadcast(hosts, cue, payload=None, port=8765, timeout=5.0)`
- `wait_for(cue, timeout=None)`
- `cues()`

Use the `team` namespace to stage multi-robot performances. One robot starts a
cue server, and the other robots can wait for named cues such as `"entrance"`
or `"line_two"` before moving or speaking.

### `myRobot.emotion`

- `express(emotion)`
- `happy()`
- `sad()`
- `excited()`
- `confused()`
- `greet()`
- `is_busy()` — `True` if currently expressing
- `available()` — list of emotion names

### `myRobot.battery`

- `voltage()` — battery voltage, e.g. `11.4`
- `percentage()` — battery level 0-100
- `is_low()` — `True` if below the low-battery threshold
- `is_critical()` — `True` if below the critical threshold
- `status()` — dict with voltage, percentage, `is_low`, `is_critical`

### `myRobot.sensors`

- `distance()` — ToF distance in mm, `-1` if unavailable
- `init_distance_sensor()` — start the ToF sensor
- `imu()` — accelerometer data dict
- `buzz(freq_hz, on_secs=0.1, off_secs=0.05, repeat=1)`
- `buzz_pattern(pattern)` — named patterns: `happy`, `sad`, `sos`, `short`,
  `long`

### `myRobot.navigation`

- `go_to_tag(tag_id, timeout=10.0)` — walk to an AprilTag
- `follow_person()` — follow a person (YOLO + ToF)
- `stop()` — stop navigation or following
- `get_tag_map()` — last-seen position of each tag
- `update_tag(tag_id, cx, cy, area)` — called internally by
  `vision.find_tag` to keep the map fresh

### `myRobot.patrol`

- `start()` — begin autonomous patrol with obstacle logging
- `stop()` — stop patrol, save a JSON log, and return an AI-generated
  summary (falls back to a plain obstacle count if the Claude API is
  unavailable)
- `log()` — current obstacle log list
- `update_frame(frame)` — called internally to keep the latest camera frame
  available for obstacle snapshots

### `myRobot.games`

- `simon_says(difficulty=2)` — start Simon Says; `1` easy (4 rounds, 5s
  timeout), `2` medium (8 rounds, 5s timeout), `3` hard (8 rounds, 3s
  timeout)
- `stop_game()`
- `is_game_running()`
- `set_difficulty(level)`

### `myRobot.help`

- `help()` — print a quick reference of all namespaces (this is
  `myRobot.help.__call__`, so just call `myRobot.help()`)
- `help.all()` — print every command across all namespaces
- `help.<namespace>()` — print detailed commands for one namespace, e.g.
  `myRobot.help.vision()`, `myRobot.help.pickup()`

## Public API Rules

- Students import only `student_robot_v2`.
- Method names stay short and descriptive.
- Behind the scenes we can split implementation into helper modules later, but
  those remain private.
- Expressive actions should be available before advanced autonomous tasks.
- All installed TonyPi action groups should remain reachable through `myRobot.anim.run(...)` or `myRobot.anim.run_id(...)` even if they are not wrapped by a named helper yet.
