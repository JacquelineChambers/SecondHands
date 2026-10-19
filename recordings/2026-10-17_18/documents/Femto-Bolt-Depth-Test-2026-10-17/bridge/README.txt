FEMTO BOLT LOCAL DEPTH BRIDGE

Start: double-click Start-Depth-Bridge.cmd, then click Start depth.
Stop capture and save: click Stop & save in the viewer.
Stop the background viewer server: run Stop-Depth-Bridge.ps1 in PowerShell.
The bridge does not automatically start with Windows.

Viewer: http://127.0.0.1:8765/
Report: depth-bridge-report.html (standalone, includes both previews)
Measurements: latest-depth.npz, arrays depth_mm and ir
16-bit depth image: latest-depth-mm.png (zero means no valid measurement)
Evidence: bridge-results.json

All capture and processing run on this Snapdragon computer. No cloud service
or second machine is used. The x64 vendor depth engine runs through Windows
ARM64 emulation. Capture was also verified independently in native ARM64.

This prototype supports NFOV unbinned depth, 640 x 576, at 15 FPS. It uses
the camera's own calibration and Orbbec's depth engine. It bypasses Windows
Frame Server by explicitly loading the built-in KS proxy. It does not change
the driver, firmware, registry, or persistent camera calibration.

It is a viewer/export bridge, not a registered virtual camera or a replacement
DLL for arbitrary Orbbec applications. Absolute distance accuracy has not been
verified against a measured target. Pixel coverage depends on the scene.

Keep this folder inside Femto-Bolt-Depth-Test-2026-10-17: the launcher uses the
parent folder's .venv and sdk/OrbbecSDK_v1.10.37/Example/bin/depthengine_2_0.dll.
Dependencies already installed here: x64 Python, numpy, Pillow, vendor SDK.
Close other applications that are using this camera before starting capture.

Command-line validation (from the bridge folder):
  ..\.venv\Scripts\python.exe run_bridge.py --test-seconds 15

Implementation:
  direct_capture.py - camera discovery and direct KS proxy capture
  depth_engine.py   - vendor decoder API and raw sensor frame adapter
  run_bridge.py     - viewer, local HTTP API, exports, and report

HTTP API, local only:
  GET /status       - current capture status and frame statistics (JSON)
  GET /depth.png    - colour depth preview
  GET /ir.png       - infrared amplitude preview
  GET /depth.npz    - latest depth_mm and ir arrays
  GET /report      - saved HTML test report
  POST /start      - start capture; Content-Type: application/json, body {}
  POST /stop       - stop capture and save outputs; same content type/body

Diagnostic scripts and JSON files document routes tried before the successful
KS proxy implementation. Failed ks_capture.py experiments are not the working
transport. Use Start-Depth-Bridge.cmd or run_bridge.py.

No network-facing service is created: the HTTP server binds to 127.0.0.1 only.
Saved camera images and depth data stay in this folder. Each completed capture
replaces the latest exports and report.
