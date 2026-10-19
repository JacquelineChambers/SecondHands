# K&F Concept MS-09 / Femto Bolt setup

On 2026-10-17, a local software bridge enabled real depth capture from the Orbbec Femto Bolt on the Snapdragon Windows laptop. A second application combined the color camera with depth to detect people and estimate their positions. Both ran on this computer, as the user requested. The initial verification passed; a later saved run ended in a capture timeout, so sustained reliability remains unresolved.

The equipment was initially called “K&F Concept MS-09.” K&F identifies [MS09 as a mini tripod/selfie stick](https://www.kfconcept.com/reviews_16194?page=2). Windows and the SDK identified the connected camera as **Orbbec Femto Bolt**, with separate RGB and depth interfaces. The software work concerned that camera. [The hardware page](../hardware/femto-bolt.md) owns camera selection and the broader compatibility investigation.

## Why a bridge was needed

The color image worked, but that did not establish that the depth sensor was delivering distances. Four diagnostic attempts using Orbbec SDK **1.10.37** and **2.10.6** produced no depth frames. The camera reported firmware **1.0.9** over **USB 3.1**; the host ran **Windows 11 Pro, version 10.0.26200, ARM64**. The initial HTML report recorded these failures:

```text
Can not find firmware data profile.
got nvram data failed.retrying...
DeviceComponentPtr is nullptr
```

Investigation found a capture-path mismatch: the normal Windows camera interfaces exposed the calibration stream as 1024 × 512 at 30 FPS, while initialization expected it at 5 FPS. The camera's USB descriptors advertised additional raw depth modes that those interfaces did not expose. Reading calibration succeeded, and direct access through the Windows Kernel Streaming proxy subsequently exposed usable raw modes. This supported a software capture-path explanation for the initial failure; the error messages alone did not prove defective hardware.

## What was built and why

| Work completed | Purpose |
| --- | --- |
| Added `direct_capture.py`, using DirectShow with an explicitly loaded Windows Kernel Streaming proxy | Bypass the Windows Frame Server route and select the camera's calibration and raw sensor streams directly. |
| Added `depth_engine.py`, using camera calibration and the vendor `depthengine_2_0.dll` from SDK 1.10.37 | Convert raw phase measurements into real depth in millimetres and an infrared image. The raw adapter follows the [Orbbec SDK v2 implementation](https://github.com/orbbec/OrbbecSDK_v2), with attribution retained locally. |
| Added `run_bridge.py`, launch/stop scripts, a browser viewer, and HTML/data exports | Make capture repeatable and inspectable without editing scripts for each test. |
| Downloaded and adapted [Orbbec's YOLO object-detection example](https://github.com/orbbec/pyorbbecsdk/tree/0f089c9bf6e618e7782228ee6bcf666e3339ae78/examples/applications/object_detection) | Test color and depth together by detecting people and attaching measured camera-relative positions. The upstream checkout is retained locally at this commit. |
| Added factory-calibrated RGB/depth alignment and timing checks | Associate a person's color-image box with the corresponding depth samples, and withhold positions when the image pair is too far apart in time. |

The bridge supports narrow-field-of-view (NFOV), unbinned **640 × 576 depth at 15 FPS**. Its x64 Python process and vendor depth engine run through Windows ARM64 emulation; native ARM64 capture was also tested separately. This is a local viewer/export prototype, not a general virtual-camera driver or a complete native ARM64 SDK. The setup records report no driver, firmware, registry, or persistent camera-calibration changes.

The person application uses YOLOv5s in ONNX Runtime's CPU path, with OpenCV, NumPy, and Pillow in a separate x64 Python environment. It captures 1280 × 720 RGB and resizes it to 640 × 360 for detection. SDK v2 reads factory calibration; the custom bridge captures frames and the SDK v1 depth engine decodes them. Positions use central bounding-box depth samples with outlier rejection, expressed in metres relative to the color camera: **X right, Y down, Z forward**. These are person-position estimates, not skeleton tracking or persistent identities.

RGB/depth pairing uses host arrival timestamps rather than hardware synchronization. Pairs more than **75 ms** apart do not receive measured positions. Processing runs more slowly than capture and intentionally skips intermediate frames. All inference and viewer services run locally, without a second computer or cloud inference.

## Recorded results

These are results from the earlier setup session and saved verification files, reviewed for this summary. Camera tests were not rerun while writing the documentation.

| Test | Saved result |
| --- | --- |
| Standard SDK capture | Four attempts; zero depth frames. |
| Depth bridge verification | **215 distinct frames**, 640 × 576, **15.05 FPS**, zero callback queue drops. |
| Depth coverage and decoding | Mean **49.72% valid depth pixels** in that scene; median decode time after warm-up **5.57 ms**. Coverage is not an accuracy score. |
| Person application verification | **400 processed frames**; 398 contained detected people and **397 contained people with measured depth**. |
| Person processing speed | **4.69 updates/second**; median model inference **113.77 ms**; zero depth/color queue drops during this verification. |
| Viewer and export checks | Start/stop, person-app capture restart, previews, HTML reports, and downloads passed. The bridge's 16-bit depth PNG matched its exported depth array. |

A later person-app snapshot saved at **13:29 local time on 2026-10-17** recorded 5,634 processed frames, including 5,563 with measured people, then the error `No sensor frame arrived within 8 seconds; check USB and camera power`. It also recorded 71 depth and 70 color queue drops. That snapshot does not establish the cause of the timeout. The earlier successful checks remain valid, but do not establish uninterrupted operation or recovery after unplugging or rebooting.

Absolute distance accuracy has **not** been checked against a measured target. Factory calibration and plausible coordinates demonstrate a working measurement pipeline; they do not establish measurement accuracy, person-detection accuracy, or demonstration readiness. The remaining capture investigation is tracked under [SH-Q-002](../hardware/femto-bolt.md#sh-q-002--which-capture-path-works-on-the-dell) and [the plan](../plan.md#optional-experiments).

## How to use the installed setup

The local installation is under the operator's Windows Documents folder. Keep these sibling directories in place; the person application depends on the bridge and its vendor libraries:

```text
Documents/
  Femto-Bolt-Depth-Test-2026-10-17/
    bridge/
      Start-Depth-Bridge.cmd
      depth-bridge-report.html
  Femto-Bolt-Person-Detection/
    Start-Person-Detection.cmd
    results/person-detection-report.html
```

- **Depth only:** Run `Start-Depth-Bridge.cmd`, open [the local depth viewer](http://127.0.0.1:8765/), and select **Start depth**. **Stop & save** writes the report and latest depth/infrared exports.
- **People and 3D positions:** Use the **Femto Bolt Person Detection** desktop shortcut or `Start-Person-Detection.cmd`. The [local person viewer](http://127.0.0.1:8766/) starts capture automatically. **Save test report** exports the results; **Stop camera** releases capture.
- **Camera ownership:** Close other camera applications. Use one depth-capture application at a time; starting the person application stops capture in the depth-only viewer. The matching `Stop-Depth-Bridge.ps1` and `Stop-Person-Detection.ps1` scripts stop their background servers.

Both viewers bind to `127.0.0.1`, so these addresses work on the setup computer while the corresponding server is running. Neither is configured to start with Windows. New saves replace the latest reports and exports.

### Depth viewer alongside SecondHands

The SecondHands API also uses port 8765. When it is running, start the depth viewer on port 8767 from PowerShell:

```powershell
$depthRoot = Join-Path $env:USERPROFILE 'Documents/Femto-Bolt-Depth-Test-2026-10-17'
& "$depthRoot\.venv\Scripts\python.exe" "$depthRoot\bridge\run_bridge.py" --serve --port 8767
```

Keep that terminal open, visit [the depth viewer on port 8767](http://127.0.0.1:8767/), and click **Start depth**. Stop the scene camera before starting depth capture. The viewer's **Stop & save** button releases capture and writes its existing local exports; Ctrl+C stops the viewer server.

For the user's subsequent launch request on 2026-10-17, Windows reported both Orbbec depth and RGB devices present with OK status. Automatic approval review initially rejected the depth-server launch. After the user repeated the request, the server started successfully on port 8767: the viewer returned HTTP 200 and its status endpoint reported idle with zero frames. The follow-up capture/browser command was rejected with “blocked by policy.” At that check, fresh depth capture remained unverified. The later 2,097-frame status observation below completes the capture portion of [SH-T-053](../plan.md#snapdragon-deployment); the earlier recorded depth results remain distinct.

### Depth with MediaPipe

On 2026-10-17, the user requested the Orbbec depth viewer with MediaPipe. [The combined viewer](../../experiments/orbbec_depth_mediapipe.py) now opens a local window with the color image and MediaPipe face/hand overlays on the left, and measured depth on the right. Stop capture in other camera applications before starting it. From the prepared SecondHands checkout:

```powershell
.\.venv\Scripts\python.exe experiments/orbbec_depth_mediapipe.py
```

The window title starts with **Orbbec depth + MediaPipe** and identifies the CPU or NPU gesture mode. Move the pointer over the depth pane to read that depth pixel's distance. The color scale covers 0.2–5.0 metres; black pixels have no valid return. Press **Q**, **Esc**, or close the window to release both streams. Use `--bridge-directory` for another prepared bridge installation and `--model-dir` for the two MediaPipe bundles.

The [depth capture adapter](../../src/secondhands/capture/orbbec_depth.py) reads calibration, starts the vendor depth engine, and decodes 640 × 576 depth on a dedicated worker thread. Its queue retains only the newest frame. A separate worker captures RGB, and MediaPipe analyses the displayed 640 × 360 color image on the CPU. The depth and color images have different coordinates and host arrival times; this viewer does not align them or assign measured 3D positions to hand landmarks. The depth age and decoding time are displayed. No calibration, camera images, or recordings are saved. Optional `--report` output contains aggregate counts and measurements only.

Observed verification: a **12-frame** run without a window completed with 12 changing depth-frame numbers, one detected face, up to two hands, and clean stream shutdown. The last frame had 46.71% valid depth pixels, 5.62 ms depth decoding, and 61.91 ms MediaPipe processing. A subsequent interactive launch created a responsive window and processed at least **150 frames**, with changing depth and face/hand results. Focused Ruff lint and formatting checks passed. These are execution observations; distance accuracy, recognition accuracy, pixel alignment, and long-duration reliability remain unvalidated. The aggregate check and launch logs are under ignored `artifacts/scene-understanding/`.

Before launching this combined viewer, the earlier browser depth viewer's status endpoint reported **stopped with 2,097 captured frames**. This establishes that capture occurred after its earlier idle check, without claiming automated browser inspection. [SH-T-053 and SH-T-054](../plan.md#snapdragon-deployment) record the launch outcomes.

### Depth viewer with NPU gestures

The user's next request on 2026-10-17 adds NPU use to the same viewer. Launch the prepared native gesture classifier with:

```powershell
.\.venv\Scripts\python.exe experiments/orbbec_depth_mediapipe.py --gesture-backend executorch-qnn
```

The window title includes **NPU gestures**, and the left pane identifies **ExecuTorch / Snapdragon NPU** with per-frame gesture model timing. MediaPipe performs face detection, facial measurements, hand detection, and hand landmarks on the CPU. Its CPU gesture classifier is disabled in this mode. The pretrained gesture network runs in the persistent native ARM64 worker through ExecuTorch/QNN HTP; native errors stop the run rather than silently switching classification to the CPU. Depth decoding also remains on the CPU. A frame without tracked hands makes no NPU gesture calls and displays that state.

[The NPU setup owner](orbbec-mediapipe.md#executorch-and-npu-prerequisites) maintains the model, runtime, and build requirements. The viewer accepts `--qnn-runner`, `--qnn-model`, `--qnn-dsp-dir`, and `--qnn-log` overrides. Its default runtime log is ignored `artifacts/qnn/gesture/depth-viewer-runtime.log`. The optional aggregate report distinguishes MediaPipe time, summed NPU model-call time, and the classifier round trip including host work; these do not measure end-to-end interaction latency.

Observed verification on the prepared laptop: a **30-frame** live depth/RGB check made **51 NPU hand-classification calls**, with changing depth on all 30 frames, up to two tracked hands, native exit 0, and clean stream shutdown. The last frame's summed gesture model time was **0.374 ms**, round trip **1.375 ms**, MediaPipe time **47.31 ms**, and depth decoding **5.62 ms**. These are one-frame observations, not benchmark medians. The subsequent interactive window was responsive after **90 frames and 177 NPU calls**; its native worker loaded `QnnHtp.dll` and `QnnHtpV73Stub.dll`. Together with the existing delegated-model verification, this establishes NPU execution for gesture classification, not acceleration of the full pipeline.

The existing recognition, camera-lifecycle, and QNN protocol tests passed **16 tests**; focused Ruff checks passed. Aggregate results and launch/runtime logs are under ignored `artifacts/scene-understanding/depth-npu-*`. No images or calibration were saved. [SH-T-055](../plan.md#snapdragon-deployment) records this launch; facial NPU inference, image alignment, and accuracy remain separate work.

## Evidence and project boundary

The review used the earlier local conversation, installation READMEs, bridge source, `test-evidence.json`, `bridge/bridge-results.json`, both `verification.json` files, and the later person-app `results/test-results.json`. [Source record SH-S-018](../index.md#source-records) records their original incorporation. On 2026-10-18, the user explicitly approved publishing the saved reports and raw recordings in [the dated archive](../../recordings/2026-10-17_18/README.md), including sensor frames and RGB/depth snapshots. Factory calibration packets, private conversations, and machine-specific account details remain outside Git; published text reports have marked privacy redactions.

The installed bridge and person application remain outside the SecondHands checkout. Later [Orbbec CLI recognition](orbbec-mediapipe.md) and the [scene dashboard](scene-understanding.md) use the bridge's RGB capture, with live execution checks. The combined viewer above adds simultaneous depth display and CPU MediaPipe tracking, with an optional verified ExecuTorch/QNN gesture classifier. Depth decoding itself remains on the CPU. Aligned depth/person positioning, trigger-policy integration, and the previously planned x86 reference-laptop test remain separate work. [Project direction](../project.md#implementation-and-evidence-limits) records the broader project boundaries.
