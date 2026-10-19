"""Camera ownership and error propagation without requiring Windows hardware."""

from threading import get_ident

import pytest

from secondhands.capture import orbbec


def test_bridge_failure_reaches_reader_and_thread_exits(monkeypatch, tmp_path):
    def fail(_):
        raise OSError("camera disconnected")

    monkeypatch.setattr(orbbec, "_load_bridge", fail)
    with orbbec.OrbbecCamera(tmp_path) as camera:
        with pytest.raises(RuntimeError, match="camera disconnected"):
            camera.read()
    assert not camera._thread.is_alive()


def test_capture_and_cleanup_share_worker_thread(monkeypatch, tmp_path):
    calls = []

    class FakeBridge:
        def __init__(self, *args, **kwargs):
            calls.append(("create", get_ident()))

        def __enter__(self):
            return self

        def read(self):
            calls.append(("read", get_ident()))
            raise OSError("end of test stream")

        def __exit__(self, *args):
            calls.append(("close", get_ident()))

    monkeypatch.setattr(orbbec, "_load_bridge", lambda _: FakeBridge)
    with orbbec.OrbbecCamera(tmp_path) as camera:
        with pytest.raises(RuntimeError, match="end of test stream"):
            camera.read()
    assert [name for name, _ in calls] == ["create", "read", "close"]
    assert len({thread for _, thread in calls}) == 1
    assert calls[0][1] != get_ident()


def test_only_latest_frame_is_retained(tmp_path):
    camera = orbbec.OrbbecCamera(tmp_path)
    camera._publish(b"old frame")
    camera._publish(b"new frame")
    assert camera._frames.get_nowait() == b"new frame"
