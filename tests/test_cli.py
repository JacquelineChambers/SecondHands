import subprocess
import sys

import pytest


@pytest.mark.parametrize("args", [["camera", "--max-frames", "0"], ["image", "missing.png"]])
def test_invalid_input_fails_with_actionable_message(args):
    result = subprocess.run(
        [sys.executable, "-m", "secondhands.recognition", *args], capture_output=True, text=True
    )
    assert result.returncode == 2
    assert "error:" in result.stderr
    assert result.stdout == ""


def test_help_does_not_require_vision_imports():
    result = subprocess.run(
        [sys.executable, "-m", "secondhands.recognition", "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "download-models" in result.stdout


def test_download_rejects_bad_content_and_leaves_no_model(tmp_path, monkeypatch):
    from secondhands.recognition import assets

    def transfer(url, filename):
        from pathlib import Path

        Path(filename).write_bytes(b"invalid model")

    monkeypatch.setattr(assets, "urlretrieve", transfer)
    with pytest.raises(ValueError, match="checksum"):
        assets.download_models(tmp_path)
    assert list(tmp_path.iterdir()) == []
