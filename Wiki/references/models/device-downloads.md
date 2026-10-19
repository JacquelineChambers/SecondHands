# Model files on the Snapdragon device

On 2026-10-17, the user requested downloads of every candidate in [the model index](index.md), explicitly including the additional research candidates and Clef-Flash. The files are stored locally under ignored `artifacts/`. The user-approved [recorded experiment archive](../../../recordings/2026-10-17_18/README.md) now includes download manifests and source metadata; the model weights remain local. Downloading a candidate does not select it for the application or establish Windows, ExecuTorch, or NPU execution.

The selected downloads completed on 2026-10-17: **198 Hugging Face files totaling 43,949,059,278 bytes**, all checked against their pinned host hashes, plus **20 direct-download files** and the two existing checksum-verified MediaPipe task bundles. The final Hugging Face report contains zero failures. The table below identifies the selected checkpoint for every released candidate. The organizer's unpublished DeepLab `.pte` and the proposed, untrained custom classifier are the explicit exceptions; there is no published artifact for either in the inspected references.

## Storage and reproducibility

Hugging Face checkpoints use `artifacts/huggingface/hub/models--OWNER--NAME/snapshots/REVISION/`, matching the existing experiment cache. The five primary models retain the repository's pinned revisions and Google bundle versions. Additional releases are pinned to the commit returned by the model host during this download. Adapter-only candidates include their required base checkpoints.

The local inventory and verification records are under `artifacts/model-downloads/`: `huggingface-files.json`, `direct-files.json`, and the saved model-host metadata. They record source URLs, revisions, sizes, hashes, and completion or failure status. Hugging Face files are checked against the host's SHA-256 or Git blob hash; the two original MediaPipe bundles are checked against the repository's SHA-256 pins. The Qualcomm MediaPipe source weights also matched the pinned Git object hashes. Other direct downloads use published checksum prefixes or S3 checksums where available; files without a published full checksum have their downloaded SHA-256 and size recorded. Those verification levels are distinct.

Downloads are resumable and retain partial files until complete. Alternate quantizations and duplicate ONNX exports are omitted where a complete source checkpoint is already selected. These are downloads of each listed model, not every export format or historical version.

## Candidate inventory

