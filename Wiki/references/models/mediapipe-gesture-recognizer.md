# MediaPipe Gesture Recognizer

**Status:** Starting candidate for hand controls in the [recommended order](index.md#recommended-starting-order), recorded at the user's request on 2026-10-16. Not installed or evaluated in SecondHands. This is a recognition model bundle, not a configurable decision model.

## Capability and role

The [Google task guide](https://developers.google.com/edge/mediapipe/solutions/vision/gesture_recognizer) documents hand landmarks, handedness, and common static hand-gesture categories. It supports images and continuous input. These published capabilities were checked in this repository conversation on 2026-10-16; they do not establish our recognition accuracy or latency.

Use the predefined gestures as a baseline before testing personalized gestures. The landmarks can also provide inputs to a [custom PyTorch classifier](index.md#mediapipe-landmarks-with-a-small-pytorch-classifier).

## First comparison and limits

Test the chosen hand poses, neutral hands, ambiguous poses, and frames with no hand. Use the [shared measurements](../../experiments-before-saturday.md#measurements). Live-stream tracking is not proof that a temporal gesture such as a wave is recognized as a sequence.

Mac and Windows ARM64 execution, useful gesture coverage, and target-device performance remain untested. This MediaPipe path does not itself demonstrate ExecuTorch.

## Qualcomm package lead

[Exchange 4](../../SecondHands-conversation.md#exchange-4--camera-hardware-and-model-options) separately links [Qualcomm AI Hub's MediaPipe Hand Gesture Recognition](https://aihub.qualcomm.com/models/mediapipe_hand_gesture) and a [PyTorch demo](https://github.com/qualcomm/ai-hub-models/blob/main/src/qai_hub_models/models/mediapipe_hand_gesture/README.md). Retain that distribution as a possible alternate execution path. Its downloads, outputs, and Compute support were not reverified here; sharing a MediaPipe name does not establish an interchangeable package or an ExecuTorch `.pte`.
