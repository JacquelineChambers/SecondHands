import io
import struct

import pytest

from secondhands.recognition.qnn_gesture import _read_result, hand_features


def _hand():
    return {
        "landmarks": [{"x": i / 50, "y": (i % 5) / 20, "z": i / 200} for i in range(21)],
        "handedness": [{"label": "Right", "score": 0.9}],
    }


def test_features_preserve_shape_across_image_scale_and_translation():
    np = pytest.importorskip("numpy")
    hand = _hand()
    reference = hand_features(hand, 640, 480)
    for point in hand["landmarks"]:
        point["x"] += 0.2
        point["y"] -= 0.1
        point["z"] += 0.05
    np.testing.assert_allclose(hand_features(hand, 1280, 960), reference, atol=1e-6)
    assert reference.shape == (128,)
    assert reference[63] == pytest.approx(0.9)
    assert reference[127] == pytest.approx(0.1)


def test_incomplete_landmarks_are_rejected():
    pytest.importorskip("numpy")
    hand = _hand()
    hand["landmarks"].pop()
    with pytest.raises(ValueError, match="21 finite"):
        hand_features(hand, 640, 480)


class FragmentedStream(io.BytesIO):
    def read(self, size=-1):
        return super().read(min(size, 3))


def test_worker_response_can_arrive_in_fragments():
    payload = struct.pack("<II8fd", 1, 8, 0, 0, 0, 0, 0, 1, 0, 0, 0.5)
    scores, elapsed = _read_result(FragmentedStream(payload))
    assert scores[5] == 1
    assert elapsed == 0.5


@pytest.mark.parametrize(
    "payload, message",
    [
        (b"", "disconnected"),
        (struct.pack("<II", 1, 5000000), "eight gesture"),
        (struct.pack("<II8fd", 1, 8, float("nan"), 0, 0, 0, 0, 1, 0, 0, 0.5), "invalid"),
        (struct.pack("<II8fd", 1, 8, 0, 0, 0, 0, 0, 1, 0, 0, -1), "invalid"),
    ],
)
def test_invalid_worker_response_fails_explicitly(payload, message):
    with pytest.raises(RuntimeError, match=message):
        _read_result(io.BytesIO(payload))
