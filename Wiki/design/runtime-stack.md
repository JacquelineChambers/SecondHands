# Runtime stack

**Status:** reviewed 2026-10-16 against the hackathon Compute guide, ExecuTorch 1.5 documentation, package metadata, and a Mac smoke run; updated 2026-10-17 with a [native QNN gesture component and Orbbec CLI integration](../setup/orbbec-mediapipe.md), then a separate [CPU scene dashboard](../setup/scene-understanding.md). Dashboard NPU integration and full facial NPU execution remain separate work. The user accepts mixed local runtimes for exploration. That does not resolve the organizers' [mixed-runtime acceptance question](../hackathon-compute.md#unresolved-event-details).

## Framework roles

The UI rows reflect the user-approved 2026-10-17 [React and Bun migration](../experiments-before-saturday.md#react-and-bun-migration-observations). It changes frontend tooling, not the Python inference runtimes.

| Component | SecondHands role |
| --- | --- |
| Python | Camera processing, model integration, experiments, and the implemented FastAPI dashboard service. |
| PyTorch | Define, load, train, and test compatible models; export their computation for deployment. |
| ExecuTorch | Execute an exported `.pte` model using the backend selected during export. |
| XNNPACK | ExecuTorch's optimized CPU backend; used for the first Mac check. |
| Qualcomm QAIRT/QNN HTP | ExecuTorch's route to the Snapdragon Hexagon NPU; used by the pretrained gesture classifier in the recognition CLI and optional [depth viewer mode](../setup/ms-09-femto-bolt-bridge.md#depth-viewer-with-npu-gestures). |
| MediaPipe | Face/hand detection and landmarks, CPU gesture categories, and body poses in the scene mode. The CLI can replace gesture classification with a separate exported Qualcomm network; MediaPipe's task runtime itself remains on the CPU. |
| OpenCV DNN | Runs the existing YOLOv5s ONNX object detector on the CPU in scene mode. |
| Local JEVision service | Processes sampled scene images through PyTorch on ARM64 CPU, separately from tracking. |
| React 19, TypeScript, Vite | The implemented local recognition dashboard, with a Vite proxy to the Python service. |
| Bun 1.4.3 | UI dependency installation and execution of Vite, TypeScript, and Vitest. Verified on the Mac; Dell execution remains untested. |

PyTorch is the model development framework; ExecuTorch is its on-device inference framework. We can use pretrained models without training them ourselves. The documented export and test workflow uses Python APIs, so the first Mac check needs no application C++ code. See [ExecuTorch getting started](https://docs.pytorch.org/executorch/1.5/getting-started.html).

## From a PyTorch model to ExecuTorch

The export path is: PyTorch model and example tensor inputs → `torch.export.export` → backend lowering → `.pte` file → ExecuTorch runtime. Lowering converts supported model operations into the chosen backend's implementation. Quantization, when used, reduces numerical precision and needs accuracy checks with representative data. Unsupported operations can require CPU fallback or changes to the model/export path. Export success alone is not an accuracy or latency result. See [model export and lowering](https://docs.pytorch.org/executorch/1.5/using-executorch-export.html).

A `.pte` is specialized for its backend. The Mac XNNPACK artifact is a CPU baseline; it does not become a Qualcomm NPU artifact when copied to Windows. QNN needs a separate compatible export and runtime. Keep the source, preprocessing specification, model identity, and validation observations shared, with generated artifacts under ignored `artifacts/`.

## Mac and Snapdragon execution

The [Compute guide](https://github.com/aaishikasb/qc-executorch-guide/blob/main/Compute/README.md) still specifies ExecuTorch **1.5.1**, QAIRT/QNN **2.37.0.250724**, Snapdragon X Elite **SC8380XP**, and Hexagon **HTP v73** on Windows 11 ARM64. It directs attendees to start with a supplied model/runtime bundle; custom export and source compilation are optional. The detailed event procedure remains in [the Compute summary](../hackathon-compute.md).

On the Mac, the checked path is Python → ExecuTorch 1.5.1 → XNNPACK → Apple Silicon CPU. [XNNPACK supports ARM64 macOS CPU execution](https://docs.pytorch.org/executorch/1.5/backends/xnnpack/xnnpack-overview.html). This check uses neither the Apple GPU nor Apple Neural Engine and cannot test Qualcomm NPU execution.

On the supplied PC, the documented accelerated path is Windows ARM64 application → ExecuTorch Qualcomm backend → QAIRT/QNN HTP → Hexagon NPU. The separate [Orbbec recognition record](../setup/orbbec-mediapipe.md) now verifies that path for a pretrained gesture classifier connected to the CLI. Face/hand landmarks still use MediaPipe on the CPU. The supplied DeepLabV3 segmentation demonstration remains a separate unexecuted task.

For custom QNN export, the guide uses Windows x64 Python under emulation, with native ARM64 deployment. The local gesture experiment instead uses isolated native ARM64 Python, an official PyTorch CPU wheel, and a source-built QNN binding; its [build record](../setup/orbbec-mediapipe.md#executorch-and-npu-prerequisites) owns that experimental environment. The root lockfile's [Windows dependency limit](../runbooks/mac-and-snapdragon-development.md#windows-arm64-compatibility-limit) remains separate. Neither the Mac environment nor its CPU `.pte` substitutes for a QNN export.

## Five candidate integrations

The additional [scene mode](../setup/scene-understanding.md) uses already-available Pose Landmarker, YOLOv5s, and JEVision assets alongside the face/hand baseline. Its live camera API is checked on the PC. This extends the experiment without replacing the five-candidate comparison or integrating a decision model into command triggers. The launcher prefers Bun and uses Node when Bun is unavailable, as observed on this laptop.

The [model reference index](../references/models/index.md#recommended-starting-order) owns the selected experiment order and model-specific sources. These candidates serve different roles:

| Candidate | First local role | Current SecondHands evidence |
| --- | --- | --- |
| MediaPipe Face Landmarker | Continuous facial movement measurements | Public images and live Orbbec CPU inference checked; facial NPU work remains open. |
| MediaPipe Gesture Recognizer | Continuous hand landmarks and static categories | CPU baseline checked; alternate pretrained gesture classifier also checked through ExecuTorch/QNN, with CPU hand landmarks. |
| Laya Vision 201M | Candidate-image questions with configurable choices | Pinned CLI runs on Mac MPS and CPU; static-image outputs and timings recorded. False face classification observed; not connected to dashboard. |
| Mapika Decider 2B Vision | Compare decision quality and cost against Laya | Pinned CLI runs on Mac MPS with its MPS patch active; static-image decisions and costs recorded. Not connected to dashboard. |
| SmolVLM-500M-Instruct | Vision-language experiment and advanced ExecuTorch investigation | Pinned CLI runs on Mac MPS; generated image answers and timings recorded. False face classification observed; no dashboard or ExecuTorch integration. |

“Five working” should mean reproducible loading, inspected output on relevant observations, and recorded runtime/version/latency limits for each candidate. It should not require all five to run on every frame or all five to use ExecuTorch. A documented compatibility failure is useful evidence but does not count as a working model. Native Mac execution can precede a separate ExecuTorch port.

A small trained PyTorch classifier over face/hand measurements is a proposed additional ExecuTorch route if full vision-model conversion proves difficult. It would provide a consequential command decision, but needs data, training, and held-out validation. The synthetic network used in the smoke check is not that trained classifier and is not a sixth working recognition candidate.

## Observed Mac ExecuTorch check

The [experiment record](../experiments-before-saturday.md#executorch-cpu-smoke-observation) owns the actual result. The standalone script has its own dependency lock and isolated environment, with ExecuTorch 1.5.1 matching the guide. It does not add ExecuTorch to the application's root dependency set. [The runbook](../runbooks/mac-and-snapdragon-development.md#run-the-executorch-cpu-smoke-check) owns its command and expected result.

The useful-component milestone is now met by the [CLI gesture classifier](../setup/orbbec-mediapipe.md#observed-checks), with numerical comparison and live execution evidence. The gesture dashboard still uses MediaPipe observations and deterministic [trigger logic](recognition-and-triggers.md#trigger-policy); neither dashboard mode uses the native worker. Connecting a selected decision model to command candidates and inspecting the new scene mode in a rendered browser remain open. Work status stays in [the task plan](../plan.md).
