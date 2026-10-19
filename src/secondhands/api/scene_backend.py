"""Camera-thread scene pipeline; image-level decisions run independently."""

import base64
import logging
import os
from contextlib import ExitStack
from pathlib import Path
from time import monotonic, monotonic_ns, perf_counter

from secondhands.capture.camera import Camera
from secondhands.capture.orbbec import OrbbecCamera
from secondhands.recognition.mediapipe import MediaPipeRecognizer
from secondhands.recognition.scene import (
    ObjectDetector,
    object_model_path,
    submit_scene,
    summarize,
)

logger = logging.getLogger(__name__)


class SceneBackend:
    def __init__(self):
        self.stack = ExitStack()
        self.future = None
        self.scene_result = None
        self.scene_error = None
        self.next_scene = 0.0
        self.last_timestamp = -1
        self.closed = False

    def open(self, options):
        import cv2
        import mediapipe as mp

        self.options = options
        self.mp = mp
        cv2.setNumThreads(2)
        self.models = []
        started = perf_counter()
        try:
            self.recognizer = self.stack.enter_context(
                MediaPipeRecognizer(Path("artifacts/mediapipe"), video=True)
            )
            self.models.append(
                {"name": "MediaPipe face + hands", "state": "ready", "runtime": "CPU"}
            )
            self.pose = None
            if options["pose"]:
                self.pose = self.stack.enter_context(
                    mp.tasks.vision.PoseLandmarker.create_from_options(
                        mp.tasks.vision.PoseLandmarkerOptions(
                            base_options=mp.tasks.BaseOptions(
                                model_asset_path="artifacts/mediapipe/pose_landmarker_full.task"
                            ),
                            running_mode=mp.tasks.vision.RunningMode.VIDEO,
                            num_poses=2,
                        )
                    )
                )
                self.models.append({"name": "MediaPipe pose", "state": "ready", "runtime": "CPU"})
            self.detector = ObjectDetector(object_model_path()) if options["objects"] else None
            if self.detector:
                self.models.append({"name": "YOLOv5s objects", "state": "ready", "runtime": "CPU"})
            if options["scene_model"]:
                self.models.append({"name": "JEVision scene", "state": "waiting", "runtime": "CPU"})
            source = (
                OrbbecCamera(
                    Path(os.environ["SECONDHANDS_ORBBEC_BRIDGE"])
                    if "SECONDHANDS_ORBBEC_BRIDGE" in os.environ
                    else Path.home() / "Documents/Femto-Bolt-Depth-Test-2026-10-17/bridge"
                )
                if options["source"] == "orbbec"
                else Camera(options["camera_index"])
            )
            self.camera = self.stack.enter_context(source)
            return {"model_load_ms": (perf_counter() - started) * 1000, "models": self.models}
        except BaseException:
            self.stack.close()
            raise

    def _scene(self, rgb, captured_ms):
        import cv2

        if not self.options["scene_model"]:
            return {"state": "disabled", "result": None, "error": None}
        if self.future is not None and self.future.done():
            try:
                self.scene_result = {
                    **self.future.result(),
                    "preview": self.pending_preview,
                    "captured_ms": self.pending_timestamp,
                }
                self.scene_error = None
            except Exception:
                logger.exception("Scene model request failed")
                self.scene_error = "Scene analysis unavailable. Check the local JEVision service."
            self.future = None
            self.next_scene = monotonic() + 5
        if self.future is None and monotonic() >= self.next_scene:
            height, width = rgb.shape[:2]
            small = cv2.resize(rgb, (384, round(height * 384 / width)))
            ok, encoded = cv2.imencode(".jpg", cv2.cvtColor(small, cv2.COLOR_RGB2BGR))
            if not ok:
                raise RuntimeError("Scene frame encoding failed")
            self.future = submit_scene(encoded.tobytes())
            self.next_scene = monotonic() + 2
            if self.future is not None:
                self.pending_preview = (
                    "data:image/jpeg;base64," + base64.b64encode(encoded).decode()
                )
                self.pending_timestamp = captured_ms
        state = (
            "processing"
            if self.future
            else "error"
            if self.scene_error
            else "ready"
            if self.scene_result
            else "waiting"
        )
        return {
            "state": state,
            "error": self.scene_error,
            "result": self.scene_result,
            "age_ms": captured_ms - self.scene_result["captured_ms"] if self.scene_result else None,
        }

    def frame(self):
        import cv2

        started = perf_counter()
        rgb = self.camera.read()
        captured_ms = max(monotonic_ns() // 1_000_000, self.last_timestamp + 1)
        self.last_timestamp = captured_ms
        height, width = rgb.shape[:2]
        rgb = cv2.resize(rgb, (640, round(height * 640 / width)))
        recognition = self.recognizer.recognize(rgb, timestamp_ms=captured_ms)
        poses, pose_ms = [], 0.0
        if self.pose:
            pose_started = perf_counter()
            result = self.pose.detect_for_video(
                self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=rgb), captured_ms
            )
            poses = [
                [{"x": p.x, "y": p.y, "z": p.z, "visibility": p.visibility} for p in points]
                for points in result.pose_landmarks
            ]
            pose_ms = (perf_counter() - pose_started) * 1000
        objects, object_ms = self.detector.detect(rgb) if self.detector else ([], 0.0)
        semantic = self._scene(rgb, captured_ms)
        ok, encoded = cv2.imencode(
            ".jpg", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 78]
        )
        if not ok:
            raise RuntimeError("Preview encoding failed")
        return {
            "preview": "data:image/jpeg;base64," + base64.b64encode(encoded).decode(),
            "recognition": recognition,
            "poses": poses,
            "objects": objects,
            "summary": summarize(recognition, objects, poses, objects_enabled=bool(self.detector)),
            "scene": semantic,
            "captured_ms": captured_ms,
            "processing_ms": (perf_counter() - started) * 1000,
            "timing_ms": {
                "mediapipe": recognition["timing_ms"]["total"],
                "pose": pose_ms,
                "objects": object_ms,
            },
        }

    def close(self):
        self.closed = True
        self.stack.close()
        self.future = self.scene_result = None
