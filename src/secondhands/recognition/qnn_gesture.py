"""Pretrained gesture classification through a persistent native ExecuTorch worker."""

import math
import os
import struct
import subprocess
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pathlib import Path
from time import perf_counter

LABELS = (
    "None",
    "Closed_Fist",
    "Open_Palm",
    "Pointing_Up",
    "Thumb_Down",
    "Thumb_Up",
    "Victory",
    "ILoveYou",
)


def hand_features(hand, width, height):
    """Match Qualcomm's hand-only gesture preprocessing in image pixel coordinates."""
    import numpy as np

    points = np.asarray(
        [[p["x"] * width, p["y"] * height, p["z"] * width] for p in hand["landmarks"]],
        dtype=np.float32,
    )
    if points.shape != (21, 3) or not np.isfinite(points).all():
        raise ValueError("Gesture classification requires 21 finite hand landmarks")
    side = hand["handedness"][0]
    if side["label"] not in ("Left", "Right") or not 0 <= side["score"] <= 1:
        raise ValueError("Invalid handedness result")
    right = side["score"] if side["label"] == "Right" else 1 - side["score"]
    features = []
    for mirror in (False, True):
        normalized = points.copy()
        if mirror:
            normalized[:, 0] *= -1
        normalized -= normalized[[0, 1, 5, 9, 13, 17]].mean(axis=0)
        normalized /= max(np.ptp(normalized[:, 0]), np.ptp(normalized[:, 1])) + 1e-5
        features.append(
            np.concatenate(
                (normalized.reshape(63), np.asarray([1 - right if mirror else right]))
            ).astype("<f4")
        )
    return np.concatenate(features)


def _read_exact(stream, count):
    chunks = bytearray()
    while len(chunks) < count:
        block = stream.read(count - len(chunks))
        if not block:
            raise RuntimeError("ExecuTorch worker disconnected; inspect its runtime log")
        chunks.extend(block)
    return bytes(chunks)


def _read_result(stream):
    outputs, count = struct.unpack("<II", _read_exact(stream, 8))
    if (outputs, count) != (1, 8):
        raise RuntimeError("ExecuTorch model must return eight gesture probabilities")
    scores = struct.unpack("<8f", _read_exact(stream, 32))
    milliseconds = struct.unpack("<d", _read_exact(stream, 8))[0]
    if (
        not all(math.isfinite(s) and 0 <= s <= 1.001 for s in scores)
        or abs(sum(scores) - 1) > 0.02
        or not math.isfinite(milliseconds)
        or milliseconds < 0
    ):
        raise RuntimeError("ExecuTorch worker returned invalid probabilities or timing")
    return scores, milliseconds


class QnnGestureClassifier:
    """Keep one ARM64 model instance loaded; fail explicitly on native errors."""

    def __init__(self, runner: Path, model: Path, dsp_dir: Path, *, log: Path):
        self.runner, self.model, self.dsp_dir = map(Path, (runner, model, dsp_dir))
        self.log_path = Path(log)
        self.process = self.pool = self.log = None

    def __enter__(self):
        if not self.runner.is_file() or not self.model.is_file() or not self.dsp_dir.is_dir():
            raise FileNotFoundError(
                "Missing native ExecuTorch runner, gesture model, or DSP directory"
            )
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log = self.log_path.open("wb")
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="executorch-pipe")
        env = os.environ.copy()
        env["ADSP_LIBRARY_PATH"] = str(self.dsp_dir.resolve())
        try:
            self.process = subprocess.Popen(
                [str(self.runner.resolve()), str(self.model.resolve())],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=self.log,
                env=env,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            header = self._await(lambda: _read_exact(self.process.stdout, 8), timeout=30)
            if struct.unpack("<II", header) != (0x5348514E, 128):
                raise RuntimeError("Unexpected ExecuTorch worker/model input contract")
        except BaseException:
            self.close(check=False)
            raise
        return self

    def _await(self, operation, *, timeout=10):
        try:
            return self.pool.submit(operation).result(timeout=timeout)
        except TimeoutError as error:
            self.process.kill()
            raise RuntimeError("ExecuTorch worker timed out") from error

    def classify_frame(self, result):
        started = perf_counter()
        npu_ms = 0.0
        for hand in result["hands"]:
            features = hand_features(hand, result["image"]["width"], result["image"]["height"])

            def infer(features=features):
                self.process.stdin.write(struct.pack("<I", 128) + features.tobytes())
                self.process.stdin.flush()
                return _read_result(self.process.stdout)

            scores, milliseconds = self._await(infer)
            best = max(range(len(scores)), key=scores.__getitem__)
            if hand["gestures"]:
                hand["mediapipe_gestures"] = hand["gestures"]
            hand["gestures"] = [{"label": LABELS[best], "score": scores[best]}]
            npu_ms += milliseconds
        elapsed = (perf_counter() - started) * 1000
        result["runtime"] = {
            "face": "mediapipe-cpu",
            "hand_landmarks": "mediapipe-cpu",
            "gesture_classifier": "executorch-qnn-htp",
        }
        result["timing_ms"].update(gesture_npu=npu_ms, gesture_round_trip=elapsed)
        result["timing_ms"]["total"] += elapsed
        return result

    def close(self, *, check=True):
        code = None
        if self.process is not None:
            try:
                self.process.stdin.close()
            except (OSError, ValueError):
                pass
            try:
                code = self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                code = self.process.wait(timeout=5)
            self.process.stdout.close()
        if self.pool is not None:
            self.pool.shutdown(wait=True, cancel_futures=True)
        if self.log is not None:
            self.log.close()
        if check and code not in (None, 0):
            raise RuntimeError(
                f"ExecuTorch worker exited with code {code}; inspect its runtime log"
            )

    def __exit__(self, exc_type, *_):
        self.close(check=exc_type is None)
