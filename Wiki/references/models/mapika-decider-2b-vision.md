# Mapika Decider 2B Vision

**Status:** Installed and run locally on Mac MPS with public hand and face examples on 2026-10-17. This establishes local execution, not reliable recognition across users. Mapika remains a comparison candidate in the [recommended order](index.md#recommended-starting-order).

## Capability and role

The [model card](https://huggingface.co/Mapika/decider-2b-vision) describes typed decisions from an image in one forward pass, using scores over the supplied options instead of generating an answer. This published interface was checked in this repository conversation on 2026-10-16; it is not evidence of useful SecondHands recognition or target-device speed.

Compare this larger, approximately 2B-parameter candidate with [Laya Vision](laya-vision-201m.md) using the same labeled observations and decision questions. The reason for the comparison is to establish whether any accuracy improvement justifies the additional latency and memory.

## First comparison and limits

Use the [shared experiment measurements](../../experiments-before-saturday.md#measurements). Keep changes to questions and choices recorded so that differences in prompts are not mistaken for model differences.

Windows ARM64 support, target-device memory use, and gesture-specific calibration remain unverified. No model-specific ExecuTorch deployment has been verified in this repository. Local MPS execution and a model-family CPU path do not establish performance on the supplied Snapdragon PC.

## Reproducible setup findings

The reviewed code revision is [`d6fc522aed7fc392576a9b66a330409bc6c382bd`](https://github.com/Mapika/decider/tree/d6fc522aed7fc392576a9b66a330409bc6c382bd). The reviewed model revision is [`863e290863655f1d6b69324d77d09ac972d21609`](https://huggingface.co/Mapika/decider-2b-vision/tree/863e290863655f1d6b69324d77d09ac972d21609). Download the model at that revision and pass the local snapshot directory to `VisionDecisionModel`; its constructor has no `revision` argument.

The package is named `decider-ai`; its Python import is `decider`. The pinned [package configuration](https://github.com/Mapika/decider/blob/d6fc522aed7fc392576a9b66a330409bc6c382bd/pyproject.toml) declares Python 3.11 or later, PyTorch, Transformers, NumPy, Hugging Face Hub, Jinja2, and `flash-linear-attention`. Install Pillow explicitly for image inputs. The optional `metal` extra adds MLX on Apple Silicon.

The isolated [experiment environment](../../../experiments/mapika_vision.py) installed successfully with its declared dependencies, including `flash-linear-attention`. No dependency overrides or optional MLX package were needed. The observed inference path used PyTorch MPS, not CUDA kernels.

The [MPS implementation](https://github.com/Mapika/decider/blob/d6fc522aed7fc392576a9b66a330409bc6c382bd/decider/mps_ops.py) requires Transformers 5.17 or later for its optimized Qwen3.5 patch, despite the broader package requirement of Transformers 5 or later. It can use an optional MLX Metal kernel and otherwise falls back to PyTorch MPS operations. Record the resolved versions and actual path used during tests.

## Inference interface

The pinned [vision implementation](https://github.com/Mapika/decider/blob/d6fc522aed7fc392576a9b66a330409bc6c382bd/decider/vision/model.py) accepts a PIL image, NumPy image array, or encoded image bytes, paired with an `Example`. An `Example` supplies text context and a list of `Q` objects. Each question has text, ordered answer options, and a gold-label index used for training bookkeeping. A placeholder index does not select the inference answer.

This minimal recipe follows that interface. `snapshot_path` and `image` must already refer to the downloaded model and an RGB image:

```python
import torch
from decider.infer import Example, Q
from decider.vision import VisionDecisionModel

device = "mps" if torch.backends.mps.is_available() else "cpu"
dtype = torch.float16 if device == "mps" else torch.float32
model = VisionDecisionModel(
    snapshot_path, dtype=dtype, grad_ckpt=False
).to(device).eval()
options = ["thumb up", "open palm", "another pose", "no visible hand"]
example = Example(
    "Describe the visible hand pose. Do not infer a command or intent.",
    [Q("Which hand pose is visible?", options, 0)],
)
inputs = model.prepare([(image, example)])
with torch.inference_mode():
    probabilities = torch.softmax(model.slot_logits(inputs), dim=-1)
scores = probabilities[0, :len(options)].cpu().tolist()
```

Pass the dtype explicitly. The vision constructor otherwise chooses float16 whenever MPS is available, or bfloat16 otherwise. That default differs from the text API's float32 CPU default. `slot_logits` applies the MPS patch when its model buffers are on MPS. It returns one row per question and masks unused option columns before softmax. It does not return the richer text API's typed response or apply an application abstention threshold.

The [model card](https://huggingface.co/Mapika/decider-2b-vision/blob/863e290863655f1d6b69324d77d09ac972d21609/README.md) identifies approximately 4.1 GB of BF16 weights under Apache-2.0. The vision model retains v5 text weights; newer text-family calibration and interface claims do not automatically apply. The example probabilities are model scores, not evidence of command intent or calibration on SecondHands gestures. Measure image preprocessing, synchronized inference, and total request latency separately.

## Verified Mac execution

The inspected reports are `artifacts/results/mapika-hand.json` and `artifacts/results/mapika-face.json`; these generated files stay outside Git. Both used Python 3.12.9, PyTorch 2.14.1, Transformers 5.20.1, and float16 on Apple MPS. The reported `mapika_mps_patch` value was `true`.

The model weight file is approximately 4.426 GB in decimal units, consistent with approximately 4.1 GiB. The download was completed using checked parallel HTTP ranges and verified against SHA-256 `ac99c16652524d0c6a8017c987efb8aeaca5050f0bf3c7a3d92b927a57ec17ec`. The normal `just download-mapika` command then completed successfully against the cache. From the repository root, use `just test-mapika` for the public hand examples or `just recognize-mapika path/to/image.jpg` for another local image. The [root justfile](../../../justfile) owns these commands.

The tests used the public MediaPipe [portrait](https://storage.googleapis.com/mediapipe-assets/portrait.jpg) and [thumb-up](https://storage.googleapis.com/mediapipe-assets/thumb_up.jpg) images. Each image had one first request and three measured warm requests.

The hand question was “Which visible hand gesture is present?” Choices were `thumbs up`, `open palm`, `closed fist`, `other hand pose`, and `no visible hand`:

- On `thumb_up.jpg`, Mapika selected `thumbs up`, with score 0.9860 and warm median 182.77 ms.
- On `portrait.jpg`, it selected `open palm`, with score 0.4055 and warm median 661.96 ms. The portrait contains resting hands; this choice does not establish an intended command.

The face question was “Which visible facial movement is present?” Choices were `smiling`, `mouth open`, `neutral expression`, and `no visible face`:

- On `portrait.jpg`, Mapika correctly selected `smiling`, with score 0.9586 and warm median 660.03 ms.
- On the negative face example `thumb_up.jpg`, it correctly selected `no visible face`, with score 0.8955 and warm median 181.05 ms.

All repeated outputs within each image/question combination were identical. Model loading took 16.54 seconds in the hand run and 3.15 seconds in the later face run; these are separate observations, not stable startup estimates. Peak process RSS was 9,021.86 MiB and 8,984.59 MiB respectively. RSS does not measure total MPS allocation or predict Snapdragon memory needs.

Request timings include preprocessing, inference, output decoding, and device synchronization. They exclude image-file reading and model loading. Image-dependent timings differ substantially here; these two examples do not establish general latency or accuracy. Successful face absence on one negative example does not validate command intent, calibration, live streams, or use with a new person. CPU execution remains an available source-level fallback with explicit float32, but was not measured in these runs.
