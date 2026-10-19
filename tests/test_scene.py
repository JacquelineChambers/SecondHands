from concurrent.futures import Future
from threading import Event

import numpy as np
import pytest

from secondhands.api.scene import options_from
from secondhands.recognition import scene


def test_object_decode_uses_objectness_and_does_not_suppress_other_classes():
    rows = np.zeros((1, 4, 85), dtype=np.float32)
    rows[0, :, :4] = [320, 320, 320, 320]
    rows[0, :, 4] = [0.9, 0.8, 0.9, 0.1]
    rows[0, 0, 5] = 0.9
    rows[0, 1, 5] = 0.8  # Duplicate person: suppressed.
    rows[0, 2, 5 + 56] = 0.8  # Overlapping chair: retained.
    rows[0, 3, 5 + 63] = 1  # Strong class with low objectness: rejected.
    detections = scene.decode_objects(rows)
    assert [item["label"] for item in detections] == ["person", "chair"]
    assert detections[0]["score"] == pytest.approx(0.81)
    assert detections[0]["box"] == pytest.approx([0.25, 0.25, 0.5, 0.5])


def test_scene_request_is_bounded_across_sessions(monkeypatch):
    entered, release = Event(), Event()

    def blocked(jpeg):
        entered.set()
        assert release.wait(3)
        return {"description": "test"}

    monkeypatch.setattr(scene, "scene_request", blocked)
    first = scene.submit_scene(b"image")
    try:
        assert entered.wait(1)
        assert scene.submit_scene(b"second session") is None
    finally:
        release.set()
        assert first.result(timeout=3) == {"description": "test"}
    assert scene.submit_scene(b"third").result(timeout=3) == {"description": "test"}


def test_closed_backend_does_not_retain_pending_scene_result():
    from secondhands.api.scene_backend import SceneBackend

    backend = SceneBackend()
    pending = Future()
    backend.future = pending
    backend.scene_result = {"description": "old"}
    backend.close()
    pending.set_result({"description": "late"})
    assert backend.future is None
    assert backend.scene_result is None


@pytest.mark.parametrize("message", [{"source": "file"}, {"camera_index": True}, {"pose": "yes"}])
def test_invalid_camera_options_are_rejected(message):
    with pytest.raises(ValueError):
        options_from(message)


def test_summary_uses_observations_without_turning_missing_input_into_a_gesture():
    result = scene.summarize({"faces": [], "hands": []}, [], [], objects_enabled=True)
    assert "No objects above" in result
    assert "hands: 0" in result
    assert "Hand categories" not in result
