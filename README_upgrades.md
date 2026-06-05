# TonyPi Upgrade Modules — Functions IDs 13–18

> **AIBrain (Gemini Live) has been removed** — it required a paid Google Gemini API key and `google-genai` SDK. All other modules below need no paid external API except optional Anthropic Claude usage in SceneDescribe and PatrolLog.



This document covers the eight new function modules added to the TonyPi platform. All modules reside in `Functions/` and implement the standard `init / start / stop / exit / run(img)` interface so they integrate seamlessly with `Running.py`.

---

## Install dependencies

```bash
pip3 install anthropic mediapipe apriltag
```

Environment variables (set in your shell or systemd unit):

| Variable | Used By | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | SceneDescribe, PatrolLog | Anthropic Claude API key (optional — falls back gracefully if absent) |

---

## Function 13 — EmotionExpress (`Functions/EmotionExpress.py`)

EmotionExpress gives TonyPi a vocabulary of physical emotions expressed through arm servos, head servos, and buzzer tones. Calling `express('happy')` raises both arms to half-height, bobs the head twice, and plays a cheerful two-tone beep. `express('sad')` drops the arms, tilts the head down, and plays a low drone. `express('excited')` triggers the wave action group and a rapid high-frequency buzz. `express('confused')` slowly pans the head left and right. `express('greet')` waves and plays a short acknowledgement beep. All expressions run in a daemon thread, so the camera loop is never blocked. If an emotion is already playing, new requests are silently dropped.

**Trigger:** Call `EmotionExpress.express(emotion_name)` from any module, or load via function ID 13 and trigger via RPC.

**Hardware required:** Bus servos (IDs 6, 7, 14, 15), PWM servos (1, 2), buzzer.

---

## Function 14 — SceneDescribe (`Functions/SceneDescribe.py`)

SceneDescribe captures the current camera frame, encodes it as a base64 JPEG, and sends it to the Anthropic Claude claude-opus-4-5 model with a robot-persona system prompt. The model returns a 1–2 sentence conversational description which is printed to the console and spoken aloud via `espeak-ng` (or `piper` if installed). While the API call is in flight, a "Thinking..." overlay is drawn on the camera feed. Calls are non-blocking; a second trigger while one is in progress is ignored.

**Trigger:** Call `SceneDescribe.trigger()` from any module, or load via function ID 14 and send an RPC trigger. Voice keyword suggestion: "What do you see?"

**Environment variables:** `ANTHROPIC_API_KEY`

**Hardware required:** Camera (640×480). espeak-ng or piper for TTS (optional but recommended).

---

## Function 15 — Follow (`Functions/Follow.py`)

Follow tracks a coloured object (default: red) using LAB colour space and PID control on the head pan servo (servo2). When the blob is centred in frame and the path ahead is clear, the robot advances with `go_forward_one_step`. If a VL53L0X ToF sensor is present (I²C bus 1, address 0x29), distance gating prevents the robot from colliding: below 350 mm it stops advancing; between 350–650 mm it holds position and tracks with the head only; above 650 mm normal following resumes. On `exit()` the ToF sensor is cleanly shut down.

**Trigger:** Load via function ID 15. Change the target colour at runtime with `Follow.set_target_colour('blue')`.

**Hardware required:** Camera, LAB colour calibration YAML, VL53L0X ToF sensor (optional but recommended).

---

## Function 16 — SimonSays (`Functions/SimonSays.py`)

SimonSays is an interactive memory game in which TonyPi plays back a growing sequence of colours (red, green, blue) as buzzer tones and the player must show each colour to the camera in order. Correct responses are rewarded with a head nod and a positive beep; wrong answers or timeouts trigger a sad buzz and the robot stands still. Completing the full sequence triggers a wave and a celebration buzz. Difficulty is adjustable: level 1 (4 rounds, 5 s timeout), level 2 (8 rounds, 5 s), level 3 (8 rounds, 3 s). Colour detection uses the same LAB YAML calibration as the rest of the platform.

**Trigger:** Load via function ID 16. Set difficulty with `SimonSays.set_difficulty(2)` before starting.

**Hardware required:** Camera, LAB colour calibration YAML, buzzer, PWM servo 1 (for nod feedback).

---

## Function 17 — TagNav (`Functions/TagNav.py`)

TagNav detects AprilTag (family `tag36h11`) markers in the camera feed and maintains an in-memory map of every tag seen, including its centroid, bounding area, and last-seen timestamp. Calling `navigate_to_tag(tag_id)` launches a daemon thread that steers the robot toward the requested tag: it turns left or right to centre the tag horizontally, then steps forward until the tag fills 30% of the frame (arrived). If the tag is not visible, the robot searches by rotating right up to 10 seconds before giving up. The tag map is accessible via `get_tag_map()`.

**Trigger:** Call `TagNav.navigate_to_tag(42)` from any module, or load via function ID 17 and send an RPC navigate command.

**Hardware required:** Camera, `apriltag` Python library (`pip3 install apriltag`).

---

## Function 18 — PatrolLog (`Functions/PatrolLog.py`)

PatrolLog combines line-following (black tape on the floor) with obstacle logging and avoidance. It detects the line using HSV thresholding and steers with simple bang-bang control. A background thread polls the VL53L0X ToF sensor every 200 ms; when an obstacle is closer than 400 mm it logs the event, saves a JPEG snapshot to `/home/pi/TonyPi/patrol_logs/`, and executes a back-turn-forward avoidance manoeuvre. When `stop()` is called the full obstacle log is written as JSON and, if `ANTHROPIC_API_KEY` is set, a two-sentence plain-English summary is generated via the Claude API and spoken aloud.

**Trigger:** Load via function ID 18. Logs are written to `/home/pi/TonyPi/patrol_logs/`.

**Environment variables:** `ANTHROPIC_API_KEY` (optional — summary skipped if absent)

**Hardware required:** Camera, black tape on floor, VL53L0X ToF sensor, espeak-ng (optional TTS).

