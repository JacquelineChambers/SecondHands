from threading import Event

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from secondhands.api.app import create_app

ORIGIN = {"origin": "http://localhost:5173"}


class Backend:
    def __init__(self):
        self.closed = Event()
        self.entered = Event()
        self.release = Event()
        self.release.set()

    def open(self, options):
        return {"models": [], "model_load_ms": 1}

    def frame(self):
        self.entered.set()
        assert self.release.wait(3)
        return {"preview": "test", "scene": {"state": "processing", "result": None}}

    def close(self):
        self.closed.set()


def start(ws):
    ws.send_json({"type": "start"})
    return ws.receive_json()


def test_scene_origin_is_checked():
    with TestClient(create_app()) as client:
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/api/scene", headers={"origin": "https://other.test"}):
                pass


def test_scene_frames_have_session_identity_and_disconnect_closes_camera():
    backend = Backend()
    with TestClient(create_app(scene_backend_factory=lambda: backend)) as client:
        with client.websocket_connect("/api/scene", headers=ORIGIN) as ws:
            hello = start(ws)
            ws.send_json({"type": "frame"})
            result = ws.receive_json()
            assert result["session_id"] == hello["session_id"]
            assert result["frame_id"] == 1
            assert result["scene"]["state"] == "processing"
        assert backend.closed.wait(1)


def test_scene_camera_lock_is_shared_with_original_dashboard():
    with TestClient(create_app(scene_backend_factory=Backend)) as client:
        with client.websocket_connect("/api/scene", headers=ORIGIN) as scene_ws:
            assert start(scene_ws)["type"] == "started"
            with client.websocket_connect("/api/session", headers=ORIGIN) as original:
                assert start(original)["type"] == "error"
            with client.websocket_connect("/api/scene", headers=ORIGIN) as other:
                assert start(other)["type"] == "error"


def test_stop_during_capture_discards_late_frame_and_allows_restart():
    backend = Backend()
    backend.release.clear()
    with TestClient(create_app(scene_backend_factory=lambda: backend)) as client:
        with client.websocket_connect("/api/scene", headers=ORIGIN) as ws:
            first = start(ws)
            ws.send_json({"type": "frame"})
            assert backend.entered.wait(1)
            ws.send_json({"type": "frame"})
            assert ws.receive_json()["type"] == "busy"
            ws.send_json({"type": "stop"})
            backend.release.set()
            assert ws.receive_json()["type"] == "stopped"
            assert backend.closed.wait(1)
            second = start(ws)
            assert second["session_id"] != first["session_id"]


def test_start_failure_releases_shared_camera_lock():
    class Broken(Backend):
        def open(self, options):
            raise RuntimeError("Missing local asset")

    with TestClient(create_app(scene_backend_factory=Broken)) as client:
        with client.websocket_connect("/api/scene", headers=ORIGIN) as ws:
            assert start(ws)["type"] == "error"
            assert "Another camera session" not in start(ws)["message"]
