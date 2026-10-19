"""Measured Femto Bolt depth using the installed x64 vendor depth engine."""

import importlib.util
from dataclasses import dataclass
from queue import Empty

from .orbbec import OrbbecCamera, _load_bridge


@dataclass
class DepthFrame:
    depth_mm: object
    infrared: object
    captured_at: float
    number: int
    decode_ms: float


def _load_engine(directory):
    source = directory / "depth_engine.py"
    if not source.is_file():
        raise FileNotFoundError("Bridge directory must contain depth_engine.py")
    spec = importlib.util.spec_from_file_location("secondhands_orbbec_depth_engine", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.DepthEngine, module.calibration_blob


class OrbbecDepthCamera(OrbbecCamera):
    """Reuse bounded capture lifecycle; calibrate/decode on the same worker thread.

    The returned image is in depth-camera coordinates. It is not registered to RGB.
    Calibration and sensor frames stay in memory.
    """

    def _capture(self):
        try:
            direct_camera = _load_bridge(self._bridge_directory)
            engine_type, calibration_blob = _load_engine(self._bridge_directory)
            with direct_camera(1024, 512, 5) as camera:
                packet, _, _ = camera.read()
                calibration = calibration_blob(packet)
            if self._stop.is_set():
                return
            with engine_type(calibration) as engine:
                with direct_camera(7680, 434, 15) as camera:
                    while not self._stop.is_set():
                        raw, _, arrival = camera.read()
                        depth, infrared, info = engine.decode(raw)
                        self._publish(
                            DepthFrame(
                                depth, infrared, arrival, info["frame_number"], info["decode_ms"]
                            )
                        )
        except Exception as error:
            self._publish(error)

    def read(self):
        try:
            frame = self._frames.get(timeout=20)
        except Empty:
            raise RuntimeError(
                "No Orbbec depth frame; close other depth viewers and check USB/power"
            ) from None
        if isinstance(frame, Exception):
            raise RuntimeError(f"Orbbec depth capture failed: {frame}") from frame
        return frame
