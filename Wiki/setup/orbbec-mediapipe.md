# Orbbec face and hand recognition on the Snapdragon PC

Saved reports, export metadata, model inputs/outputs, profiles, and runtime logs are available in the user-approved [recorded experiment archive](../../recordings/2026-10-17_18/README.md). Runtime models and installed dependencies remain local.

On 2026-10-17, the user requested MediaPipe face and hand-gesture recognition from Orbbec, with ExecuTorch using the Snapdragon NPU. A local sample now combines **MediaPipe face/hand landmarks on the CPU with gesture classification through ExecuTorch/QNN on the NPU**. The native worker completed real-image and live-camera checks with clean shutdown. Face detection, face blendshapes, hand detection, and hand landmarks still use the CPU. [The plan](../plan.md#snapdragon-deployment) tracks that remaining scope.

The Orbbec was reconnected for a later run on 2026-10-17. The final code, with redundant CPU gesture classification removed, completed a 30-frame live check and the interactive NPU gesture preview was started successfully.

The later [depth viewer with NPU gestures](ms-09-femto-bolt-bridge.md#depth-viewer-with-npu-gestures) reuses this native classifier alongside measured depth and CPU MediaPipe landmarks. That owner maintains its launch command, visible runtime labels, and combined-stream verification.

## Live capture and recognition

The [capture adapter](../../src/secondhands/capture/orbbec.py) uses the separately installed [Femto Bolt bridge](ms-09-femto-bolt-bridge.md) and its 1280 × 720 MJPEG color stream at 15 FPS. This requires RGB only; it does not start depth capture or change calibration. The bridge and MediaPipe initialize incompatible Windows COM threading modes, so bridge creation, reads, and cleanup run on a dedicated thread. The adapter retains only the newest frame and propagates camera errors.

The [recognition CLI](../../src/secondhands/recognition/__main__.py) supports the original MediaPipe CPU pipeline and the new `executorch-qnn` gesture backend. The latter extracts the hand-landmark subtask from the existing checksum-pinned Gesture Recognizer bundle, without running its CPU gesture classifier. [The worker client](../../src/secondhands/recognition/qnn_gesture.py) normalizes landmarks and sends them to a persistent native ARM64 ExecuTorch process. The preview draws landmarks, skeletons, and categories, and labels the CPU/NPU split. Native errors fail the request; there is no gesture CPU fallback.

`--quiet` suppresses per-frame JSON. The preview writes runtime diagnostics but no camera recording. This integration is exposed through the CLI; the dashboard's camera-index interface is unchanged.

## Start and stop

Connect the Femto Bolt and close other applications using its color stream. From the repository root in PowerShell:

```powershell
.\experiments\start-orbbec-preview.ps1 -GestureBackend executorch-qnn
```

The [launcher](../../experiments/start-orbbec-preview.ps1) uses the prepared `.venv`, native runtime, and installed bridge under the operator's Documents folder. Pass `-BridgeDirectory "D:\camera-bridge"` for another bridge location. Press **q** to stop. The default limit is 54,000 processed frames; `-MaxFrames 60` gives a short check. Omit `-GestureBackend` for the original CPU baseline. No elevated privileges are needed.

These commands use dependencies already prepared on this laptop. A fresh checkout also needs the external bridge, models, SDK, native Python environment, and built worker.

## Observed checks

All observations below were made on 2026-10-17. They establish execution, not participant accuracy or a whole-pipeline speedup.

| Check | Observation and limit |
| --- | --- |
| Original CPU camera smoke | 30 frames; faces in 20, hands in 15, including one `Thumb_Up`. Median combined face/hand task time 52.67 ms; total 5.95 seconds including startup and capture. A later 60-frame run and preview also completed. |
| Native gesture worker | 25 calls on landmarks from Qualcomm's public `thumbs_up.jpg`; exit 0; `Thumb_Up`; maximum absolute probability difference from native PyTorch 0.00650. Median warm model-call time 0.05325 ms measures the small gesture network, not capture or landmarks. |
| Live hybrid camera smoke | 90 frames; faces and hands in all 90; exit 0; median accumulated gesture model-call time 0.23965 ms per frame. This run also calculated the original CPU gesture result for comparison, then used the NPU result. |
| Final landmark-only CPU path | A fresh export from the checked-in script passed 30 repeated public-image frames in MediaPipe VIDEO mode: hands and `Thumb_Up` in all 30, no CPU gesture classification, native exit 0. Median accumulated NPU call time 0.3053 ms. A repeated static image does not test motion tracking. |
| Earlier final camera rerun | Failed before capturing a frame: `Expected one connected Femto Bolt color camera; found 0`. Windows also listed no connected Orbbec camera. The later reconnected check below resolves this missing live verification. |
| Reconnected final pipeline | 30 live frames, one hand classified by the NPU in every frame, exit 0, and no redundant CPU gesture result. Median gesture model-call time was 0.30835 ms. All classifications were `None`; this confirms execution, not successful recognition of a named gesture. The preview then opened with a responsive window and a native worker loading `QnnHtp.dll` and `QnnHtpV73Stub.dll`. |
| Code checks | **53 tests passed, one optional test skipped**; focused Ruff checks passed; the checked-in native build script completed successfully. Tests cover capture ownership/cleanup, normalization, fragmented native responses, invalid results, and landmark-only results. |

The running worker loaded `QnnHtp.dll`, `QnnHtpV73Stub.dll`, and the laptop's DSP transport driver. The exported gesture graph contains one QNN delegate and no CPU neural-compute nodes. This evidence applies to that graph, not the surrounding MediaPipe tasks. Event tracing/ETDump is disabled; this is not a full hardware profiling report.

Local reports include `artifacts/orbbec-mediapipe/cpu-smoke.json`, `artifacts/qnn/gesture/stream-smoke.json`, and `artifacts/qnn/repro/public-video-smoke.json`. `artifacts/qnn/gesture/camera-smoke.json` contains the earlier missing-camera result, replacing the original successful report. The original 90-frame result was observed in the task output. The later successful 30-frame check is preserved separately in `artifacts/qnn/gesture/reconnected-camera-smoke.json`; it contains aggregate counts, runtime labels, and timing without camera images or landmarks. `artifacts/qnn/gesture/active-preview.json` records that preview launch and its diagnostic log paths; a launch record does not establish that the process is still running. Weights, logs, reports, and public sample images remain under ignored `artifacts/`. No personal imagery or calibration is added to Git.

## ExecuTorch and NPU prerequisites

MediaPipe `.task` bundles use MediaPipe/TensorFlow Lite; they are not ExecuTorch `.pte` files. [The runtime design](../design/runtime-stack.md) explains that boundary. The [official Windows QNN workflow](https://docs.pytorch.org/executorch/1.5/backends-qualcomm.html) uses an x64 export host and native ARM64 deployment. This experiment instead built a native ARM64 QNN Python binding and successfully exported the selected gesture network on the laptop. It does not establish Windows ARM64 support for every export dependency or model.

The prepared toolchain includes:

- ExecuTorch **1.5.1**, source commit `3b60683923245cf472b7323426920e15623ba361`, with the Qualcomm CMake binding condition extended to Windows ARM64.
- Qualcomm QAIRT/QNN **2.37.0.250724**, matching Windows ARM64 libraries and Hexagon v73 DSP libraries. The public SDK download accepted ranged GET requests despite HEAD returning HTTP 403.
- Native ARM64 CPython **3.12.10**, PyTorch **2.14.1+cpu** from the [official CPU wheel index](https://download.pytorch.org/whl/cpu/torch/), and ExecuTorch Python export files with a locally built native QNN binding. The x64 wheel's compiled Python modules are excluded from this native environment.
- Microsoft MSVC **14.50.35717**, Windows SDK **10.0.26100.0**, Python development headers/import library, CMake, Ninja, and ARM64 Microsoft C++ runtime libraries.

The MediaPipe application uses x64 CPython 3.12.15 under Windows ARM64 emulation. It communicates with the native ARM64 worker over binary pipes; it does not load ARM64 DLLs into the x64 process.

## Gesture model and rebuild

The pretrained gesture embedder and classifier come from [Qualcomm AI Hub Models at the pinned revision](https://github.com/qualcomm/ai-hub-models/blob/70b5aeeec774d188465cac561d07cac0d022ce29/src/qai_hub_models/models/mediapipe_hand_gesture/model.py). [The inventory](../references/models/device-downloads.md) records the weights. The combined **370,304-byte FP16** model targets `SC8380XP` and returns eight probabilities. Pixel scaling, centering, normalization, and original/mirrored landmark preprocessing remain in Python. All neural checkpoint keys load strictly; two fixed preprocessing constants are checked separately.

The [export script](../../experiments/executorch-qnn/export_gesture.py) verifies the upstream source hash, extracts neural methods without the full AI Hub dependency stack, records weight hashes/versions, and requires one QNN delegate with no remaining CPU neural computation. The [C++ worker](../../experiments/executorch-qnn/qnn_stream.cpp) loads the model once. The [build script](../../experiments/executorch-qnn/build.ps1) uses the prepared toolchain and stages matching DLLs beside it.

Stop this sample's preview before rebuilding. From the repository root:

```powershell
.\experiments\executorch-qnn\build.ps1
.\artifacts\qnn\python-arm64\python.exe .\experiments\executorch-qnn\export_gesture.py
```

The default output is `artifacts/qnn/gesture/gesture_qnn.pte`; `export.json` records source, hashes, precision, and delegation. These scripts rebuild from prepared dependencies; they are not a fresh-machine SDK installer.

An earlier supplied runner with QNN 2.45 wrote outputs but crashed during shutdown with `0xc0000409`. The matching ExecuTorch 1.5.1/QNN 2.37 source build resolved that failure in the native, public-image, and live-camera checks. A prior `0xc000007b` startup failure was resolved by staging ARM64 Microsoft runtime DLLs. Old logs remain local historical diagnostics.

The public thumbs-up sample produced the same category in the original MediaPipe bundle, downloaded PyTorch network, and NPU network, with different confidence scores. This single example does not establish full equivalence between model distributions.

## Camera sample search

The primary sources inspected on 2026-10-17 did not establish a ready-to-run upstream Windows camera application using ExecuTorch on the X Elite NPU. The [official Qualcomm backend tutorial](https://docs.pytorch.org/executorch/1.5/backends-qualcomm.html) supports Windows ARM64 and `SC8380XP`, with a DeepLab segmentation workflow requiring camera integration. The [Compute guide](https://github.com/aaishikasb/qc-executorch-guide/blob/main/Compute/README.md) likewise expects an installed model/runtime bundle and application integration; its author distinguishes documentation review from execution of the Windows/NPU workflow.

Arm's [YOLOv8s webcam example](https://learn.arm.com/courses/executorch-on-arm/optimize-image-classification/optional-yolov8s-object-detection/deploy-yolov8s-object-detector/) supplies a full ExecuTorch camera loop, but targets Raspberry Pi 5 with XNNPACK on the CPU. The local SecondHands sample supplies Orbbec integration and a verified gesture NPU path; it does not move the whole face/hand pipeline onto the NPU.

## Questions

### SH-Q-005 — Compatible face and gesture NPU export bundle

**Partially resolved factual prerequisite.** The user requested ExecuTorch on the Snapdragon NPU and asked us to obtain dependencies without an organizer bundle. The local build now supplies the gesture model and working native runtime. [The CLI](../../src/secondhands/recognition/__main__.py) retains CPU face/hand detection and landmarks. The remaining question is which compatible facial components can preserve the current landmarks and 52-blendshape interface on the NPU.

- **Use a supplied compatible face bundle.** Obtain the `.pte`, matching runtime, and preprocessing/output specification. Example: compare landmarks and blendshapes against Face Landmarker on public images before connecting the camera. No complete bundle has been found.
- **Extend the local export.** Export compatible facial components using the established compiler/runtime. Example: test the downloaded Qualcomm face network, then separately supply and verify the blendshape stage. Face-location or landmark output alone does not preserve the interface.

The original alternatives were a supplied face/gesture bundle or a local build. The observed local gesture build and final live rerun resolve that part only. Compare remaining paths by availability, reproducibility, output equivalence, and QNN delegation. [The deployment task](../plan.md#snapdragon-deployment) remains open for facial scope.
