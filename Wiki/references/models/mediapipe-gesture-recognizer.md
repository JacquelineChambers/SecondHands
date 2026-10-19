# MediaPipe Gesture Recognizer

**Status:** Implemented in the first Python baseline on 2026-10-16. Image execution is smoke-tested on the Mac. The later [Orbbec test](../../setup/orbbec-mediapipe.md) verifies the CPU baseline and an alternate Qualcomm pretrained gesture classifier running through ExecuTorch/QNN on the Snapdragon NPU. Hand detection and landmarks remain on the CPU; personalized accuracy remains unverified. See the earlier [Mac observations](../../experiments-before-saturday.md#mediapipe-baseline-observations) and [runbook](../../runbooks/mac-and-snapdragon-development.md#run-mediapipe-face-and-hand-recognition). This is a recognition model bundle, not a configurable decision model.

## Capability and role

The [Google task guide](https://developers.google.com/edge/mediapipe/solutions/vision/gesture_recognizer) documents hand landmarks, handedness, and common static hand-gesture categories. It supports images and continuous input. These published capabilities were checked in this repository conversation on 2026-10-16; they do not establish our recognition accuracy or latency.

Use the predefined gestures as a baseline before testing personalized gestures. The landmarks can also provide inputs to a [custom PyTorch classifier](index.md#mediapipe-landmarks-with-a-small-pytorch-classifier).

## First comparison and limits

Test the chosen hand poses, neutral hands, ambiguous poses, and frames with no hand. Use the [shared measurements](../../experiments-before-saturday.md#measurements). Live-stream tracking is not proof that a temporal gesture such as a wave is recognized as a sequence.

The smoke checks do not establish useful personalized gesture coverage. The later [Windows observations](../../setup/orbbec-mediapipe.md#observed-checks) distinguish the MediaPipe CPU baseline from the native ARM64 ExecuTorch gesture worker. Public-image comparison and live execution verify the latter's QNN path, with scene-specific timings and a final live rerun pending camera reconnection. This does not establish equivalence between the two gesture-model distributions.

## Qualcomm package lead

[Exchange 4](../../SecondHands-conversation.md#exchange-4--camera-hardware-and-model-options) separately links [Qualcomm AI Hub's MediaPipe Hand Gesture Recognition](https://aihub.qualcomm.com/models/mediapipe_hand_gesture) and a [PyTorch demo](https://github.com/qualcomm/ai-hub-models/blob/main/src/qai_hub_models/models/mediapipe_hand_gesture/README.md). Its source weights are now in [the device inventory](device-downloads.md). Retain that distribution as a possible alternate execution path; output equivalence and Compute execution remain unverified. Sharing a MediaPipe name does not establish an interchangeable package or an ExecuTorch `.pte`.
