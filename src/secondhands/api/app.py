"""Loopback-only exploration API with explicit camera ownership and bounded work."""

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .backend import CameraBackend
from .session import DashboardSession

ALLOWED_ORIGINS = {"http://localhost:5173", "http://127.0.0.1:5173"}


def create_app(backend_factory=CameraBackend):
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    camera_owner = asyncio.Lock()

    @app.get("/api/health")
    def health():
        return {"status": "ok", "scope": "local exploration; simulated actions only"}

    @app.websocket("/api/session")
    async def session_socket(ws: WebSocket):
        if ws.headers.get("origin") not in ALLOWED_ORIGINS:
            await ws.close(code=1008)
            return
        await ws.accept()
        executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="secondhands-camera")
        loop = asyncio.get_running_loop()
        session = None
        backend = None
        pending = None
        owns_camera = False
        send_lock = asyncio.Lock()

        async def send(payload):
            async with send_lock:
                await asyncio.wait_for(ws.send_json(payload), timeout=5)

        async def close_camera():
            nonlocal backend, session, owns_camera, pending
            if session:
                session.stop()
            if pending:
                with suppress(Exception):
                    await asyncio.shield(pending)
                pending = None
            if backend:
                await asyncio.shield(loop.run_in_executor(executor, backend.close))
                backend = None
            if owns_camera:
                camera_owner.release()
                owns_camera = False
            session = None

        async def produce(current, token):
            try:
                result = await loop.run_in_executor(executor, backend.frame)
                envelope = current.accept(token, *result)
                await send(envelope or {"type": "discarded"})
            except Exception:
                current.stop()
                with suppress(Exception):
                    await send(
                        {
                            "type": "error",
                            "fatal": True,
                            "message": "Camera processing stopped. Check camera access and models.",
                        }
                    )
                with suppress(Exception):
                    await ws.close(code=1011)

        try:
            while True:
                raw = await asyncio.wait_for(ws.receive_text(), timeout=30)
                if len(raw) > 8192:
                    await ws.close(code=1009)
                    break
                try:
                    message = json.loads(raw)
                    if not isinstance(message, dict):
                        raise ValueError("Expected a command object")
                    command = message.get("type")
                    if command == "start":
                        if session or camera_owner.locked():
                            raise ValueError("A camera session is already running")
                        index = message.get("camera_index", 0)
                        if type(index) is not int or not 0 <= index <= 10:
                            raise ValueError("Camera index must be an integer from 0 to 10")
                        await camera_owner.acquire()
                        owns_camera = True
                        backend = backend_factory()
                        try:
                            load_ms = await loop.run_in_executor(executor, backend.open, index)
                        except Exception:
                            await close_camera()
                            raise ValueError(
                                "Cannot start camera. Download MediaPipe models, check the camera "
                                "index, and allow camera access for this terminal."
                            ) from None
                        session = DashboardSession()
                        await send(
                            {"type": "started", "model_load_ms": load_ms, **session.status()}
                        )
                    elif command == "stop":
                        await close_camera()
                        await send({"type": "stopped"})
                    elif not session or not session.running:
                        raise ValueError("Start the camera first")
                    elif command == "frame":
                        if pending and not pending.done():
                            await send({"type": "busy"})
                        else:
                            pending = asyncio.create_task(produce(session, session.token))
                    elif command == "configure":
                        session.configure(
                            message.get("mapping", {}), message.get("simulate", False)
                        )
                        await send({"type": "configured", **session.status()})
                    elif command == "calibrate":
                        session.calibrate(message.get("label"))
                        await send({"type": "calibrating", **session.status()})
                    elif command == "cancel":
                        session.cancel()
                        await send({"type": "cancelled", **session.status()})
                    elif command == "compare":
                        await send(session.compare())
                    else:
                        raise ValueError("Unknown command")
                except (ValueError, TypeError):
                    # Avoid reflecting arbitrary objects, paths or oversized input to the UI.
                    await send(
                        {
                            "type": "error",
                            "fatal": False,
                            "message": "Command rejected. Check camera availability, model "
                            "downloads, current frame, and experiment settings.",
                        }
                    )
        except (TimeoutError, WebSocketDisconnect, RuntimeError):
            pass
        finally:
            await close_camera()
            with suppress(Exception):
                await ws.close()
            executor.shutdown(wait=False, cancel_futures=True)

    return app


app = create_app()
