"""Run local recognition. JSON lines go to stdout; status goes to stderr."""

import argparse
import json
import sys
from pathlib import Path
from time import monotonic_ns


def _positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("download-models", "image", "camera"):
        command = commands.add_parser(name)
        command.add_argument("--model-dir", type=Path, default=Path("artifacts/mediapipe"))
        if name == "image":
            command.add_argument("path", type=Path)
        if name == "camera":
            command.add_argument("--camera-index", type=int, default=0)
            command.add_argument("--max-frames", type=_positive, default=100)
            command.add_argument(
                "--preview", action="store_true", help="Open a local preview; press q to stop"
            )
    args = parser.parse_args(argv)
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

        with MediaPipeRecognizer(args.model_dir, video=args.command == "camera") as recognizer:
            if args.command == "image":
                bgr = cv2.imread(str(args.path))
                if bgr is None:
                    raise ValueError("Cannot decode image file")
                result = recognizer.recognize(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
                print(json.dumps(result, allow_nan=False))
            else:
                from secondhands.capture.camera import Camera

                start = monotonic_ns()
                last = -1
                try:
                    with Camera(args.camera_index) as camera:
                        for _ in range(args.max_frames):
                            rgb = camera.read()
                            timestamp = max(last + 1, (monotonic_ns() - start) // 1_000_000)
                            last = timestamp
                            result = recognizer.recognize(rgb, timestamp_ms=timestamp)
                            print(json.dumps(result, allow_nan=False), flush=True)
                            if args.preview:
                                preview = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
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
