"""Preview Orbbec RGB and classify sampled frames with the local JEVision service."""

import argparse
import base64
import json
import math
import textwrap
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import monotonic
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import cv2
import numpy as np

from secondhands.capture.orbbec import OrbbecCamera

DEFAULT_CHOICES = (
    "An open palm with fingers spread.",
    "A thumbs-up gesture.",
    "A closed fist.",
    "One index finger pointing up.",
    "A two-finger V or victory sign.",
    "No clear hand gesture is visible.",
)
WINDOW = "JEVision + Orbbec (q to stop)"


def request_json(url, body=None, *, timeout=90):
    request = Request(
        url,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except HTTPError as error:
        detail = error.read(1500).decode(errors="replace")
        raise RuntimeError(f"JEVision HTTP {error.code}: {detail}") from error


def classify(rgb, server, question, choices):
    started = monotonic()
    height, width = rgb.shape[:2]
    scale = min(1, 384 / max(height, width))
    small = cv2.resize(rgb, (round(width * scale), round(height * scale)))
    ok, encoded = cv2.imencode(
        ".jpg", cv2.cvtColor(small, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90]
    )
    if not ok:
        raise RuntimeError("Could not encode the camera frame")
    criteria = {f"option_{index}": value for index, value in enumerate(choices, start=1)}
    result = request_json(
        server + "/v1/systemone",
        {
            "model": "jevvision",
            "state": "Use only the attached camera image. Judge visible appearance, not intent.",
            "images": [
                {"data_url": "data:image/jpeg;base64," + base64.b64encode(encoded).decode()}
            ],
            "questions": {
                "decision": {"type": "choice", "instructions": question, "criteria": criteria}
            },
        },
    )
    answer = result["answers"]["decision"]
    if answer["choice"] not in criteria:
        raise ValueError("JEVision returned an unknown choice")
    probabilities = answer["probabilities"]
    if set(probabilities) != set(criteria) or not all(
        isinstance(value, (float, int)) and math.isfinite(value) and 0 <= value <= 1
        for value in probabilities.values()
    ):
        raise ValueError("JEVision returned invalid probabilities")
    if not math.isclose(sum(probabilities.values()), 1, abs_tol=0.02):
        raise ValueError("JEVision probabilities do not sum to one")
    return {
        "choice": criteria[answer["choice"]],
        "probability": probabilities[answer["choice"]],
        "probabilities": {criteria[key]: value for key, value in probabilities.items()},
        "latency_ms": result["latency_ms"],
        "round_trip_seconds": monotonic() - started,
        "input_tokens": result["usage"]["input_tokens"],
    }


def preview(bridge, server, question, choices):
    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="jevvision-request")
    future = None
    pending_frame = completed_frame = None
    result = None
    error = ""
    submitted = completed_capture = 0.0
    next_request = 0.0
    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW, 960, 540)
    try:
        with OrbbecCamera(bridge) as camera:
            while True:
                rgb = camera.read()
                now = monotonic()
                if future is not None and future.done():
                    try:
                        result = future.result()
                        completed_frame = pending_frame
                        completed_capture = submitted
                        error = ""
                        print(json.dumps(result, allow_nan=False), flush=True)
                    except (OSError, RuntimeError, ValueError, KeyError, TypeError) as failure:
                        error = str(failure)
                    future = None
                    next_request = now + (5 if error else 1)
                if future is None and now >= next_request:
                    submitted = now
                    pending_frame = rgb.copy()
                    future = pool.submit(classify, pending_frame, server, question, choices)

                canvas = np.zeros((540, 960, 3), dtype=np.uint8)
                canvas[:] = (29, 23, 17)
                canvas[40:400, :640] = cv2.resize(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), (640, 360))
                shown = completed_frame if completed_frame is not None else pending_frame
                if shown is not None:
                    canvas[40:220, 640:960] = cv2.resize(
                        cv2.cvtColor(shown, cv2.COLOR_RGB2BGR), (320, 180)
                    )

                def text(value, x, y, *, color=(230, 230, 230), scale=0.55, frame=canvas):
                    cv2.putText(frame, value, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1)

                text("Orbbec live", 12, 26, scale=0.7)
                text("Last analysed frame" if result else "Frame being analysed", 650, 26)
                text("JEVision | CPU | q to stop", 12, 430, color=(180, 230, 180))
                if result:
                    for index, line in enumerate(textwrap.wrap(result["choice"], 32)):
                        text(line, 650, 250 + index * 24, color=(150, 230, 220))
                    text(f"Model probability: {result['probability']:.1%}", 650, 330)
                    text(f"Inference: {result['latency_ms'] / 1000:.2f} s", 650, 355)
                    text(f"Analysed frame age: {now - completed_capture:.1f} s", 650, 380)
                status = f"Analysing camera frame... {now - submitted:.1f} s" if future else "Ready"
                text(status, 12, 458)
                text("Predictions are experimental; probability is not verified accuracy.", 12, 486)
                if error:
                    text(error[:110], 12, 518, color=(100, 100, 255), scale=0.45)
                cv2.imshow(WINDOW, canvas)
                if (
                    cv2.waitKey(1) & 0xFF == ord("q")
                    or cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1
                ):
                    break
    finally:
        cv2.destroyAllWindows()
        pool.shutdown(wait=False, cancel_futures=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bridge-directory",
        type=Path,
        default=Path.home() / "Documents/Femto-Bolt-Depth-Test-2026-10-17/bridge",
    )
    parser.add_argument("--server", default="http://127.0.0.1:8009")
    parser.add_argument("--question", default="Which hand gesture is most clearly visible?")
    parser.add_argument("--choice", action="append")
    parser.add_argument("--once", action="store_true", help="Classify one camera frame and exit")
    parser.add_argument(
        "--report", type=Path, help="Save the single-frame result, without the image"
    )
    args = parser.parse_args()
    parsed = urlparse(args.server)
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1"):
        parser.error("Use a local HTTP JEVision service")
    choices = args.choice or DEFAULT_CHOICES
    if not 2 <= len(choices) <= 12 or len(set(choices)) != len(choices):
        parser.error("Provide 2 to 12 distinct choices")
    if any(not value.strip() or len(value) > 160 for value in choices):
        parser.error("Each choice must contain 1 to 160 characters")
    if args.report and not args.once:
        parser.error("--report requires --once")
    server = args.server.rstrip("/")
    models = request_json(server + "/v1/models", timeout=5)["models"]
    model = next(item for item in models if item["id"] == "jevvision")
    if not model.get("visual_route"):
        raise RuntimeError("The JEVision service does not have its image adapter loaded")
    if model["device"] != "cpu":
        raise RuntimeError("This preview is configured for the prepared CPU JEVision service")
    if args.once:
        with OrbbecCamera(args.bridge_directory) as camera:
            rgb = camera.read()
        result = classify(rgb, server, args.question, choices)
        result.update(camera="Orbbec Femto Bolt", model="JEVision", device=model["device"])
        print(json.dumps(result, allow_nan=False), flush=True)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(result, indent=2), encoding="utf-8")
    else:
        preview(args.bridge_directory, server, args.question, choices)


if __name__ == "__main__":
    main()
