import json
from types import SimpleNamespace as NS

import pytest

from secondhands.recognition.results import frame_result


def test_empty_detections_are_empty_arrays_not_commands():
    result = frame_result(
        NS(face_landmarks=[], face_blendshapes=[]),
        NS(hand_landmarks=[], handedness=[], gestures=[]),
        timestamp_ms=0,
        width=640,
        height=480,
        face_ms=2,
        hand_ms=3,
    )
    assert result["faces"] == []
    assert result["hands"] == []
    assert result["timing_ms"] == {"face": 2, "hand": 3, "total": 5}
    assert json.loads(json.dumps(result))["timestamp_ms"] == 0


def test_results_preserve_subject_categories_and_coordinates():
    landmark = NS(x=0.1, y=0.2, z=-0.3)
    category = NS(category_name="Open_Palm", score=0.9)
    result = frame_result(
        NS(
            face_landmarks=[[landmark]], face_blendshapes=[[NS(category_name="jawOpen", score=0.7)]]
        ),
        NS(
            hand_landmarks=[[landmark]],
            handedness=[[NS(category_name="Left", score=0.8)]],
            gestures=[[category]],
        ),
        timestamp_ms=100,
        width=320,
        height=240,
        face_ms=1,
        hand_ms=2,
    )
    assert result["faces"][0]["blendshapes"] == {"jawOpen": 0.7}
    assert result["hands"][0]["gestures"] == [{"label": "Open_Palm", "score": 0.9}]
    assert result["hands"][0]["landmarks"] == [{"x": 0.1, "y": 0.2, "z": -0.3}]
    assert result["hands"][0]["handedness"] == [{"label": "Left", "score": 0.8}]


def test_missing_models_give_download_instruction(tmp_path):
    from secondhands.recognition.mediapipe import MediaPipeRecognizer

    with pytest.raises(FileNotFoundError, match="download-models"):
        MediaPipeRecognizer(tmp_path)


def test_landmark_only_result_does_not_require_cpu_gesture_predictions():
    landmark = NS(x=0.1, y=0.2, z=0.0)
    result = frame_result(
        NS(face_landmarks=[], face_blendshapes=[]),
        NS(hand_landmarks=[[landmark]], handedness=[[NS(category_name="Right", score=0.9)]]),
        timestamp_ms=0,
        width=640,
        height=480,
        face_ms=1,
        hand_ms=2,
        hand_gestures=[[]],
    )
    assert len(result["hands"]) == 1
    assert result["hands"][0]["gestures"] == []


def test_failed_camera_open_releases_device(monkeypatch):
    cv2 = pytest.importorskip("cv2", reason="Install the vision extra for camera tests")

    from secondhands.capture.camera import Camera

    device = NS(isOpened=lambda: False, release=lambda: setattr(device, "closed", True))
    monkeypatch.setattr(cv2, "VideoCapture", lambda index: device)
    with pytest.raises(RuntimeError, match="camera"):
        with Camera(7):
            pytest.fail("An unavailable camera must not enter its context")
    assert device.closed


def test_camera_read_failure_releases_device(monkeypatch):
    cv2 = pytest.importorskip("cv2", reason="Install the vision extra for camera tests")

    from secondhands.capture.camera import Camera

    device = NS(
        isOpened=lambda: True,
        read=lambda: (False, None),
        release=lambda: setattr(device, "closed", True),
    )
    monkeypatch.setattr(cv2, "VideoCapture", lambda index: device)
    with pytest.raises(RuntimeError, match="frame"):
        with Camera(0) as camera:
            camera.read()
    assert device.closed
