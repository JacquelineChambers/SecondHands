# Laya Vision 201M

**Status:** Installed and run locally on Mac MPS with public sample images on 2026-10-17. This establishes local execution, not reliable gesture recognition. Laya remains a comparison candidate in the [recommended order](index.md#recommended-starting-order).

## Capability and role

The [model card](https://huggingface.co/thaitea/laya-vision-201m) describes a 201M-parameter experimental model that accepts an image, optional context, and typed questions. It scores predefined answers without generating text. Question types cover choices, yes/no probabilities, and ordered scores. These published capabilities were checked in this repository conversation on 2026-10-16; calibration claims do not establish reliable gesture decisions for our users.

Use it to test whether configurable questions can distinguish the observed gestures or facial movements. Compare the same examples with the dedicated recognition models. This tests the decision-model goal while keeping a separate recognition baseline.

## First comparison and limits

Use deliberate, neutral, and ambiguous observations, including a no-command outcome. Record the [shared measurements](../../experiments-before-saturday.md#measurements), especially false activation, abstention, latency, and the effort to change available choices.

Gesture accuracy across users and Snapdragon latency remain untested. No ExecuTorch or Windows ARM64 deployment has been verified in this repository. The [pinned model card](https://huggingface.co/thaitea/laya-vision-201m/blob/0b6228f7a0762566de1c4539e9aa4eb1c1aef5f4/README.md) lists CC BY-NC-SA 4.0 weights, which include noncommercial terms; long-term commercial suitability remains unresolved. The code and base model have Apache-2.0 licenses, which do not replace the released weights' license. The text/JSON [Laya 322M and 421M candidates](index.md#laya-322m-and-421m) are distinct from this model.

## Verified Mac execution

The local [experiment entry point](../../../experiments/laya_vision.py) uses a separate locked environment. The observed runs used Python 3.12.9, PyTorch 2.14.1, Transformers 5.17.0, and float32 on Apple MPS. The model revision is `0b6228f7a0762566de1c4539e9aa4eb1c1aef5f4`; the [source revision](https://github.com/r33drichards/laya-vision/tree/9e1e2419d855ad3e1a2af4d4bd1ef6be5418842c) is `9e1e2419d855ad3e1a2af4d4bd1ef6be5418842c`.

From the repository root, use `just download-laya` to fetch the pinned model and `just test-laya` to run the public hand samples. Use `just recognize-laya path/to/image.jpg` for another local image. The commands are owned by the [root justfile](../../../justfile). Downloads require network access; recognition uses the cached model offline.

The inspected local reports are `artifacts/results/laya-hand.json` and `artifacts/results/laya-face.json`. These generated files stay outside Git. Both runs used the public MediaPipe [portrait](https://storage.googleapis.com/mediapipe-assets/portrait.jpg) and [thumb-up](https://storage.googleapis.com/mediapipe-assets/thumb_up.jpg) images. Each image had one first request followed by three measured warm requests.

The hand question was “Which visible hand gesture is present?” Choices were `thumbs up`, `open palm`, `closed fist`, `other hand pose`, and `no visible hand`:

- On `thumb_up.jpg`, the selected answer was `thumbs up`, with score 0.4938 and warm median 62.04 ms.
- On `portrait.jpg`, the selected answer was `closed fist`, with score 0.4105 and warm median 64.00 ms. The portrait contains resting hands; it is not a labeled command-gesture example.

The face question was “Which visible facial movement is present?” Choices were `smiling`, `mouth open`, `neutral expression`, and `no visible face`:

- On `portrait.jpg`, the selected answer was `smiling`, with score 0.7810 and warm median 63.74 ms.
- On the negative face example `thumb_up.jpg`, the model incorrectly selected `smiling`, with score 0.5324 and warm median 62.72 ms, despite the `no visible face` choice.

All repeated outputs within each image/question combination were identical. The hand run's model load took 4.24 seconds; the face run's load took 4.21 seconds. Peak process RSS was about 1,925–1,928 MiB. RSS does not establish total MPS allocation or target-device memory requirements.

Request timings include preprocessing, inference, output decoding, and device synchronization. They exclude image-file reading and model loading. These two-image smoke checks are not an accuracy benchmark or evidence that a score establishes command intent. In particular, a supplied absence option did not prevent the observed false face classification.

## Compatibility findings

During local setup, Transformers 4.57.6 rejected the saved tokenizer's list-valued `extra_special_tokens`. Transformers 5.20.1 returned image features as a list, which the pinned Laya implementation did not accept. Transformers 5.17.0 completed inference and is the verified experiment pin.

The working version still warned that the backbone's `pad_token_id` was outside its vocabulary. The recorded runs completed despite this warning; its wider effect has not been established. Keep the pinned combination for reproducibility and rerun the smoke checks before upgrading.
