from threading import Event

import pytest

pytest.importorskip("fastapi", reason="Install the dashboard extra for API tests")
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from secondhands.api.app import create_app

ORIGIN = {"origin": "http://localhost:5173"}


class CameraBackend:
    def __init__(self):
        self.closed = Event()
        self.entered = Event()
        self.release = Event()
        self.release.set()

    def open(self, index):
        return 12.0

    def frame(self):
        self.entered.set()
        self.release.wait(3)
        return (
            {
                "faces": [],
                "hands": [],
                "image": {"width": 1, "height": 1},
                "timing_ms": {"face": 1, "hand": 2, "total": 3},
            },
            "jpeg",
            10,
            5,
            1,
        )

    def close(self):
        self.closed.set()


def start(ws):
    ws.send_json({"type": "start", "camera_index": 0})
    return ws.receive_json()


def test_origin_is_required_before_camera_access():
    with TestClient(create_app()) as client:
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/api/session", headers={"origin": "https://other.test"}):
                pass


@pytest.mark.parametrize("endpoint", ["/api/session", "/api/scene"])
def test_remote_origin_requires_configuration(monkeypatch, endpoint):
    monkeypatch.delenv("SECONDHANDS_ALLOWED_ORIGINS", raising=False)
    with TestClient(create_app()) as client:
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(endpoint, headers={"origin": "https://dashboard.test"}):
                pass


@pytest.mark.parametrize("endpoint", ["/api/session", "/api/scene"])
def test_configured_origins_are_exact_and_preserve_local_access(monkeypatch, endpoint):
    monkeypatch.setenv(
        "SECONDHANDS_ALLOWED_ORIGINS",
        " https://dashboard.test, https://dashboard.test:8443, ",
    )
    with TestClient(create_app()) as client:
        for origin in (
            "https://dashboard.test",
            "https://dashboard.test:8443",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ):
            with client.websocket_connect(endpoint, headers={"origin": origin}) as ws:
                ws.send_json({"type": "stop"})
                assert ws.receive_json()["type"] == "stopped"
        for origin in (
            "https://other.test",
            "https://dashboard.test.attacker.test",
            "http://dashboard.test",
            "https://dashboard.test:9443",
            "null",
            "",
            None,
        ):
            with pytest.raises(WebSocketDisconnect):
                headers = {} if origin is None else {"origin": origin}
                with client.websocket_connect(endpoint, headers=headers):
                    pass


def test_start_frame_stop_and_disconnect_release_resources():
    backend = CameraBackend()
    with TestClient(create_app(lambda: backend)) as client:
        with client.websocket_connect("/api/session", headers=ORIGIN) as ws:
            hello = start(ws)
            assert hello["type"] == "started"
            assert hello["simulate"] is False
            ws.send_json({"type": "frame"})
            frame = ws.receive_json()
            assert frame["frame_id"] == 1
            assert frame["preview"].endswith("jpeg")
            ws.send_json({"type": "stop"})
            assert ws.receive_json()["type"] == "stopped"
        assert backend.closed.wait(1)
    backend = CameraBackend()
    with TestClient(create_app(lambda: backend)) as client:
        with client.websocket_connect("/api/session", headers=ORIGIN) as ws:
            start(ws)
        assert backend.closed.wait(1)


def test_inflight_work_is_bounded_and_changed_mapping_discards_result():
    backend = CameraBackend()
    backend.release.clear()
    with TestClient(create_app(lambda: backend)) as client:
        with client.websocket_connect("/api/session", headers=ORIGIN) as ws:
            start(ws)
            ws.send_json({"type": "frame"})
            assert backend.entered.wait(1)
            ws.send_json({"type": "frame"})
            assert ws.receive_json()["type"] == "busy"
            ws.send_json({"type": "configure", "mapping": {}, "simulate": False})
            assert ws.receive_json()["type"] == "configured"
            backend.release.set()
            assert ws.receive_json()["type"] == "discarded"


def test_second_session_cannot_acquire_camera():
    with TestClient(create_app(CameraBackend)) as client:
        with client.websocket_connect("/api/session", headers=ORIGIN) as first:
            start(first)
            with client.websocket_connect("/api/session", headers=ORIGIN) as second:
                assert start(second)["type"] == "error"


def test_stop_during_work_discards_frame_and_releases_camera():
    backend = CameraBackend()
    backend.release.clear()
    with TestClient(create_app(lambda: backend)) as client:
        with client.websocket_connect("/api/session", headers=ORIGIN) as ws:
            start(ws)
            ws.send_json({"type": "frame"})
            assert backend.entered.wait(1)
            ws.send_json({"type": "stop"})
            backend.release.set()
            responses = [ws.receive_json(), ws.receive_json()]
            assert {r["type"] for r in responses} == {"discarded", "stopped"}
            assert backend.closed.wait(1)
            assert start(ws)["type"] == "started"


def test_unexpected_worker_error_is_reported_and_releases_camera():
    class BrokenBackend(CameraBackend):
        def frame(self):
            raise LookupError("Native processing failure")

    backend = BrokenBackend()
    with TestClient(create_app(lambda: backend)) as client:
        with client.websocket_connect("/api/session", headers=ORIGIN) as ws:
            start(ws)
            ws.send_json({"type": "frame"})
            response = ws.receive_json()
            assert response["type"] == "error"
            assert response["fatal"] is True
        assert backend.closed.wait(1)
