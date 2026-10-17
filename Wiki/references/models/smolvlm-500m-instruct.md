# SmolVLM-500M-Instruct

**Status:** Starting candidate for an advanced ExecuTorch investigation in the [recommended order](index.md#recommended-starting-order), recorded at the user's request on 2026-10-16. Not installed, exported, or evaluated in SecondHands.

## Capability and role

The [upstream Qualcomm ExecuTorch guide](https://github.com/pytorch/executorch/blob/main/examples/qualcomm/oss_scripts/llama/README.md) documents SmolVLM 500M as a vision-language model with a vision encoder and a generative language decoder. The model identity is [HuggingFaceTB/SmolVLM-500M-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct). The recipe was checked in this repository conversation on 2026-10-16; its commands use Android deployment.

Investigate it as a possible useful vision-language component inside ExecuTorch. It is not a native typed decision model. Configurable decision scoring would require additional work; generating a description is not the same interface as directly scoring supplied choices.

## First investigation and limits

Confirm the export/runtime versions and Windows target path before attempting deployment. If that path works, compare representative image outputs and measure latency and memory using the [shared measurements](../../experiments-before-saturday.md#measurements). SH-T-017 in the [task plan](../../plan.md#optional-experiments) owns this investigation.

The published Qualcomm recipe is not an attendee-ready Windows ARM64 package. No Windows export, NPU execution, or SecondHands gesture accuracy has been verified. A Qualcomm AI Hub listing or a successful run through another runtime would not establish ExecuTorch compatibility.
