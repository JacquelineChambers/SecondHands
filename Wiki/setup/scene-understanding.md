# Orbbec scene understanding

Saved reports and service logs from these runs are available in the user-approved [recorded experiment archive](../../recordings/2026-10-17_18/README.md). Runtime output still goes to the ignored local `artifacts/` directory.

On 2026-10-17, the user requested a MediaPipe application that analyses the live Orbbec camera stream and uses available models for scene understanding. The implemented **Scene understanding** dashboard combines MediaPipe face, hand, and body measurements, YOLOv5s object detections, and sampled-image JEVision descriptions. These model choices implement the requested experiment; they do not resolve the project's final model selection or control policy.

## Start and stop

On the prepared Snapdragon laptop, run [the launcher](../../experiments/start-scene-dashboard.ps1) from the repository root:

```powershell
.\experiments\start-scene-dashboard.ps1
```

Open `http://127.0.0.1:5173`, select **Scene understanding**, and click **Start scene camera**. Orbbec is selected by default. Body pose, object detection, and JEVision analysis can each be disabled before starting. **Stop scene camera** releases the camera and clears observations. Changing to **Gesture experiments** closes the scene session; the two modes share one camera lock.

The launcher needs the prepared project `.venv`, UI dependencies, [RGB bridge](ms-09-femto-bolt-bridge.md), and [downloaded models](../references/models/device-downloads.md). It starts the loopback API and Vite services, plus the prepared [JEVision service](jevvision-orbbec.md#start-and-stop) when available. It prefers Bun; this laptop's observed run used Node with the existing UI dependencies because Bun was unavailable. This launcher is for the prepared device, not a fresh-machine installer. Logs and process identifiers are written under ignored `artifacts/scene-understanding/`. Stopping a camera session leaves these services available.

Use `-BridgeDirectory` for a directory containing `direct_capture.py`, and `-ObjectModel` for a different local YOLOv5s ONNX file. The API also accepts `SECONDHANDS_ORBBEC_BRIDGE` and `SECONDHANDS_OBJECT_MODEL`. Without an object-model override, it checks `artifacts/models/yolov5s/yolov5s.onnx` and then the prepared person-detection installation under the operator's Documents directory. Restart the API after changing these paths; an already-running service retains its environment.

MediaPipe assets are `face_landmarker.task`, `gesture_recognizer.task`, and, when enabled, `pose_landmarker_full.task` under `artifacts/mediapipe/`. Missing tracking/object assets produce a startup error. A missing or failed JEVision service is reported separately while tracking continues; disable JEVision to omit those requests. A standard OpenCV camera is also selectable, but that input was not exercised in this device check.

## Observations and model boundaries

| Component | Displayed result | Current runtime |
| --- | --- | --- |
| MediaPipe Face Landmarker | Face landmarks and count, up to one face | CPU |
| MediaPipe Gesture Recognizer | Hand landmarks and static gesture categories, up to two hands | CPU |
| MediaPipe Pose Landmarker Full | Body skeletons, up to two poses | CPU |
| YOLOv5s ONNX | Boxes and scores for its 80 COCO object classes | OpenCV DNN on CPU |
| JEVision 0.8B | One scene description selected from six experimental choices | Local PyTorch service on ARM64 CPU |

The live preview is resized to 640 pixels wide. Its overlays and deterministic summary use the same frame. The summary reports detected counts, static hand categories, and visible wrists above shoulders; it does not infer identity or command intent. YOLO uses objectness multiplied by class score, a 0.4 threshold, and per-class overlap suppression. These settings are implementation defaults without participant accuracy validation. Coordinates describe the image; this mode does not use depth or report metric distances.

JEVision receives a separate JPEG resized to 384 pixels wide. The choices cover a seated person near a desk, a standing person, a person handling an object, a room without a clear person, an outdoor scene, and an unclear scene. The UI shows the selected hypothesis with its own source thumbnail, age, probability, and inference time. Its probability is a model output, not a calibrated accuracy estimate. The source thumbnail prevents an older scene result from appearing to describe the latest preview.

Only one scene request can run across sessions. Tracking continues while it runs; the next request waits five seconds after completion. Stop/disconnect clears session results and prevents late output from being displayed. An HTTP request already in progress can finish after Stop and temporarily delay a new session's scene request. No camera recordings or calibration data are saved. This mode performs observation only and issues no physical or simulated commands.

All models in this mode currently use the CPU. The separate [ExecuTorch/QNN gesture CLI](orbbec-mediapipe.md) retains its verified NPU path; that native classifier is not connected to the scene dashboard.

## Implementation and verification

[The backend](../../src/secondhands/api/scene_backend.py) owns capture and model execution on a worker thread. [The scene protocol](../../src/secondhands/api/scene.py) bounds frame work and shares ownership with the original gesture endpoint. [Model adapters](../../src/secondhands/recognition/scene.py) provide object decoding and asynchronous JEVision requests. [The React dashboard](../../ui/src/scene/SceneDashboard.tsx) displays matching observations and retains the slower scene result separately.

Observed on the prepared Snapdragon laptop on 2026-10-17:

- A direct five-frame backend check loaded all enabled models and processed live Orbbec frames. JEVision returned a scene hypothesis in 6.54 seconds. Aggregate results are local at `artifacts/scene-understanding/live-smoke.json`.
- A real WebSocket session processed 15 live frames, received a JEVision result, stopped, restarted with a new session ID and JEVision disabled, and cleared the previous result. Median capture/analysis time was **584 ms**; the first frame took **3.76 seconds** including initial camera waiting. JEVision inference took **7.66 seconds** and selected the desk-person description. These timings exclude browser rendering and are not a sustained benchmark or an accuracy result. Aggregate results are local at `artifacts/scene-understanding/api-smoke.json` without source images.
- The full Python suite passed **65 tests**, with **one optional integration test skipped**. The frontend passed **11 tests across four files**. Focused Python lint/format checks, TypeScript checking, and the Vite production build passed. [Backend tests](../../tests/test_scene_api.py) cover ownership, invalid origins, failure cleanup, bounded work, and late results; [UI tests](../../ui/src/scene/SceneDashboard.test.tsx) cover controls, matching overlays, delayed source images, stale sessions, Stop, and disconnect.
- Automatic approval review blocked launching Edge for browser testing with the reason “blocked by policy.” Rendered-browser inspection was therefore not completed. Live API operation and component tests are verified separately.

[SH-T-052](../plan.md#snapdragon-deployment) records this implementation and execution check. Full browser inspection, sustained capture reliability, participant accuracy, comparative model selection, and the wider deployment scope remain open in the plan.
