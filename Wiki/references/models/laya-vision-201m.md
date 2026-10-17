# Laya Vision 201M

**Status:** Starting candidate for configurable visual decisions in the [recommended order](index.md#recommended-starting-order), recorded at the user's request on 2026-10-16. Not installed or evaluated in SecondHands.

## Capability and role

The [model card](https://huggingface.co/thaitea/laya-vision-201m) describes a 201M-parameter experimental model that accepts an image, optional context, and typed questions. It scores predefined answers without generating text. Question types cover choices, yes/no probabilities, and ordered scores. These published capabilities were checked in this repository conversation on 2026-10-16; calibration claims do not establish reliable gesture decisions for our users.

Use it to test whether configurable questions can distinguish the observed gestures or facial movements. Compare the same examples with the dedicated recognition models. This tests the decision-model goal while keeping a separate recognition baseline.

## First comparison and limits

Use deliberate, neutral, and ambiguous observations, including a no-command outcome. Record the [shared measurements](../../experiments-before-saturday.md#measurements), especially false activation, abstention, latency, and the effort to change available choices.

Gesture accuracy, memory use, Mac performance, and Snapdragon latency remain untested. No ExecuTorch or Windows ARM64 deployment has been verified in this repository. The model card lists CC BY-NC-SA 4.0 weights, which include noncommercial terms; long-term commercial suitability remains unresolved. The text/JSON [Laya 322M and 421M candidates](index.md#laya-322m-and-421m) are distinct from this model.
