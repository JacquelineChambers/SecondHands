# Experiments before Saturday

**Status:** Proposed experiment plan for the lead-up to Saturday, 2026-10-17. This page incorporates “The experiment I'd run before Saturday” from the model review supplied by the user on 2026-10-14. That section matches the [archived source](SecondHands-conversation.md#the-experiment-id-run-before-saturday), including its proposed division of effort and Saturday follow-up. No experiments were run during this documentation update.

## Purpose

Task status and execution evidence links are tracked in [the task plan](plan.md). This page owns the experiment method and recorded results when available.

Compare candidate decision models on SecondHands movements before access to the supplied Compute PC. Use the same small test set on the Apple Silicon Mac to establish a comparative baseline. The results will inform [SH-Q-001 — Model and runtime selection](project.md#sh-q-001--model-and-runtime-selection); Mac results will not establish Snapdragon X Elite performance or compatibility.

## Models and observations

Compare these three models from the supplied review:

- [Laya Vision 201M](https://huggingface.co/thaitea/laya-vision-201m).
- [Mapika Decider 2B Vision](https://huggingface.co/Mapika/decider-2b-vision).
- [MobileCLIP2-S0](https://huggingface.co/apple/MobileCLIP2-S0).

Create approximately 30–50 labeled observations with examples from two different volunteers. Include deliberate movements, neutral movements, and ambiguous gestures. Run the same observations through each model so that the comparison uses the same evidence.

These are experiment candidates from the supplied review, not a final model selection. Their local execution has not been verified in this repository. The [current proposal](proposal.md) continues to own the product architecture and hardware proposal; this benchmark does not select a camera.

## Measurements

| Metric | Question the measurement answers |
| --- | --- |
| Decision accuracy | Does the model choose the correct observable gesture? |
| False activation rate | Does it trigger when no command was intended? |
| Abstention performance | Can it decline uncertain decisions? |
| Median / p95 latency | How responsive is it? p95 is the 95th percentile of measured response times. |
| Memory use | How much memory does it need, and could it fit the event hardware? |
| Calibration effort | How many examples does a new user need? |
| Configurability | Can the available choices change without retraining? |

These measurements concern SecondHands observations. Published benchmarks on unrelated images or decision tasks do not replace this comparison. The source gives no numerical acceptance thresholds or results.

## Proposed division of effort

These roles reproduce the source's recommended responsibilities; they do not record confirmed task assignments.

| Role | Responsibility |
| --- | --- |
| AI specialist | Compare Laya Vision, Mapika Decider, and MobileCLIP2. |
| Project lead | Camera pipeline, calibration data collection, actuator, and application integration. |
| Doctor | Choose movements that are accessible, intentional, and practical; define safe failure behavior. |
| Marketing teammate | Develop the two-person demonstration, product story, and presentation. |

## Saturday follow-up

The source recommends first getting the supplied DeepLab ExecuTorch demonstration running on the Compute PC. Then assess whether a useful part of the vision-decision pipeline can move into ExecuTorch while experimental decision models run through their native local runtimes. Availability of the supplied demonstration and acceptance of this runtime combination remain [evidence gaps](project.md#implementation-and-evidence-limits).
