# Recorded experiments, 17–18 October 2026

This archive contains 252 saved experiment files (40,813,252 bytes), including 48 binary captures, image previews, array exports, model inputs/outputs, and profiler dumps. The user requested publication to GitHub on 2026-10-18 and explicitly confirmed **“Include raw recordings too.”** This approval applies to the saved SecondHands experiments in this dated archive, not to automatic publication of future captures.

[manifest.json](manifest.json) lists every archived data file, its original relative location, source modification time, published byte count, SHA-256 checksum, and any redaction categories. Paths under `artifacts/` came from the SecondHands checkout; paths under `documents/` came from the two local Femto Bolt installations. The originals remain in place. The archive is a snapshot: processes may continue updating their local logs after publication.

## Contents

| Directory | Files | Recorded evidence |
| --- | ---: | --- |
| [Depth tests and bridge](documents/Femto-Bolt-Depth-Test-2026-10-17/) | 53 | Failed SDK attempts, successful bridge reports, three raw NFOV depth frames, decoded depth/infrared arrays, image exports, screenshots, and capture diagnostics |
| [Person detection](documents/Femto-Bolt-Person-Detection/) | 18 | RGB/depth snapshots, detection overlays, aligned position arrays, reports, and verification logs |
| [Dual-camera tests](artifacts/dual-camera-test/) | 12 | Failed attempts, simultaneous changing-frame capture, and reopening checks |
| [Image-model results](artifacts/results/) | 4 | Laya, Mapika, and SmolVLM public-image results and a tracker preview |
| [MediaPipe camera run](artifacts/orbbec-mediapipe/) | 5 | CPU smoke report and preview logs |
| [Face NPU experiments](artifacts/orbbec-face-npu/) | 13 | Reports, profiles, model provenance, and logs |
| [Selfie NPU experiments](artifacts/orbbec-selfie-npu/) | 12 | Reports, profiles, model provenance, and logs |
| [Scene and depth viewers](artifacts/scene-understanding/) | 21 | Live API and backend checks, depth/MediaPipe and NPU runs, and service logs |
| [JEVision runs](artifacts/jevvision-run/) | 7 | Camera/model responses, launch record, service logs, and the saved local viewer HTML |
| [Model download metadata](artifacts/model-downloads/) | 35 | Pinned source metadata, download manifests, file sizes, and hashes |
| [QNN experiments](artifacts/qnn/) | 71 | Gesture, phase, and RTMPose inputs/outputs, profiler dumps, export metadata, and build/runtime logs |
| [Browser check](artifacts/tailscale-page-check/browser-result.json) | 1 | Saved page title, controls, readiness, and JavaScript exception list |

No continuous video or audio files were found in these experiment directories. The raw camera evidence consists of saved sensor frames and RGB/depth snapshots; counters in a live-run report do not imply that every processed camera frame was saved.

## Open the captures

The saved [depth report](documents/Femto-Bolt-Depth-Test-2026-10-17/bridge/depth-bridge-report.html) and [person report](documents/Femto-Bolt-Person-Detection/results/person-detection-report.html) can be downloaded and opened locally. Their original links to running local services or installation scripts are historical and may not work from the archive.

- `direct-nfov-000.bin` through `direct-nfov-002.bin` are original sensor phase frames: 7680 × 434 16-bit samples, 6,666,240 bytes each. They require the original depth decoder and private factory calibration for decoding; corresponding decoded `.npz` files are included.
- Depth `.npz` files contain `depth_mm` and `ir` arrays, each 576 × 640 with `uint16` values. The 16-bit depth PNG retains millimetre values; the colour preview is for inspection.
- `setup-pair.npz` contains 720 × 1280 BGR colour, depth, and infrared arrays. `results/latest-rgb-depth.npz` contains 360 × 640 BGR colour, depth, infrared, and a 360 × 640 × 3 `float32` array named `aligned_xyz_mm`.
- QNN `.raw` files are binary model inputs, reference outputs, or inference outputs, not ordinary image files. Their surrounding experiment reports describe the model and invocation. `.etdp` files are ExecuTorch profiler dumps.

All 48 binary files are unchanged copies. Load NumPy archives with `numpy.load(path, allow_pickle=False)`. Measurements remain subject to the accuracy and reliability limits in [the bridge setup record](../../Wiki/setup/ms-09-femto-bolt-bridge.md), [scene setup record](../../Wiki/setup/scene-understanding.md), and [camera findings](../../Wiki/hardware/femto-bolt.md).

## Publication handling

Thirty-nine text files have marked redactions for personal home paths, local usernames/hostnames, email addresses, private network addresses, device identifiers, or serial numbers. Technical measurements, public source attribution, download hashes, and failed-run evidence are retained. `manifest.json` records the categories for each changed file. Checksums describe the published copies after redaction.

Factory calibration packets, device descriptor binaries, credentials, browser profiles, installed dependencies, downloaded model weights/SDKs, and unrelated personal recordings are outside this archive. Runtime model files and local applications remain in their original installations. The model manifests describe downloads; they do not make the weights part of this snapshot.

The Git attributes for this archive disable line-ending conversion so checksum verification works on every platform. To verify from the repository root:

```python
import hashlib
import json
from pathlib import Path

root = Path('recordings/2026-10-17_18')
manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
for entry in manifest['files']:
    content = (root / entry['path']).read_bytes()
    assert len(content) == entry['bytes'], entry['path']
    assert hashlib.sha256(content).hexdigest() == entry['sha256'], entry['path']
print(f"Verified {manifest['file_count']} files")
```

Publication checks on 2026-10-18: all archive checksums and JSON files validated; targeted credential/private-identifier scans passed; Python tests passed 69 with one optional integration skipped; frontend tests passed 11 across four files; Ruff, TypeScript, and the Vite production build passed. Python tests used a fresh temporary directory after the default Windows pytest cleanup encountered a permissions error. Frontend checks used the installed Node runtime because Bun was unavailable. These checks do not constitute a new camera capture or accuracy evaluation.
