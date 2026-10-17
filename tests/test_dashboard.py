import pytest

from secondhands.api.session import DashboardSession


def observation(face=0.1, hand=0.1):
    return {
        "faces": [{"blendshapes": {"browInnerUp": face}, "landmarks": []}],
        "hands": [
            {"gestures": [{"label": "Open_Palm", "score": hand}], "landmarks": [], "handedness": []}
        ],
        "timing_ms": {"face": 2, "hand": 3, "total": 5},
        "image": {"width": 10, "height": 10},
    }


def test_observation_never_activates_and_mapping_change_rejects_old_result():
    s = DashboardSession()
    token = s.token
    s.accept(token, observation(0.9), "jpeg", 0, 5, 1)
    s.accept(token, observation(0.9), "jpeg", 1000, 5, 1)
    assert not s.lamp
    s.configure({"mode": "face", "hold_ms": 0}, True)
    assert s.accept(token, observation(0.9), "jpeg", 1001, 5, 1) is None
    assert not s.lamp
    s.accept(s.token, observation(0.9), "jpeg", 1002, 5, 1)
    assert s.lamp
    s.stop()
    assert s.accept(s.token, observation(0.9), "jpeg", 1100, 5, 1) is None


def test_calibration_is_bounded_resets_triggers_and_clears_on_mapping_change():
    s = DashboardSession()
    s.configure({"mode": "face", "hold_ms": 0}, True)
    s.calibrate("neutral")
    for i in range(40):
        s.accept(s.token, observation(0.1), "jpeg", i * 20, 5, 1)
    assert s.calibration_summary()["neutral"]["count"] == 30
    assert not s.simulate
    s.calibrate("deliberate")
    for i in range(40, 80):
        s.accept(s.token, observation(0.9), "jpeg", i * 20, 5, 1)
    assert s.calibration_summary()["face_suggestion"]["activate"] == pytest.approx(0.7)
    s.configure({"face_signal": "jawOpen"}, False)
    assert s.calibration_summary()["neutral"]["count"] == 0


def test_compare_copies_one_observation_without_claiming_extra_model_runs():
    s = DashboardSession()
    with pytest.raises(ValueError):
        s.compare()
    s.accept(s.token, observation(), "jpeg", 0, 5, 1)
    result = s.compare()
    assert result["frame_id"] == 1
    assert len(result["models"]) == 5
    assert sum(m["available"] for m in result["models"]) == 2
    assert result["recognition"]["timing_ms"]["total"] == 5


@pytest.mark.parametrize(
    "mode,missing", [("face", "hands"), ("hand", "faces"), ("either", "hands"), ("either", "faces")]
)
def test_calibration_accepts_required_modality_only(mode, missing):
    s = DashboardSession()
    s.configure({"mode": mode}, False)
    s.calibrate("neutral")
    frame = observation()
    frame[missing] = []
    s.accept(s.token, frame, "jpeg", 0, 5, 1)
    result = s.calibration_summary()["neutral"]
    assert result["count"] == 1
    assert result["hand_mean" if missing == "hands" else "face_mean"] is None


def test_cancel_invalidates_comparison_evidence():
    s = DashboardSession()
    s.accept(s.token, observation(), "jpeg", 0, 5, 1)
    s.cancel()
    with pytest.raises(ValueError):
        s.compare()
