"""Run local recognition. JSON lines go to stdout; status goes to stderr."""

import argparse
import json
import sys
from contextlib import ExitStack
from pathlib import Path
from time import monotonic_ns


def _positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


# MediaPipe's 21-point hand topology: thumb, four fingers, and the palm.
HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20), (0, 17),
)  # fmt: skip


def _draw_trackers(cv2, image, result):
    """Draw face landmarks and hand skeletons from normalized result coordinates."""
    height, width = image.shape[:2]

    def pixel(point):
        return int(point["x"] * width), int(point["y"] * height)

    for face in result["faces"]:
        for point in face["landmarks"]:
            cv2.circle(image, pixel(point), 1, (255, 200, 0), -1)
    for hand in result["hands"]:
        points = [pixel(p) for p in hand["landmarks"]]
        for start, end in HAND_CONNECTIONS:
            cv2.line(image, points[start], points[end], (0, 255, 0), 2)
        for point in points:
            cv2.circle(image, point, 4, (0, 0, 255), -1)
        if hand["gestures"]:
            gesture = hand["gestures"][0]
            x, y = points[0]
            cv2.putText(
                image,
                f"{gesture['label']} {gesture['score']:.2f}",
                (x - 40, y + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("download-models", "image", "camera"):
        command = commands.add_parser(name)
        command.add_argument("--model-dir", type=Path, default=Path("artifacts/mediapipe"))
        if name in ("image", "camera"):
            command.add_argument(
                "--gesture-backend", choices=("mediapipe", "executorch-qnn"), default="mediapipe"
            )
            command.add_argument(
                "--qnn-runner",
                type=Path,
                default=Path("artifacts/qnn/build-stream/secondhands_qnn_stream.exe"),
            )
            command.add_argument(
                "--qnn-model", type=Path, default=Path("artifacts/qnn/gesture/gesture_qnn.pte")
            )
            command.add_argument(
                "--qnn-dsp-dir",
                type=Path,
                default=Path("artifacts/qnn/qairt/2.37.0.250724/lib/hexagon-v73/unsigned"),
            )
        if name == "image":
            command.add_argument("path", type=Path)
        if name == "camera":
            command.add_argument("--camera-index", type=int, default=0)
            command.add_argument("--camera-source", choices=("opencv", "orbbec"), default="opencv")
            command.add_argument(
                "--orbbec-bridge",
                type=Path,
                help="Installed bridge directory with direct_capture.py",
            )
            command.add_argument("--max-frames", type=_positive, default=100)
            command.add_argument("--quiet", action="store_true", help="Suppress per-frame JSON")
            command.add_argument(
                "--preview", action="store_true", help="Open a local preview; press q to stop"
            )
    args = parser.parse_args(argv)
    if args.command == "camera" and args.camera_source == "orbbec" and not args.orbbec_bridge:
        parser.error("Orbbec capture requires --orbbec-bridge DIRECTORY")
    try:
        if args.command == "download-models":
            from .assets import download_models

            download_models(args.model_dir)
            print("MediaPipe model bundles are ready.", file=sys.stderr)
            return 0
        if args.command == "image" and not args.path.is_file():
            raise ValueError("Image file does not exist")
        import cv2

        from .mediapipe import MediaPipeRecognizer

        with ExitStack() as stack:
            recognizer = stack.enter_context(
                MediaPipeRecognizer(
                    args.model_dir,
                    video=args.command == "camera",
                    classify_gestures=args.gesture_backend == "mediapipe",
                )
            )
            classifier = None
            if args.gesture_backend == "executorch-qnn":
                from .qnn_gesture import QnnGestureClassifier

                classifier = stack.enter_context(
                    QnnGestureClassifier(
                        args.qnn_runner,
                        args.qnn_model,
                        args.qnn_dsp_dir,
                        log=Path("artifacts/qnn/gesture/preview-runtime.log"),
                    )
                )
            if args.command == "image":
                bgr = cv2.imread(str(args.path))
                if bgr is None:
                    raise ValueError("Cannot decode image file")
                result = recognizer.recognize(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
                if classifier:
                    result = classifier.classify_frame(result)
                print(json.dumps(result, allow_nan=False))
            else:
                from secondhands.capture.camera import Camera

                if args.camera_source == "orbbec":
                    from secondhands.capture.orbbec import OrbbecCamera

                    source = OrbbecCamera(args.orbbec_bridge)
                else:
                    source = Camera(args.camera_index)
                start = monotonic_ns()
                last = -1
                try:
                    with source as camera:
                        for _ in range(args.max_frames):
                            rgb = camera.read()
                            timestamp = max(last + 1, (monotonic_ns() - start) // 1_000_000)
                            last = timestamp
                            result = recognizer.recognize(rgb, timestamp_ms=timestamp)
                            if classifier:
                                result = classifier.classify_frame(result)
                            if not args.quiet:
                                print(json.dumps(result, allow_nan=False), flush=True)
                            if args.preview:
                                preview = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                                _draw_trackers(cv2, preview, result)
                                labels = [
                                    g["label"] for h in result["hands"] for g in h["gestures"]
                                ]
                                text = (
                                    f"Faces: {len(result['faces'])} Hands: {len(result['hands'])} "
                                )
                                cv2.putText(
                                    preview,
                                    text + ", ".join(labels),
                                    (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6,
                                    (0, 255, 0),
                                    2,
                                )
                                cv2.putText(
                                    preview,
                                    (
                                        "Face/landmarks CPU | gesture ExecuTorch NPU "
                                        f"{result['timing_ms']['gesture_npu']:.2f} ms | q to stop"
                                        if classifier
                                        else f"MediaPipe CPU | {args.camera_source} | q to stop"
                                    ),
                                    (10, preview.shape[0] - 15),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6,
                                    (0, 255, 255),
                                    2,
                                )
                                cv2.imshow("SecondHands (q to stop)", preview)
                                if cv2.waitKey(1) & 0xFF == ord("q"):
                                    break
                finally:
                    if args.preview:
                        cv2.destroyAllWindows()
        return 0
    except KeyboardInterrupt:
        return 130
    except ImportError:
        parser.error("Install vision dependencies with uv sync --locked --extra vision")
    except (OSError, RuntimeError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    sys.exit(main())
