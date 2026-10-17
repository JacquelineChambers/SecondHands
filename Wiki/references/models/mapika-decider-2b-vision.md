# Mapika Decider 2B Vision

**Status:** Starting comparison candidate for configurable visual decisions in the [recommended order](index.md#recommended-starting-order), recorded at the user's request on 2026-10-16. Not installed or evaluated in SecondHands.

## Capability and role

The [model card](https://huggingface.co/Mapika/decider-2b-vision) describes typed decisions from an image in one forward pass, using scores over the supplied options instead of generating an answer. This published interface was checked in this repository conversation on 2026-10-16; it is not evidence of useful SecondHands recognition or target-device speed.

Compare this larger, approximately 2B-parameter candidate with [Laya Vision](laya-vision-201m.md) using the same labeled observations and decision questions. The reason for the comparison is to establish whether any accuracy improvement justifies the additional latency and memory.

## First comparison and limits

Use the [shared experiment measurements](../../experiments-before-saturday.md#measurements). Keep changes to questions and choices recorded so that differences in prompts are not mistaken for model differences.

Local vision execution, Windows ARM64 support, memory use, and gesture-specific calibration remain unverified. No model-specific ExecuTorch deployment has been verified in this repository. A documented interface or a model-family CPU path does not establish performance on the supplied Snapdragon PC.
