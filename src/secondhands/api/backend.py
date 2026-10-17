"""All native camera and MediaPipe operations run on one worker thread."""

import base64
from contextlib import ExitStack
from pathlib import Path
from time import monotonic_ns, perf_counter_ns

from secondhands.capture.camera import Camera
from secondhands.recognition.mediapipe import MediaPipeRecognizer


class CameraBackend:
    def __init__(self):
        self.stack = ExitStack()
        self.last_timestamp = -1

    def open(self, index):
        start = perf_counter_ns()
        try:
            self.recognizer = self.stack.enter_context(
                MediaPipeRecognizer(Path("artifacts/mediapipe"), video=True)
            )
            load_ms = (perf_counter_ns() - start) / 1e6
            self.camera = self.stack.enter_context(Camera(index))
            return load_ms
        except BaseException:
            self.stack.close()
            raise

    def frame(self):
        import cv2

        before = perf_counter_ns()
        rgb = self.camera.read()
        capture_ms = (perf_counter_ns() - before) / 1e6
        captured_ms = max(monotonic_ns() // 1_000_000, self.last_timestamp + 1)
        self.last_timestamp = captured_ms
        start = perf_counter_ns()
        # Bound preview and recognition pixel work, preserving the same coordinate system.
        height, width = rgb.shape[:2]
        if width > 960:
            rgb = cv2.resize(rgb, (960, round(height * 960 / width)))
        result = self.recognizer.recognize(rgb, timestamp_ms=captured_ms)
        ok, encoded = cv2.imencode(
            ".jpg", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 75]
        )
        if not ok:
            raise RuntimeError("Preview encoding failed")
        return (
            result,
            base64.b64encode(encoded).decode("ascii"),
            captured_ms,
            (perf_counter_ns() - start) / 1e6,
            capture_ms,
        )

    def close(self):
        self.stack.close()
