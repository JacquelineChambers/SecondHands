"""Scene exploration protocol sharing exclusive camera ownership with gestures."""

import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


def options_from(message):
    options = {
        "source": message.get("source", "orbbec"),
        "camera_index": message.get("camera_index", 0),
        "pose": message.get("pose", True),
        "objects": message.get("objects", True),
        "scene_model": message.get("scene_model", True),
    }
    if options["source"] not in ("orbbec", "opencv"):
        raise ValueError("Choose Orbbec or a standard camera")
    if type(options["camera_index"]) is not int or not 0 <= options["camera_index"] <= 10:
        raise ValueError("Camera index must be from 0 to 10")
    if any(type(options[key]) is not bool for key in ("pose", "objects", "scene_model")):
        raise ValueError("Model settings must be enabled or disabled")
    return options


def install_scene(app, camera_owner, origins, backend_factory):
    @app.websocket("/api/scene")
    async def scene_socket(ws: WebSocket):
        if ws.headers.get("origin") not in origins:
            await ws.close(code=1008)
            return
        await ws.accept()
        executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="scene-camera")
        loop = asyncio.get_running_loop()
        backend = None
        pending = None
        owns_camera = False
        session_id = None
        frame_id = 0
        send_lock = asyncio.Lock()

        async def send(payload):
            async with send_lock:
                await asyncio.wait_for(ws.send_json(payload), timeout=5)

        async def stop():
            nonlocal backend, pending, session_id, owns_camera
            session_id = None
            if pending:
                with suppress(Exception):
                    await asyncio.shield(pending)
                pending = None
            try:
                if backend:
                    await asyncio.shield(loop.run_in_executor(executor, backend.close))
            finally:
                backend = None
                if owns_camera:
                    camera_owner.release()
                    owns_camera = False

        async def produce(token):
            nonlocal frame_id
            try:
                result = await loop.run_in_executor(executor, backend.frame)
                if token == session_id:
                    frame_id += 1
                    await send(
                        {"type": "frame", "session_id": token, "frame_id": frame_id, **result}
                    )
            except Exception:
                logger.exception("Scene camera processing failed")
                with suppress(Exception):
                    await send(
                        {
                            "type": "error",
                            "fatal": True,
                            "message": "Camera processing stopped. Check USB, camera ownership, "
                            "and model files.",
                        }
                    )
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
                        raise ValueError("Expected a command")
                    command = message.get("type")
                    if command == "start":
                        options = options_from(message)
                        if backend or camera_owner.locked():
                            raise ValueError("Another camera session is running. Stop it first.")
                        await camera_owner.acquire()
                        owns_camera = True
                        backend = backend_factory()
                        try:
                            info = await loop.run_in_executor(executor, backend.open, options)
                        except Exception:
                            logger.exception("Scene camera startup failed")
                            await stop()
                            raise ValueError(
                                "Cannot start. Check the camera connection, installed bridge, "
                                "and enabled model files."
                            ) from None
                        session_id = uuid4().hex
                        frame_id = 0
                        await send({"type": "started", "session_id": session_id, **info})
                    elif command == "stop":
                        await stop()
                        await send({"type": "stopped"})
                    elif command == "frame" and backend:
                        if pending and not pending.done():
                            await send({"type": "busy"})
                        else:
                            pending = asyncio.create_task(produce(session_id))
                    else:
                        raise ValueError("Start the scene camera first")
                except (ValueError, TypeError) as error:
                    await send({"type": "error", "fatal": False, "message": str(error)[:180]})
        except (TimeoutError, WebSocketDisconnect, RuntimeError):
            pass
        finally:
            await stop()
            with suppress(Exception):
                await ws.close()
            executor.shutdown(wait=False, cancel_futures=True)
