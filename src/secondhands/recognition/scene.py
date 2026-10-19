"""Local object detections and asynchronous image-level scene decisions."""

import base64
import json
import math
import os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import BoundedSemaphore
from time import perf_counter
from urllib.request import Request, urlopen

COCO_LABELS = (
    "person,bicycle,car,motorcycle,airplane,bus,train,truck,boat,traffic light,fire hydrant,"
    "stop sign,parking meter,bench,bird,cat,dog,horse,sheep,cow,elephant,bear,zebra,giraffe,"
    "backpack,umbrella,handbag,tie,suitcase,frisbee,skis,snowboard,sports ball,kite,baseball bat,"
    "baseball glove,skateboard,surfboard,tennis racket,bottle,wine glass,cup,fork,knife,spoon,"
    "bowl,banana,apple,sandwich,orange,broccoli,carrot,hot dog,pizza,donut,cake,chair,couch,"
    "potted plant,bed,dining table,toilet,tv,laptop,mouse,remote,keyboard,cell phone,microwave,"
    "oven,toaster,sink,refrigerator,book,clock,vase,scissors,teddy bear,hair drier,toothbrush"
).split(",")
SCENE_CHOICES = {
    "desk": "A person seated near a desk or computer.",
    "standing": "A person standing in a room.",
    "handling": "A person holding or handling an object.",
    "room": "An indoor room with furniture and no clearly visible person.",
    "outdoors": "An outdoor scene.",
    "unclear": "None of these descriptions is clearly supported.",
}
_scene_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="secondhands-scene")
_scene_slot = BoundedSemaphore(1)


def object_model_path():
    configured = os.environ.get("SECONDHANDS_OBJECT_MODEL")
    if configured:
        return Path(configured)
    local = Path("artifacts/models/yolov5s/yolov5s.onnx")
    if local.is_file():
        return local
    return (
        Path.home()
        / "Documents/Femto-Bolt-Person-Detection/upstream/examples/applications"
        / "object_detection/models/yolov5s.onnx"
    )


def decode_objects(prediction, threshold=0.4):
    """Decode YOLOv5 COCO output, multiplying objectness and class probability."""
    import cv2
    import numpy as np

    rows = np.asarray(prediction, dtype=np.float32).reshape(-1, 85)
    rows = rows[np.isfinite(rows).all(axis=1)]
    classes = rows[:, 5:].argmax(axis=1)
    scores = rows[:, 4] * rows[np.arange(len(rows)), 5 + classes]
    keep = (scores >= threshold) & (scores <= 1) & (rows[:, 2] > 0) & (rows[:, 3] > 0)
    rows, classes, scores = rows[keep], classes[keep], scores[keep]
    detections = []
    for category in np.unique(classes):
        indices = np.flatnonzero(classes == category)
        boxes = [
            [float(r[0] - r[2] / 2), float(r[1] - r[3] / 2), float(r[2]), float(r[3])]
            for r in rows[indices]
        ]
        selected = cv2.dnn.NMSBoxes(boxes, scores[indices].tolist(), threshold, 0.45)
        for selected_index in np.asarray(selected).reshape(-1):
            index = indices[selected_index]
            x, y, width, height = boxes[selected_index]
            x0, y0 = max(0.0, x / 640), max(0.0, y / 640)
            x1, y1 = min(1.0, (x + width) / 640), min(1.0, (y + height) / 640)
            if x1 > x0 and y1 > y0:
                detections.append(
                    {
                        "label": COCO_LABELS[category],
                        "score": float(scores[index]),
                        "box": [x0, y0, x1 - x0, y1 - y0],
                    }
                )
    return sorted(detections, key=lambda d: d["score"], reverse=True)[:50]


class ObjectDetector:
    def __init__(self, path):
        import cv2

        self.net = cv2.dnn.readNetFromONNX(str(path))
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    def detect(self, rgb):
        import cv2

        started = perf_counter()
        self.net.setInput(cv2.dnn.blobFromImage(rgb, 1 / 255, (640, 640), swapRB=False))
        detections = decode_objects(self.net.forward())
        return detections, (perf_counter() - started) * 1000


def summarize(recognition, objects, poses, *, objects_enabled):
    """Summarize visible model observations without inferring identity or intent."""
    counts = Counter(item["label"] for item in objects)
    parts = []
    if objects_enabled:
        parts.append(
            "Objects detected: " + ", ".join(f"{count} {name}" for name, count in counts.items())
            if counts
            else "No objects above the detection threshold."
        )
    parts.append(f"Faces tracked: {len(recognition['faces'])}; hands: {len(recognition['hands'])}.")
    gestures = [
        gesture["label"].replace("_", " ")
        for hand in recognition["hands"]
        for gesture in hand["gestures"][:1]
        if gesture["label"] != "None"
    ]
    if gestures:
        parts.append("Hand categories: " + ", ".join(gestures) + ".")
    for pose in poses:
        for side, wrist, shoulder in (("Left", 15, 11), ("Right", 16, 12)):
            if min(pose[wrist]["visibility"], pose[shoulder]["visibility"]) >= 0.6:
                if pose[wrist]["y"] < pose[shoulder]["y"]:
                    parts.append(f"{side} wrist is above its shoulder in the image.")
    return " ".join(parts)


def scene_request(jpeg, *, origin="http://127.0.0.1:8009"):
    body = {
        "model": "jevvision",
        "state": "Judge only what is visible in this image. Do not infer identity or intent.",
        "images": [{"data_url": "data:image/jpeg;base64," + base64.b64encode(jpeg).decode()}],
        "questions": {
            "scene": {
                "type": "choice",
                "instructions": "Which description best matches the visible scene?",
                "criteria": SCENE_CHOICES,
            }
        },
    }
    request = Request(
        origin + "/v1/systemone",
        json.dumps(body).encode(),
        {"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=60) as response:
        result = json.load(response)
    answer = result["answers"]["scene"]
    probabilities = answer["probabilities"]
    if answer["choice"] not in SCENE_CHOICES or set(probabilities) != set(SCENE_CHOICES):
        raise ValueError("Invalid scene choice")
    if not all(math.isfinite(value) and 0 <= value <= 1 for value in probabilities.values()):
        raise ValueError("Invalid scene probabilities")
    if not math.isclose(sum(probabilities.values()), 1, abs_tol=0.02):
        raise ValueError("Invalid scene probability total")
    return {
        "description": SCENE_CHOICES[answer["choice"]],
        "probability": probabilities[answer["choice"]],
        "latency_ms": result["latency_ms"],
        "model": "JEVision 0.8B",
        "runtime": "CPU",
    }


def submit_scene(jpeg):
    """One global in-flight request, including across stopped/restarted sessions."""
    if not _scene_slot.acquire(blocking=False):
        return None

    def run():
        try:
            return scene_request(jpeg)
        finally:
            _scene_slot.release()

    try:
        return _scene_pool.submit(run)
    except BaseException:
        _scene_slot.release()
        raise
