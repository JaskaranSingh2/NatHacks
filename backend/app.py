import asyncio
import contextlib
import importlib.util
import json
import logging
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import lru_cache
from threading import Lock
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field, validator

LOGGER = logging.getLogger("assistivecoach.backend")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="Assistive Coach Backend", version="0.1.0")

ALLOWED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Anchor(BaseModel):
    landmark: Optional[str] = None
    aruco_id: Optional[int] = Field(default=None, ge=0)
    pixel: Optional[Dict[str, float]] = None

    @validator("pixel")
    def validate_pixel(cls, value: Optional[Dict[str, float]]) -> Optional[Dict[str, float]]:
        if value is None:
            return value
        if not {"x", "y"}.issubset(value.keys()):
            raise ValueError("pixel anchor must include x and y")
        return value

    @validator("landmark")
    def validate_landmark(cls, value: Optional[str], values: Dict[str, object]) -> Optional[str]:
        if value and values.get("aruco_id") is not None:
            raise ValueError("Anchor cannot define both landmark and aruco_id")
        return value


class Shape(BaseModel):
    kind: str
    anchor: Anchor
    to: Optional[Anchor] = None
    radius_px: Optional[int] = Field(default=None, ge=0)
    accent: Optional[str] = None
    text: Optional[str] = None

    @validator("kind")
    def validate_kind(cls, value: str) -> str:
        allowed = {"ring", "arrow", "badge"}
        if value not in allowed:
            raise ValueError(f"Shape kind must be one of {sorted(allowed)}")
        return value

    @validator("to")
    def validate_to(cls, value: Optional[Anchor], values: Dict[str, object]) -> Optional[Anchor]:
        if values.get("kind") == "arrow" and value is None:
            raise ValueError("Arrow shapes require a 'to' anchor")
        return value


class HUDPayload(BaseModel):
    title: Optional[str] = None
    step: Optional[str] = None
    subtitle: Optional[str] = None
    time_left_s: Optional[int] = Field(default=None, ge=0)
    hint: Optional[str] = None


class OverlayMessage(BaseModel):
    type: str
    shapes: Optional[List[Shape]] = None
    hud: Optional[HUDPayload] = None
    camera: Optional[str] = None
    lighting: Optional[str] = None
    fps: Optional[float] = None
    ar_overlays: Optional[bool] = None
    detectors: Optional[Dict[str, bool]] = None
    text: Optional[str] = None
    level: Optional[str] = None
    reason: Optional[str] = None

    @validator("type")
    def validate_type(cls, value: str) -> str:
        allowed = {"overlay.set", "status", "tts", "safety.alert"}
        if value not in allowed:
            raise ValueError(f"Unsupported message type: {value}")
        return value


class OverlayRequest(BaseModel):
    message: OverlayMessage


