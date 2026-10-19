FEMTO BOLT PERSON DETECTION - INSTALLED LOCAL APPLICATION

Start: double-click Start-Person-Detection.cmd (or the desktop shortcut).
Viewer: http://127.0.0.1:8766/
Capture starts automatically with the launcher. Use Stop camera when done.
Save test report exports a standalone HTML report, JSON observations, and arrays.
To terminate the background server, run Stop-Person-Detection.ps1 in PowerShell.

TESTING A PERSON
Stand about 1-3 metres from the camera with your upper body visible.
Move left/right: the X coordinate and top-down marker should move.
Move closer/farther: Z should decrease/increase.
Green boxes have usable measured depth. Orange boxes have no reliable depth.
Depth overlay colours should follow visible surfaces in the colour image.
The small cyan rectangle shows the depth sampling region for each person.
Box numbers are labels within a frame, not identities or persistent track IDs.

This uses the first recommended GitHub project:
https://github.com/orbbec/pyorbbecsdk/tree/v2-main/examples/applications/object_detection
An unchanged clone is in upstream/. The adaptation is in detector.py and
person_app.py. It uses the repository's YOLOv5s ONNX model and the working
local Femto Bolt bridge. Upstream camera capture is replaced because the
standard SDK capture path failed on this computer.

WHAT WAS INSTALLED
A separate x64 Python environment in .venv, with ONNX Runtime, OpenCV 4,
NumPy and Pillow. The model is already downloaded. Runtime is local and does
not require cloud inference. requirements-lock.txt records installed versions.
Windows runs the x64 Python environment through ARM64 emulation.
No drivers, registry entries, firmware, or startup tasks were changed.

HOW RGB AND DEPTH ARE COMBINED
The local bridge reads the built-in Windows KS proxy directly. It captures
1280x720 MJPEG RGB and 640x576 decoded depth using 15 FPS profiles. RGB is
resized to 640x360 for detection and the matching factory calibration.
The SDK v2 is used only to read calibration from the connected camera; the
SDK v1 depth engine decodes raw phase data. Neither SDK is used for capture.
The calibration reader runs at each Start camera, so a stale calibration is
not silently used for a different camera.

Depth is undistorted using factory lens coefficients, transformed into RGB
camera space, projected into the RGB image, and resolved with nearest-depth
occlusion handling. Valid source depth is limited to 0.5-3.86 m for NFOV
unbinned mode. Position uses a median of central box samples with outlier
rejection. Occlusion/background can still affect the estimate.

X/Y/Z are in metres relative to the colour camera: right/down/forward.
Z is forward depth; Euclidean distance is also available in JSON.
RGB/depth pairing uses host callback arrival timestamps. It is not hardware
synchronization. Measurements are withheld if the pair differs by >75 ms.
The detector processes recent frames at its own rate (about 4-5 FPS in the
initial test); intermediate capture frames are intentionally skipped.
Absolute distance accuracy has not been verified against a measured target.

FILES
results/person-detection-report.html - standalone saved report
results/test-results.json            - stats and up to 3000 recent observations
results/latest-rgb-depth.npz          - color_bgr, depth_mm, ir, aligned_xyz_mm
results/color-detections.jpg          - last annotated colour image
results/aligned-depth.jpg             - last calibrated depth overlay
results/verification.json             - installation test results
server-errors.log                    - error details if startup fails

Keep the sibling Femto-Bolt-Depth-Test-2026-10-17 folder. It contains the
working bridge and vendor DLLs used here. Close other camera applications
before use. Starting this app stops capture in our earlier depth-only viewer.
Both viewers can remain open, but only one should capture the depth sensor.

The service binds to 127.0.0.1 only. No network-facing service is installed.
POST /start, /stop, /save require application/json with body {}.
GET /status exposes detections and coordinates for local integration.
GET /color.jpg and /overlay.jpg provide the latest previews.

Source/license information: upstream/LICENSE and THIRD-PARTY-NOTICES.txt.
