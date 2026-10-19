"""Live measured-depth and MediaPipe RGB viewer for the prepared Orbbec laptop."""

import argparse
import json
from contextlib import ExitStack
from pathlib import Path
from time import monotonic, monotonic_ns

import cv2
import numpy as np

from secondhands.capture.orbbec import OrbbecCamera
from secondhands.capture.orbbec_depth import OrbbecDepthCamera
from secondhands.recognition.__main__ import _draw_trackers
from secondhands.recognition.mediapipe import MediaPipeRecognizer
from secondhands.recognition.qnn_gesture import QnnGestureClassifier

TITLE = "Orbbec depth + MediaPipe"


def label(image, text, point, *, scale=0.6, color=(225, 235, 240)):
    cv2.putText(image, text, point, cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)


def compose(rgb, result, frame, pointer):
    canvas = np.full((760, 1280, 3), (25, 20, 15), dtype=np.uint8)
    color = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    _draw_trackers(cv2, color, result)
    canvas[75:435, :640] = color
    scaled = np.clip((frame.depth_mm.astype(np.float32) - 200) / 4800 * 255, 0, 255)
    depth_color = cv2.applyColorMap(scaled.astype(np.uint8), cv2.COLORMAP_TURBO)
    depth_color[frame.depth_mm == 0] = (0, 0, 0)
    canvas[75:651, 640:] = depth_color
    label(canvas, "ORBBEC / DEPTH + MEDIAPIPE", (20, 32), scale=0.85)
    label(canvas, "Color camera: face + hand tracking (CPU)", (20, 62))
    label(canvas, "Measured depth: 640 x 576", (660, 62))
    label(canvas, f"Faces: {len(result['faces'])}   Hands: {len(result['hands'])}", (20, 475))
    for index, hand in enumerate(result["hands"]):
        gesture = hand["gestures"][0] if hand["gestures"] else None
        description = f"{gesture['label']} ({gesture['score']:.2f})" if gesture else "No category"
        label(canvas, f"Hand {index + 1}: {description}", (20, 510 + index * 30))
    if result.get("runtime", {}).get("gesture_classifier") == "executorch-qnn-htp":
        label(
            canvas,
            "Gesture classifier: ExecuTorch / Snapdragon NPU",
            (20, 570),
            scale=0.55,
            color=(100, 240, 180),
        )
        timing = f"NPU model: {result['timing_ms']['gesture_npu']:.3f} ms"
        if not result["hands"]:
            timing = "NPU ready; no tracked hand in this frame"
        label(canvas, timing, (20, 595), scale=0.55)
    else:
        label(canvas, "Gesture classifier: MediaPipe / CPU", (20, 570), scale=0.55)
        label(canvas, f"MediaPipe: {result['timing_ms']['total']:.0f} ms", (20, 595), scale=0.55)
    label(canvas, "Views have different fields of view and are not aligned.", (20, 625), scale=0.5)
    label(canvas, "Hand landmarks are on color, not measured 3D points.", (20, 650), scale=0.5)
    legend = np.tile(np.linspace(0, 255, 600, dtype=np.uint8), (12, 1))
    canvas[665:677, 660:1260] = cv2.applyColorMap(legend, cv2.COLORMAP_TURBO)
    label(canvas, "0.2 m", (660, 700), scale=0.5)
    label(canvas, "5.0 m", (1205, 700), scale=0.5)
    valid = frame.depth_mm[frame.depth_mm > 0]
    coverage = 100 * valid.size / frame.depth_mm.size
    label(canvas, f"Valid depth: {coverage:.1f}%   Black: no return", (660, 727), scale=0.5)
    age = max(0, (monotonic() - frame.captured_at) * 1000)
    label(
        canvas, f"Depth age: {age:.0f} ms   Decode: {frame.decode_ms:.1f} ms", (660, 750), scale=0.5
    )
    x, y = pointer
    if 640 <= x < 1280 and 75 <= y < 651:
        distance = int(frame.depth_mm[y - 75, x - 640])
        text = f"Pointer depth: {distance / 1000:.3f} m" if distance else "Pointer: no valid depth"
        label(canvas, text, (20, 700), color=(100, 240, 255))
        cv2.drawMarker(canvas, (x, y), (255, 255, 255), cv2.MARKER_CROSS, 16, 1)
    else:
        label(canvas, "Move the pointer over depth to inspect distance.", (20, 700), scale=0.5)
    label(canvas, "Q / Esc / close window: stop both streams. No recording.", (20, 740), scale=0.5)
    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bridge-directory",
        type=Path,
        default=Path.home() / "Documents/Femto-Bolt-Depth-Test-2026-10-17/bridge",
    )
    parser.add_argument("--model-dir", type=Path, default=Path("artifacts/mediapipe"))
    parser.add_argument(
        "--gesture-backend", choices=("mediapipe", "executorch-qnn"), default="mediapipe"
    )
    parser.add_argument(
        "--qnn-runner",
        type=Path,
        default=Path("artifacts/qnn/build-stream/secondhands_qnn_stream.exe"),
    )
    parser.add_argument(
        "--qnn-model", type=Path, default=Path("artifacts/qnn/gesture/gesture_qnn.pte")
    )
    parser.add_argument(
        "--qnn-dsp-dir",
        type=Path,
        default=Path("artifacts/qnn/qairt/2.37.0.250724/lib/hexagon-v73/unsigned"),
    )
    parser.add_argument(
        "--qnn-log", type=Path, default=Path("artifacts/qnn/gesture/depth-viewer-runtime.log")
    )
    parser.add_argument("--max-frames", type=int, default=0, help="0 keeps the viewer open")
    parser.add_argument("--headless", action="store_true", help="Check capture without a window")
    parser.add_argument("--report", type=Path, help="Save aggregate measurements only")
    args = parser.parse_args()
    if args.max_frames < 0:
        parser.error("--max-frames must be zero or positive")
    title = TITLE + (" + NPU gestures" if args.gesture_backend == "executorch-qnn" else " CPU")
    title += " - Q or Esc to stop"
    cv2.setNumThreads(2)
    pointer = [-1, -1]
    report = {
        "frames": 0,
        "depth_frame_changes": 0,
        "max_faces": 0,
        "max_hands": 0,
        "gesture_backend": args.gesture_backend,
        "npu_hand_calls": 0,
        "clean_shutdown": False,
    }
    previous_depth = None
    try:
        with ExitStack() as stack:
            recognizer = stack.enter_context(
                MediaPipeRecognizer(
                    args.model_dir,
                    video=True,
                    classify_gestures=args.gesture_backend == "mediapipe",
                )
            )
            classifier = None
            if args.gesture_backend == "executorch-qnn":
                classifier = stack.enter_context(
                    QnnGestureClassifier(
                        args.qnn_runner,
                        args.qnn_model,
                        args.qnn_dsp_dir,
                        log=args.qnn_log,
                    )
                )
            with OrbbecDepthCamera(args.bridge_directory) as depth_camera:
                first_depth = depth_camera.read()
                if first_depth.depth_mm.shape != (576, 640):
                    raise RuntimeError("Unexpected depth image dimensions")
                with OrbbecCamera(args.bridge_directory) as color_camera:
                    if not args.headless:
                        cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
                        cv2.setMouseCallback(
                            title,
                            lambda event, x, y, flags, param: pointer.__setitem__(
                                slice(None), [x, y]
                            ),
                        )
                    while not args.max_frames or report["frames"] < args.max_frames:
                        rgb = cv2.resize(color_camera.read(), (640, 360))
                        result = recognizer.recognize(rgb, timestamp_ms=monotonic_ns() // 1_000_000)
                        mediapipe_ms = result["timing_ms"]["total"]
                        if classifier:
                            result = classifier.classify_frame(result)
                            report["npu_hand_calls"] += len(result["hands"])
                        frame = depth_camera.read()
                        display = compose(rgb, result, frame, pointer)
                        valid = frame.depth_mm[frame.depth_mm > 0]
                        report.update(
                            frames=report["frames"] + 1,
                            depth_frame_changes=report["depth_frame_changes"]
                            + int(previous_depth != frame.number),
                            max_faces=max(report["max_faces"], len(result["faces"])),
                            max_hands=max(report["max_hands"], len(result["hands"])),
                            valid_depth_percent=float(100 * valid.size / frame.depth_mm.size),
                            median_depth_mm=float(np.median(valid)) if valid.size else None,
                            depth_decode_ms=frame.decode_ms,
                            mediapipe_ms=mediapipe_ms,
                            gesture_npu_ms=result["timing_ms"].get("gesture_npu", 0),
                            gesture_round_trip_ms=result["timing_ms"].get("gesture_round_trip", 0),
                        )
                        previous_depth = frame.number
                        if report["frames"] == 1 or report["frames"] % 30 == 0:
                            print(json.dumps(report), flush=True)
                        if not args.headless:
                            cv2.imshow(title, display)
                            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                                break
                            if cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) < 1:
                                break
        report["clean_shutdown"] = True
    finally:
        cv2.destroyAllWindows()
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({**report, "stopped": True}), flush=True)


if __name__ == "__main__":
    main()
