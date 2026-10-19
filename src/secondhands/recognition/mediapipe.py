"""Synchronous CPU baseline with optional MediaPipe dependencies."""

from contextlib import ExitStack
from pathlib import Path
from time import perf_counter_ns
from zipfile import ZipFile

from .results import frame_result


class MediaPipeRecognizer:
    """Use image mode for independent images and video mode for camera tracking."""

    def __init__(self, model_dir: Path, *, video: bool = False, classify_gestures: bool = True):
        paths = [
            Path(model_dir) / name for name in ("face_landmarker.task", "gesture_recognizer.task")
        ]
        if not all(path.is_file() for path in paths):
            raise FileNotFoundError(
                "Missing MediaPipe models. Run python -m secondhands.recognition download-models"
                " with the same --model-dir first."
            )
        import mediapipe as mp

        self._mp = mp
        self._video = video
        self._classify_gestures = classify_gestures
        self._timestamp = -1
        self._stack = ExitStack()
        mode = mp.tasks.vision.RunningMode.VIDEO if video else mp.tasks.vision.RunningMode.IMAGE
        try:
            self._face = self._stack.enter_context(
                mp.tasks.vision.FaceLandmarker.create_from_options(
                    mp.tasks.vision.FaceLandmarkerOptions(
                        base_options=mp.tasks.BaseOptions(model_asset_path=str(paths[0])),
                        running_mode=mode,
                        num_faces=1,
                        output_face_blendshapes=True,
                    )
                )
            )
            if classify_gestures:
                self._hand = self._stack.enter_context(
                    mp.tasks.vision.GestureRecognizer.create_from_options(
                        mp.tasks.vision.GestureRecognizerOptions(
                            base_options=mp.tasks.BaseOptions(model_asset_path=str(paths[1])),
                            running_mode=mode,
                            num_hands=2,
                        )
                    )
                )
            else:
                # Reuse the pinned bundle's landmark subtask without running its CPU classifier.
                with ZipFile(paths[1]) as bundle:
                    hand_model = bundle.read("hand_landmarker.task")
                self._hand = self._stack.enter_context(
                    mp.tasks.vision.HandLandmarker.create_from_options(
                        mp.tasks.vision.HandLandmarkerOptions(
                            base_options=mp.tasks.BaseOptions(model_asset_buffer=hand_model),
                            running_mode=mode,
                            num_hands=2,
                        )
                    )
                )
        except BaseException:
            self._stack.close()
            raise

    def recognize(self, rgb, *, timestamp_ms: int = 0):
        """Accept an unmirrored uint8 RGB array. Video timestamps strictly increase."""
        import numpy as np

        if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.dtype != np.uint8 or not rgb.size:
            raise ValueError("Expected a nonempty uint8 RGB image with three channels")
        if timestamp_ms < 0 or (self._video and timestamp_ms <= self._timestamp):
            raise ValueError("Video timestamps must be nonnegative and strictly increasing")
        image = self._mp.Image(
            image_format=self._mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)
        )
        start = perf_counter_ns()
        face = (
            self._face.detect_for_video(image, timestamp_ms)
            if self._video
            else self._face.detect(image)
        )
        middle = perf_counter_ns()
        if self._classify_gestures:
            hand = (
                self._hand.recognize_for_video(image, timestamp_ms)
                if self._video
                else self._hand.recognize(image)
            )
        else:
            hand = (
                self._hand.detect_for_video(image, timestamp_ms)
                if self._video
                else self._hand.detect(image)
            )
        end = perf_counter_ns()
        self._timestamp = timestamp_ms
        return frame_result(
            face,
            hand,
            timestamp_ms=timestamp_ms,
            width=rgb.shape[1],
            height=rgb.shape[0],
            face_ms=(middle - start) / 1e6,
            hand_ms=(end - middle) / 1e6,
            hand_gestures=None if self._classify_gestures else [[] for _ in hand.hand_landmarks],
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._stack.close()
