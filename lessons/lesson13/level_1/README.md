# Lesson 13 - Rock Paper Scissors

## Goal

Use TonyPi hand recognition, speech, and expressive actions to play a full round of rock paper scissors.

## What students will use

- load TonyPi with `lesson_header`
- use `myRobot.vision.recognize_hands(show=True)` to read a player hand sign
- make TonyPi count down and pick a move
- compare the player move with the robot move
- build a best-of-three game or remix the celebration routines

## Teaching Note

This lesson works best when MediaPipe is available on the robot image. If hand detection is unavailable, the notebook still shows students how the game logic is structured and reports a clear note in the result.