class TTSRequest(BaseModel):
    text: str

    @validator("text")
    def validate_text(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Text cannot be empty")
        return trimmed


class SessionRequest(BaseModel):
    patient_id: Optional[str]
    routine_id: Optional[str]


class SettingsPayload(BaseModel):
    use_cloud: Optional[bool] = None
    face: Optional[bool] = None
    hands: Optional[bool] = None
    aruco: Optional[bool] = None
    pose: Optional[bool] = None
    cloud_rps: Optional[int] = Field(default=None, ge=1, le=10)
    cloud_timeout_s: Optional[float] = Field(default=None, ge=0.1, le=3.0)
    cloud_min_interval_ms: Optional[int] = Field(default=None, ge=0)


class HealthState(BaseModel):
    camera: str = "off"
    lighting: str = "unknown"
    fps: float = 0.0
    latency_ms: float = 0.0
    last_frame_ns: Optional[int] = None
    cloud_enabled: bool = False
    cloud_ok_count: int = 0
    cloud_fail_count: int = 0
    cloud_breaker_open: bool = False
    cloud_latency_ms: float = 0.0
    cloud_last_ok_ns: Optional[int] = None
    # Hotfix additions
    mock_camera: bool = False
    camera_error: Optional[str] = None


class HealthResponse(BaseModel):
    camera: str
    lighting: str
    fps: float
    latency_ms: float
    vision_state: Optional[Dict[str, Any]] = None
    cloud: Optional[Dict[str, Any]] = None
    mock_camera: bool
    camera_error: Optional[str] = None
    pose_requested: Optional[bool] = None
    pose_available: Optional[bool] = None
    intrinsics_error: Optional[str] = None


class SettingsState(BaseModel):
    use_cloud: bool = False
    face: bool = True
    hands: bool = True
    aruco: bool = False
    pose: bool = True
    cloud_rps: int = 2
    cloud_timeout_s: float = 0.8
    cloud_min_interval_ms: int = 600


class SessionState(BaseModel):
    patient_id: Optional[str] = None
    routine_id: Optional[str] = None
    started_at: Optional[datetime] = None
    step_index: int = 0


class ConnectionManager:
    def __init__(self) -> None:
        self._active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._active_connections.append(websocket)
        LOGGER.info("WebSocket client connected. active=%d", len(self._active_connections))

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            if websocket in self._active_connections:
                self._active_connections.remove(websocket)
        LOGGER.info("WebSocket client disconnected. active=%d", len(self._active_connections))

    async def broadcast(self, message: Dict[str, object]) -> None:
        payload = json.dumps(message)
        async with self._lock:
            websockets = list(self._active_connections)
        for connection in websockets:
            try:
                await connection.send_text(payload)
            except Exception as exc:  # pragma: no cover - defensive log
                LOGGER.warning("Failed to send WS message: %s", exc)


settings_state = SettingsState()
health_state = HealthState()
session_state = SessionState()
manager = ConnectionManager()
_executor = ThreadPoolExecutor(max_workers=4)
_preview_buffer: Optional[bytes] = None
_preview_lock = Lock()
_message_queue: Optional["asyncio.Queue[Dict[str, object]]"] = None
_broadcast_task: Optional[asyncio.Task] = None
_event_loop: Optional[asyncio.AbstractEventLoop] = None


async def _broadcast_worker() -> None:
    global _message_queue
    if _message_queue is None:
        LOGGER.warning("Broadcast queue not initialised; worker exiting")
        return
    LOGGER.info("Broadcast worker started")
    while True:
        message = await _message_queue.get()
        try:
            await manager.broadcast(message)
        finally:
            _message_queue.task_done()


def queue_broadcast(message: Dict[str, object]) -> None:
    global _message_queue, _event_loop
    if _message_queue is None:
        LOGGER.warning("Broadcast queue not ready; dropping message")
        return
    try:
        running_loop = asyncio.get_running_loop()
    except RuntimeError:
        running_loop = None

    if running_loop and running_loop is _event_loop:
        try:
            _message_queue.put_nowait(message)
        except asyncio.QueueFull:  # pragma: no cover - defensive log
            LOGGER.warning("Broadcast queue full; dropping message")
        return

    if _event_loop is None:
        LOGGER.warning("Broadcast loop not ready; dropping message")
        return

    def _enqueue() -> None:
        if _message_queue is None:
            return
        if _message_queue.full():  # pragma: no cover - overflow guard
            LOGGER.warning("Broadcast queue full; dropping message")
            return
        _message_queue.put_nowait(message)

    _event_loop.call_soon_threadsafe(_enqueue)


async def broadcast(message: Dict[str, object]) -> None:
    queue_broadcast(message)


def set_preview_frame(jpeg_bytes: bytes) -> None:
    global _preview_buffer
    with _preview_lock:
        _preview_buffer = jpeg_bytes


async def get_preview_frame() -> Optional[bytes]:
    global _preview_buffer
    with _preview_lock:
        return _preview_buffer


@lru_cache
def _detect_speech_engine() -> str:
    if shutil and shutil.which("espeak-ng"):
        return "espeak-ng"
    if importlib.util.find_spec("pyttsx3") is not None:
        return "pyttsx3"
    return ""


try:
    import shutil
except ImportError:  # pragma: no cover
    shutil = None  # type: ignore


_speech_engine = _detect_speech_engine()


def _speak_espeak(text: str) -> None:
    try:
        subprocess.run(
            [_speech_engine, text],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as exc:
        LOGGER.error("espeak-ng failed: %s", exc)
        raise


def _speak_pyttsx(text: str) -> None:
    try:
        import pyttsx3  # type: ignore[import]
    except ImportError as exc:  # pragma: no cover - optional dependency
        LOGGER.error("pyttsx3 unavailable: %s", exc)
        return

    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def _speak_system(text: str) -> bool:
    """Platform-aware TTS; returns True if spoken, False otherwise."""
    try:
        import shutil as _sh
    except ImportError:
        _sh = None  # type: ignore
    sysname = platform.system()
    if sysname == "Darwin":
        try:
            subprocess.run(["say", text], check=True)
            return True
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("macOS say failed: %s", exc)
            return False
    if sysname == "Linux" and _sh and _sh.which("espeak-ng"):
        try:
            subprocess.run(["espeak-ng", text], check=True)
            return True
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("espeak-ng failed: %s", exc)
            return False
    return False


def speak_text(text: str) -> None:
    # Try system first
    if _speak_system(text):
        return
    # Fallback chain
    if _speech_engine == "pyttsx3":
        try:
            _speak_pyttsx(text)
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("pyttsx3 fallback failed: %s", exc)
    elif _speech_engine:
        try:
            _speak_espeak(text)
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("espeak-ng fallback failed: %s", exc)
    else:
        LOGGER.warning("No TTS engine available; skipping")


@app.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    vision_state = None
    if _vision_pipeline:
        vision_state = {
            "fps": health_state.fps,
            "latency_ms": health_state.latency_ms,
            "last_frame_ns": health_state.last_frame_ns,
        }
    cloud_state = None
    if health_state.cloud_enabled or health_state.cloud_latency_ms > 0:
        cloud_state = {
            "enabled": health_state.cloud_enabled,
            "latency_ms": health_state.cloud_latency_ms,
            "ok_count": health_state.cloud_ok_count,
            "fail_count": health_state.cloud_fail_count,
            "breaker_open": health_state.cloud_breaker_open,
            "last_ok_ns": health_state.cloud_last_ok_ns,
        }

    # Try to fetch last aruco meta from pipeline if present
    pose_requested = getattr(settings_state, "pose", False)
    pose_available = False
    intrinsics_error = None
    if _vision_pipeline is not None:
        meta = getattr(_vision_pipeline, "_aruco_last_meta", None)
        if isinstance(meta, dict):
            pose_available = bool(meta.get("pose_available", False))
            intrinsics_error = meta.get("intrinsics_error")
    # Fallback: if pose requested but unavailable and no intrinsics_error captured yet, surface cached loader error
    if pose_requested and not pose_available and not intrinsics_error:
        try:
            from backend import ar_overlay as _aru
            intrinsics_error = getattr(_aru, "_INTRINSICS_ERR", intrinsics_error)
        except Exception:  # pragma: no cover
            pass

    return HealthResponse(
        camera=health_state.camera,
        lighting=health_state.lighting,
        fps=health_state.fps,
        latency_ms=health_state.latency_ms,
        vision_state=vision_state,
        cloud=cloud_state,
        mock_camera=health_state.mock_camera,
        camera_error=health_state.camera_error,
        pose_requested=pose_requested,
        pose_available=pose_available,
        intrinsics_error=intrinsics_error,
    )


@app.post("/session/start")
async def start_session(payload: SessionRequest) -> JSONResponse:
    session_state.patient_id = payload.patient_id
    session_state.routine_id = payload.routine_id
    session_state.started_at = datetime.utcnow()
    session_state.step_index = 0
    LOGGER.info("Session started: %s", session_state.dict())
    
    # Send initial status
    await broadcast(
        {
            "type": "status",
            "camera": health_state.camera,
            "lighting": health_state.lighting,
            "fps": health_state.fps,
        }
    )
    
    # Immediately push Step 1 HUD (vision pipeline will add shapes on next frame)
    if _vision_pipeline and payload.routine_id:
        try:
            # Load routine to get first step
            from pathlib import Path
            import json
            tasks_path = Path(__file__).resolve().parents[1] / "config" / "tasks.json"
            if tasks_path.exists():
                with tasks_path.open("r") as f:
                    tasks = json.load(f)
                    routine_steps = tasks.get(payload.routine_id, [])
                    if routine_steps and len(routine_steps) > 0:
                        step = routine_steps[0]
                        await broadcast({
                            "type": "overlay.set",
                            "shapes": [],  # Vision pipeline will add shapes
                            "hud": {
                                "title": step.get("title"),
                                "step": f"Step 1 of {len(routine_steps)}",
                                "subtitle": step.get("subtitle"),
                                "time_left_s": step.get("min_time_s"),
                                "max_time_s": step.get("min_time_s"),
                                "hint": step.get("hint"),
                            }
                        })
        except Exception as exc:
            LOGGER.warning("Failed to send initial HUD: %s", exc)
    
    return JSONResponse({"status": "started", "session": session_state.dict()})


@app.post("/session/next_step")
async def next_step() -> JSONResponse:
    session_state.step_index += 1
    LOGGER.info("Advanced to step %d", session_state.step_index)
    return JSONResponse({"step_index": session_state.step_index})


@app.post("/session/prev_step")
async def prev_step() -> JSONResponse:
    session_state.step_index = max(0, session_state.step_index - 1)
    LOGGER.info("Rewound to step %d", session_state.step_index)
    return JSONResponse({"step_index": session_state.step_index})


@app.post("/overlay")
async def post_overlay(raw: Dict[str, Any]) -> JSONResponse:
    # Accept either {"message": {...}} or raw overlay payload
    if "message" in raw and isinstance(raw["message"], dict):
        payload = raw["message"]
    else:
        payload = raw
    if "type" not in payload:
        # Wrap arbitrary payload
        payload = {
            "type": "overlay.set",
            "shapes": [],
            "hud": payload,
        }
    await broadcast(payload)
    LOGGER.info("Broadcast overlay message %s", payload.get("type"))
    return JSONResponse({"ok": True})


@app.post("/tts")
async def post_tts(payload: TTSRequest) -> JSONResponse:
    text = payload.text.strip()

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(_executor, speak_text, text)

    await broadcast({"type": "tts", "text": text})
    LOGGER.info("Queued TTS text length=%d", len(text))
    return JSONResponse({"status": "ok"})


@app.post("/settings")
async def update_settings(payload: SettingsPayload) -> JSONResponse:
    updated = payload.dict(exclude_none=True)
    for key, value in updated.items():
        setattr(settings_state, key, value)
    if _vision_pipeline and {"cloud_rps", "cloud_timeout_s", "cloud_min_interval_ms"}.intersection(updated):
        try:
            _vision_pipeline.refresh_cloud_limits()
        except Exception as exc:
            LOGGER.warning("Failed to refresh cloud limits: %s", exc)
    LOGGER.info("Settings updated: %s", updated)
    return JSONResponse(settings_state.dict())


@app.get("/preview.jpg")
async def get_preview() -> Response:
    frame = await get_preview_frame()
    if frame is None:
        raise HTTPException(status_code=404, detail="Preview unavailable")
    return Response(content=frame, media_type="image/jpeg")


@app.websocket("/ws/mirror")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as exc:  # pragma: no cover - defensive log
        LOGGER.warning("WebSocket error: %s", exc)
        await manager.disconnect(websocket)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    global _vision_pipeline
    LOGGER.info("Shutting down backend")
    
    # Stop vision pipeline
    if _vision_pipeline:
        try:
            _vision_pipeline.stop()
            LOGGER.info("Vision pipeline stopped")
        except Exception as exc:
            LOGGER.error("Error stopping vision pipeline: %s", exc)
    
    _executor.shutdown(wait=False)
    if _broadcast_task:
        _broadcast_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await _broadcast_task


_vision_pipeline: Optional[Any] = None


@app.on_event("startup")
async def on_startup() -> None:
    global _broadcast_task, _message_queue, _event_loop, _vision_pipeline
    _event_loop = asyncio.get_running_loop()
    _message_queue = asyncio.Queue(maxsize=256)
    _broadcast_task = asyncio.create_task(_broadcast_worker())
    
    # Start vision pipeline
    try:
        from backend.vision_pipeline import VisionPipeline
        _vision_pipeline = VisionPipeline(
            broadcast_fn=queue_broadcast,
            settings=settings_state,
            session=session_state,
            health=health_state,
            camera_width=1280,
            camera_height=720,
            camera_fps=24,
            camera_device=0
        )
        _vision_pipeline.start()
        LOGGER.info("Vision pipeline started successfully")
    except Exception as exc:
        LOGGER.error("Failed to start vision pipeline: %s", exc)
        # Attempt synthetic fallback so overlays & health still work
        try:
            from backend.vision_pipeline import VisionPipeline
            _vision_pipeline = VisionPipeline(
                broadcast_fn=queue_broadcast,
                settings=settings_state,
                session=session_state,
                health=health_state,
                camera_width=1280,
                camera_height=720,
                camera_fps=24,
                camera_device=0,
                camera_enabled=False,
            )
            _vision_pipeline.start()
            LOGGER.info("Vision pipeline started in synthetic (mock) mode")
            health_state.camera = "mock"
            health_state.mock_camera = True
        except Exception as inner:
            LOGGER.error("Synthetic fallback failed: %s", inner)
            _vision_pipeline = None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host="0.0.0.0", port=5055, reload=False)
