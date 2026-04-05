# MataTonyPi Roadmap

## Phase 1: Foundation

- Create `common/lib/bootstrap.py`
- Create `common/lib/student_robot_v2.py`
- Establish lesson bundle structure:
  - `common/lib`
  - `lessons/lib`
  - `lessons/lessonXX/{level_1,level_2,demos}`
- Add `lesson.json`, `lesson_loader.py`, and `lesson_header.py` pattern

## Phase 2: Expressive Robot Basics

- Talking via a single `say()` path
- Head movement wrappers
- Arm and hand gesture wrappers
- Action-group animation presets
- Safe `home()`, `stop()`, `stand()`, `sit()`
- Build the opening demo notebook that showcases:
  - speech
  - head movement
  - hand and arm gestures
  - posture changes
  - action-group performances

## Phase 3: Vision

- Color detection
- Face detection
- AprilTag detection
- Camera snapshot helpers
- Tracking helpers

## Phase 4: Pickup and Transport

- Approach target
- Grab pose
- Pickup sequence
- Carry pose
- Place sequence
- Transport challenge lesson

## Phase 5: Platform Integration

- `robot-classroom` sync into `matatonypi`
- `robot-console` lesson assignment support
- `robot_ops_web` TonyPi profile and branding

## Known Constraints

- Vendor TonyPi code should remain untouched.
- Action groups are a key backend dependency and must be referenced, not
  rewritten blindly.
- Pickup reliability will need on-robot tuning for object size, camera angle,
  and action timing.
- The opening demo should intentionally exercise nearly every major TonyPi
  capability so students can immediately see what the robot can do.