| Reference candidate | Selected files and local location |
| --- | --- |
| MediaPipe Face Landmarker | Version 1 `artifacts/mediapipe/face_landmarker.task`; existing file verified. |
| MediaPipe Gesture Recognizer | Version 1 `artifacts/mediapipe/gesture_recognizer.task`; existing file verified. The alternate Qualcomm distribution's palm, hand-landmark, gesture-embedding, and classification weights are also downloaded below. |
| Laya Vision 201M | `thaitea/laya-vision-201m`, revision `0b6228f7a0762566de1c4539e9aa4eb1c1aef5f4`, in the Hugging Face cache. |
| Mapika Decider 2B Vision | `Mapika/decider-2b-vision`, revision `863e290863655f1d6b69324d77d09ac972d21609`, in the Hugging Face cache. |
| SmolVLM-500M-Instruct | `HuggingFaceTB/SmolVLM-500M-Instruct`, revision `a7da5b986cb59b408707209984f360a5f4ad7e47`, in the Hugging Face cache. |
| DeepLabV3 | PyTorch's [ResNet50 segmentation checkpoint](https://github.com/pytorch/vision/blob/main/torchvision/models/segmentation/deeplabv3.py), `artifacts/models/deeplabv3/deeplabv3_resnet50_coco-cd0a2569.pth`. This is source-model availability; the organizer's `dlv3_qnn.pte` is a separate missing artifact. |
| MobileCLIP2-S0 | `apple/MobileCLIP2-S0`, revision `3136ea51c8ed56b9f9abfab04cb816735aaad6cb`, including its weight license. |
| Clef-Flash 9B | `Cloudflare/clef-flash`, revision `8b2e5fd17c09fd49bc2880b805d5323ec7ff4ff3`, including all four model shards and the joint head. |
| InternVL3-1B | `OpenGVLab/InternVL3-1B`, revision `4415a3b810e636d11dfa86b0e9ba40bb00535aa8`. |
| Vision-Jev 0.8B | `LMDHQ-0420/vision-jev`, revision `b42c2f29eb6572f4a2ee31bd99d85d45ae8510c7`, selecting `vision-jev-0.8b/`; includes `Qwen/Qwen3.5-0.8B` at `2fc06364715b967f1860aea9cf38778875588b17`. The unrelated 9B variant is not the indexed candidate. |
| JEVision 0.8B | `divyanshx11/JEVision`, revision `e1cfde19bfae6548a46812c64a9a6f1a67459c95`, including adapters, heads, and bundled runtime files; includes its manifest-pinned `Qwen/Qwen3.5-0.8B-Base` at `dc7cdfe2ee4154fa7e30f5b51ca41bfa40174e68`. |
| SelfJev-4B Vision | `Jwuthrich/selfjev-4b-vision`, revision `96870c2253e64b7e5f2a4472ad49603643453cb2`; includes `Qwen/Qwen3.5-4B` at `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`. |
| Laya 421M | Root checkpoint of `convaiinnovations/laya`, revision `7b928d828b7b0e022f929d9bd2e44165aa270148`. |
| Laya multilingual 322M | `convaiinnovations/laya-multilingual`, revision `1720e3e3357cfe1e281542e223f8273b0890ca34`. |
| MediaPipe Pose Estimation | Google's version 1 `artifacts/mediapipe/pose_landmarker_full.task`, plus the [Qualcomm-referenced source repository](https://github.com/zmurez/MediaPipePyTorch/tree/65f2549ba35cd61dfd29f402f6c21882a32fabb1) pose detector, landmark weights, and anchors under `artifacts/models/mediapipe-pytorch/`. |
| MediaPipe Face Detection | Google's version 1 `artifacts/mediapipe/blaze_face_short_range.tflite`, plus Qualcomm-referenced face detector, landmark weights, and anchors under `artifacts/models/mediapipe-pytorch/`. These are distinct from the Face Landmarker task bundle. |
| PoseNet MobileNet | Qualcomm's [default source checkpoint](https://github.com/qualcomm/ai-hub-models/blob/main/src/qai_hub_models/models/posenet_mobilenet/model.py), `artifacts/models/posenet-mobilenet/mobilenet_v1_101.pth`. |
| MobileNetV2 | Qualcomm's [default source checkpoint](https://github.com/qualcomm/ai-hub-models/blob/main/src/qai_hub_models/models/mobilenet_v2/model.py), `artifacts/models/mobilenet-v2/mobilenet_v2.pth.tar`. |
| MobileNetV3-Small | [Torchvision ImageNet V1 weights](https://github.com/pytorch/vision/blob/main/torchvision/models/mobilenetv3.py), `artifacts/models/mobilenet-v3-small/mobilenet_v3_small-047dcff4.pth`. |
| HSEmotion EfficientNet-B0 | The three B0 releases referenced by the [HSEmotion loader](https://github.com/av-savchenko/hsemotion/blob/main/hsemotion/facial_emotions.py): `enet_b0_8_best_vgaf.pt`, `enet_b0_8_best_afew.pt`, and `enet_b0_8_va_mtl.pt`, under `artifacts/models/hsemotion-efficientnet-b0/`. The original upstream repository redirects to EmotiEffLib; the source URLs are retained in the local manifest. |
| SigLIP2 | Qualcomm's [default model identity](https://github.com/qualcomm/ai-hub-models/blob/main/src/qai_hub_models/models/siglip2/model.py), `google/siglip2-base-patch16-224`, revision `75de2d55ec2d0b4efc50b3e9ad70dba96a7b2fa2`. |
| MediaPipe landmarks with a small classifier | A proposed model to train, with no released checkpoint to download. The index retains it as a design candidate. |

The additional Qualcomm hand-gesture weights are under `artifacts/models/mediapipe-hand-gesture/`; palm detection weights and anchors share `artifacts/models/mediapipe-pytorch/`. Source selection follows [Qualcomm's implementation](https://github.com/qualcomm/ai-hub-models/blob/main/src/qai_hub_models/models/mediapipe_hand_gesture/model.py). No downloaded Python model code was executed during the download checks.

## Additional local model locations

The SSH access inspection on 2026-10-17 found more model bundles outside the three main download stores. The local, Git-ignored `artifacts/model-locations.txt` lists the exact paths, including folders in the PC owner's other projects and caches. The public inventory keeps those personal paths outside Git. [The SSH runbook](../../runbooks/tailscale-and-ssh.md#read-model-files-from-a-separate-windows-account) owns the granted permissions and verification limits.

| Location category | Observed model files |
| --- | --- |
| `artifacts/orbbec-face-npu/model/` | Quantized ONNX face detector and landmark detector, with their external weight data. |
| `artifacts/orbbec-selfie-npu/model/` | Quantized ONNX selfie segmentation model and its external weight data. |
| `artifacts/qnn/gesture/` and `artifacts/qnn/repro/` | A compiled `gesture_qnn.pte` in each directory. |
| GenieX cache outside the checkout | Qualcomm Qwen3-0.6B, Qwen3-4B, and Qwen3-4B-Instruct-2507 binary bundles, plus a Qwen3-0.6B GGUF. |
| Other local NPU project model folders | TinyLlama ONNX, Llama 3.2 3B ONNX/QNN, Qwen2.5 1.5B and 7B ONNX/QNN, a Qwen3 1.7B ExecuTorch bundle, and two local copies of a Gemma4 E2B ExecuTorch bundle. |
| External camera SDK sample | A YOLOv5s ONNX model. |

This inspection covered the owner's project directories and model caches plus local application staging directories. It excluded dependency test fixtures and application data unrelated to model development. File names and directory contents establish local presence; this inspection did not validate model outputs, bundle completeness, or runtime compatibility.

## Execution limits

The two primary MediaPipe tasks and the alternate Qualcomm gesture network have been exercised against the Orbbec camera in this device setup. [The live recognition record](../../setup/orbbec-mediapipe.md) owns the CPU baseline and the working ExecuTorch/QNN gesture classifier, including its native build, numerical comparison, clean shutdown, and remaining CPU facial/landmark stages. A later user-requested [JEVision camera experiment](../../setup/jevvision-orbbec.md) verified image inference through the prepared local CPU service and opened an interactive Orbbec preview. These specific execution records do not establish runtime compatibility for the remaining downloaded candidates.

The [Compute artifact inventory](https://github.com/aaishikasb/qc-executorch-guide/blob/main/Compute/artifacts/README.md) does not publish the organizer's DeepLabV3 `.pte` bundle. No copy was found in the inspected local locations. The downloaded PyTorch weights do not substitute for that compiled model or its matching runtime. Model selection, participant accuracy, and deployment compatibility remain separate tasks in [the plan](../../plan.md).
