"""Opt-in checks: SECONDHANDS_TEST_MODELS points to downloaded task bundles."""

import os
from pathlib import Path

import pytest

from secondhands.recognition.mediapipe import MediaPipeRecognizer

pytestmark = pytest.mark.skipif(
    not os.environ.get("SECONDHANDS_TEST_MODELS"), reason="requires explicit local model directory"
)


def test_blank_frame_and_video_timestamp_validation():
    import numpy as np

    with MediaPipeRecognizer(Path(os.environ["SECONDHANDS_TEST_MODELS"]), video=True) as model:
        blank = np.zeros((128, 128, 3), dtype=np.uint8)
        result = model.recognize(blank, timestamp_ms=0)
        assert result["faces"] == []
        assert result["hands"] == []
        assert result["timing_ms"]["face"] > 0
        assert result["timing_ms"]["hand"] > 0
        with pytest.raises(ValueError, match="increasing"):
            model.recognize(blank, timestamp_ms=0)
        assert model.recognize(blank, timestamp_ms=1)["timestamp_ms"] == 1
        with pytest.raises(ValueError, match="RGB"):
            model.recognize(np.zeros((128, 128), dtype=np.uint8), timestamp_ms=2)
