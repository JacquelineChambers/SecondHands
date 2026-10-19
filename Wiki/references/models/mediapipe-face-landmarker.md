# MediaPipe Face Landmarker

**Status:** Implemented in the first Python baseline on 2026-10-16. Image execution is smoke-tested on the Mac, and the later [Orbbec live test](../../setup/orbbec-mediapipe.md) verifies CPU execution on the Snapdragon Windows PC. Personalized accuracy and NPU execution remain unverified. See the earlier [Mac observations](../../experiments-before-saturday.md#mediapipe-baseline-observations) and [runbook](../../runbooks/mac-and-snapdragon-development.md#run-mediapipe-face-and-hand-recognition). This is a recognition model bundle, not a configurable decision model.

## Capability and role

The [Google task guide](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker) documents facial landmarks, 52 blendshape scores, and facial transformation matrices. Blendshape scores measure facial movements. The task accepts single images and video/live-stream input. These published capabilities were checked in this repository conversation on 2026-10-16; they are not observations from our application.

For SecondHands, test which facial signals each volunteer can produce comfortably and consistently, then use those observations for personalized controls. A detected facial movement does not by itself establish an intentional command.

## First comparison and limits

Compare deliberate movements with neutral and ambiguous examples. Measure useful signal separation, false activations, and end-to-end latency using the [shared experiment measurements](../../experiments-before-saturday.md#measurements). Keep calibration and command confirmation separate from the model's raw output.

The Mac smoke checks do not establish calibrated facial controls or Snapdragon performance. The later [Windows CPU observations](../../setup/orbbec-mediapipe.md#observed-checks) establish live execution under x64 emulation, with scene-specific timings. A MediaPipe execution path is not an ExecuTorch deployment; [the requested NPU export](../../setup/orbbec-mediapipe.md#executorch-and-npu-prerequisites) remains incomplete. The archive's [MediaPipe Face Detection candidate](index.md#mediapipe-face-detection) is a separate package lead and does not establish this bundle's outputs.
