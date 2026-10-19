# JEVision with the Orbbec camera

Saved reports and logs from this experiment are available in the user-approved [recorded experiment archive](../../recordings/2026-10-17_18/README.md). Runtime output still goes to the ignored local `artifacts/` directory.

On 2026-10-17, the user requested a JEV vision model with the Orbbec camera. The local experiment uses **JEVision 0.8B from `divyanshx11/JEVision`**, which is already loaded in the laptop's local service, and the existing Femto Bolt RGB bridge. This is distinct from the separately downloaded Vision-Jev model. Model identity and pinned downloads are maintained in [the device inventory](../references/models/device-downloads.md).

JEVision runs through PyTorch on the **ARM64 CPU**. This experiment does not use the NPU gesture classifier from [the MediaPipe preview](orbbec-mediapipe.md). The camera client uses the prepared x64 vision environment and sends resized camera images only to the loopback JEVision service at `http://127.0.0.1:8009`.

## Start and stop

On the prepared laptop, keep the existing JEVision service running. If it has stopped, start it from the repository root:

```powershell
.\artifacts\qnn\python-arm64\python.exe -u -B .\artifacts\jevvision-run\launch.py
```

This local launcher and its dependencies are prepared artifacts, not a fresh-machine installation procedure. It loads the image and text adapters with the pinned Qwen3.5-0.8B-Base checkpoint, float32 CPU inference, six PyTorch threads, and offline model loading. Confirm the service reports an image adapter:

```powershell
Invoke-RestMethod http://127.0.0.1:8009/v1/models
```

Then run [the camera experiment](../../experiments/jevvision_orbbec.py) from the repository root in another terminal:

```powershell
.\.venv\Scripts\python.exe .\experiments\jevvision_orbbec.py
```

The bridge defaults to the operator's prepared Documents installation. Use `--bridge-directory` to specify another installation. The preview is titled **JEVision + Orbbec (q to stop)**. Press **q** or close that window to release the camera; a model request already in progress may finish before the client process exits. The separate JEVision service remains running.

The left pane shows the live Orbbec frame. The right pane shows the frame associated with the last completed classification, its age, the selected description, and the model's probability. Only one request is in flight; the next request samples a fresh frame after completion. Camera frames are resized to a maximum side of 384 pixels for the request. Images and landmarks are not saved. Console output contains decision summaries and timings.

The initial choices compare an open palm, thumbs-up, closed fist, pointing finger, victory sign, and no clear hand gesture. These are experiment prompts based on the preceding gesture demo, not approved control commands. Customize them with `--question` and repeated `--choice` arguments. For example:

```powershell
.\.venv\Scripts\python.exe .\experiments\jevvision_orbbec.py --question "Which description matches the scene?" --choice "A person is visible." --choice "No person is visible."
```

## Observed verification

The live camera single-frame check completed successfully on 2026-10-17. JEVision selected **No clear hand gesture is visible** with probability **0.80**, using 190 input tokens and **9.05 seconds** of server-reported inference. The report at ignored `artifacts/jevvision-run/camera-smoke.json` contains the result and timing without the source image. This is execution evidence, not a validated classification.

The interactive preview then opened and remained responsive while classifying further Orbbec frames. Its first completed request selected the same description with probability 0.96 and took **20.56 seconds**. The result's source image is shown separately because inference takes much longer than the live preview's frame interval. These observations do not establish accuracy, calibrated probabilities, sustained throughput, or real-time control suitability.

Focused Ruff checks passed for the camera script. The single-frame request and the interactive request exercised the real camera, JPEG encoding, local visual route, choice/probability validation, and result display. The local launch record is `artifacts/jevvision-run/active-camera.json`, with timestamped stdout/stderr logs under the same ignored directory. A saved launch record does not establish that a process is still running.

To repeat the single-frame check without opening the preview:

```powershell
.\.venv\Scripts\python.exe .\experiments\jevvision_orbbec.py --once --report artifacts/jevvision-run/camera-smoke.json
```

[SH-T-051](../plan.md#snapdragon-deployment) tracks this standalone execution task. The subsequent [scene application](scene-understanding.md) integrates JEVision with live MediaPipe and object detections in a separate dashboard mode. Model selection, comparative accuracy, trigger-policy integration, and an NPU port remain separate work.
