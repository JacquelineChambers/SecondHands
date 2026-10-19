"""Femto Bolt RGB input through the separately installed local Windows bridge."""

import importlib.util
from pathlib import Path
from queue import Empty, Full, Queue
from threading import Event, Thread


def _load_bridge(directory: Path):
    source = directory / "direct_capture.py"
    if not source.is_file():
        raise FileNotFoundError("Bridge directory must contain direct_capture.py")
    spec = importlib.util.spec_from_file_location("secondhands_orbbec_bridge", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.DirectCamera


class OrbbecCamera:
    """Own capture on one COM thread and retain only the newest color frame.

    MediaPipe and the bridge initialize different Windows COM threading modes.
    Keeping bridge creation, reads, and cleanup on a dedicated thread avoids
    that conflict. No depth, calibration, or recording is required for RGB.
    """

    def __init__(self, bridge_directory: Path):
        self._bridge_directory = Path(bridge_directory)
        self._frames = Queue(maxsize=1)
        self._stop = Event()
        self._thread = None

    def _publish(self, value):
        try:
            self._frames.put_nowait(value)
        except Full:
            try:
                self._frames.get_nowait()
            except Empty:
                pass
            self._frames.put_nowait(value)

    def _capture(self):
        try:
            direct_camera = _load_bridge(self._bridge_directory)
            with direct_camera(1280, 720, 15, sensor="color", fourcc="MJPG") as camera:
                while not self._stop.is_set():
                    raw, _, _ = camera.read()
                    self._publish(raw)
        except Exception as error:
            self._publish(error)

    def __enter__(self):
        if self._thread is not None:
            raise RuntimeError("Create a new OrbbecCamera for each capture session")
        self._thread = Thread(target=self._capture, name="orbbec-rgb", daemon=True)
        self._thread.start()
        return self

    def read(self):
        """Decode the newest unmirrored frame to uint8 RGB pixels."""
        try:
            raw = self._frames.get(timeout=10)
        except Empty:
            raise RuntimeError(
                "No Orbbec color frame; check USB, power, and camera ownership"
            ) from None
        if isinstance(raw, Exception):
            raise RuntimeError(f"Orbbec capture failed: {raw}") from raw
        import cv2
        import numpy as np

        bgr = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)
        if bgr is None:
            raise RuntimeError("Cannot decode Orbbec color frame")
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    def __exit__(self, *args):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=10)
            if self._thread.is_alive():
                raise RuntimeError("Orbbec capture did not release the camera within 10 seconds")
