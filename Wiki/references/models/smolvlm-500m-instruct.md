# SmolVLM-500M-Instruct

**Status:** Installed and run on the Mac through PyTorch MPS on 2026-10-17. Static-image execution is verified; recognition accuracy and an ExecuTorch port are not. It remains the advanced ExecuTorch candidate in the [recommended order](index.md#recommended-starting-order).

## Capability and role

The [upstream Qualcomm ExecuTorch guide](https://github.com/pytorch/executorch/blob/main/examples/qualcomm/oss_scripts/llama/README.md) documents SmolVLM 500M as a vision-language model with a vision encoder and a generative language decoder. The model identity is [HuggingFaceTB/SmolVLM-500M-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct). The recipe was checked in this repository conversation on 2026-10-16; its commands use Android deployment.

Investigate it as a possible useful vision-language component inside ExecuTorch. It is not a native typed decision model. Configurable decision scoring would require additional work; generating a description is not the same interface as directly scoring supplied choices.

## First investigation and limits

Confirm the export/runtime versions and Windows target path before attempting deployment. If that path works, compare representative image outputs and measure latency and memory using the [shared measurements](../../experiments-before-saturday.md#measurements). SH-T-017 in the [task plan](../../plan.md#optional-experiments) owns this investigation.

The published Qualcomm recipe is not an attendee-ready Windows ARM64 package. No Windows export, NPU execution, or SecondHands gesture accuracy has been verified. A Qualcomm AI Hub listing or a successful run through another runtime would not establish ExecuTorch compatibility.

## Verified Mac execution

The [experiment script](../../../experiments/smolvlm.py) uses its own locked environment: Python 3.12.9, PyTorch 2.14.1, Transformers 4.57.6, and float32 on Apple MPS. The model revision is [`a7da5b986cb59b408707209984f360a5f4ad7e47`](https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct/tree/a7da5b986cb59b408707209984f360a5f4ad7e47). The model card lists Apache-2.0. Use `just download-smolvlm`, then `just test-smolvlm`; [the runbook](../../runbooks/mac-and-snapdragon-development.md#run-the-other-three-image-models) also explains custom images and questions.

The local test disables image splitting and sets the longest image edge to 512 pixels. It uses greedy generation with at most 32 new tokens. These settings reduce work compared with larger or split-image processing; they are part of the experiment configuration, not a claim about the model's default accuracy.

The same two public MediaPipe images were used for hand and face questions, with one initial request and three measured repeat requests per image. The hand choices were `thumbs up`, `open palm`, `closed fist`, `other hand pose`, and `no visible hand`. The face choices were `smiling`, `mouth open`, `neutral expression`, and `no visible face`.

| Input and question | Generated text | Warm median |
| --- | --- | --- |
| Portrait, hand | `Other hand pose.` | 134.03 ms |
| Thumb-up, hand | `Thumbs up.` | 123.60 ms |
| Portrait, face | `Smiling.` | 113.05 ms |
| Thumb-up, face | `Neutral expression.` | 107.51 ms |

The last answer is wrong: the thumb-up image has no visible face. The model did not reliably choose the absence option. All repeat outputs for each image/question pair were identical. This small result set establishes execution and exposes a failure; it does not establish accuracy or safe command activation.

The first hand run took 17.82 seconds to load; the later face process took 2.49 seconds. Peak process RSS was about 3,268–3,303 MiB. File caching and first-use initialization can affect loading time. RSS is not total GPU or system memory. Synchronized request timings include preprocessing, inference, and decoding; they exclude image reading and model loading.

The JSON reports remain under ignored `artifacts/results/smolvlm-hand.json` and `smolvlm-face.json`. The script preserves generated text and records an exact choice only when the text matches a supplied option after case and final-period normalization. It does not produce option probabilities or constrain generation to the choice list. This CLI is not connected to the live dashboard and does not run through ExecuTorch.
