import logging
import os
import platform
import threading
import time
from typing import Optional, Tuple

import cv2
import numpy as np

from backend.app import health_state, set_preview_frame

LOGGER = logging.getLogger("assistivecoach.camera")


class CameraCapture:
    """Background camera reader keeping a preview buffer and lighting metric.

    If a physical camera can't be opened and ALLOW_MOCK is true (default),
    the capture will synthesize frames so downstream systems can run.
    """

    def __init__(self, width: int = 1280, height: int = 720, fps: int = 30, device: int = 0) -> None:
        # Always initialize synchronization primitives first
        self._frame_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._latest_frame: Optional[np.ndarray] = None
        self._latest_ts: Optional[int] = None

        # Config
        env_idx = os.getenv("CAM_INDEX")
        try:
            env_idx_val = int(env_idx) if env_idx is not None else device
        except ValueError:
            env_idx_val = device
        self.width = width
        self.height = height
        self.fps = fps
        self.device = env_idx_val
        self.allow_mock = str(os.getenv("ALLOW_MOCK", "true")).lower() not in {"0", "false", "no"}
        self.mock = False
        self.last_error: Optional[str] = None

        # Try opening with a matrix of backends based on platform
        self._capture = None  # type: ignore[assignment]
        opened = False
        backend_candidates = []
        sysname = platform.system()
        if sysname == "Darwin":
            if hasattr(cv2, "CAP_AVFOUNDATION"):
                backend_candidates.append(cv2.CAP_AVFOUNDATION)
        elif sysname == "Linux":
            if hasattr(cv2, "CAP_V4L2"):
                backend_candidates.append(cv2.CAP_V4L2)
        # Always include CAP_ANY fallback
        backend_candidates.append(getattr(cv2, "CAP_ANY", 0))

        for backend in backend_candidates:
            try:
                cap = cv2.VideoCapture(self.device, backend)
                if cap is not None and cap.isOpened():
                    self._capture = cap
                    opened = True
                    break
                if cap is not None:
                    cap.release()
            except Exception as exc:
                # Continue trying other backends
                LOGGER.debug("Backend %s failed, trying next: %s", backend, exc)

        if opened:
            try:
                self._configure_capture()
                health_state.camera = "on"
                health_state.mock_camera = False
                health_state.camera_error = None
            except Exception as exc:
                # Configuration failed; decide whether to fall back to mock
                self.last_error = f"configure failed: {exc}"
                if self.allow_mock:
                    self._capture = None
                    self.mock = True
                    health_state.camera = "mock"
                    health_state.mock_camera = True
                    health_state.camera_error = self.last_error
                else:
                    raise
        else:
            self.last_error = "unable to open device"
            if self.allow_mock:
                self.mock = True
                health_state.camera = "mock"
                health_state.mock_camera = True
                health_state.camera_error = self.last_error
            else:
                raise RuntimeError("CameraCapture: unable to open device")

        # Start thread
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _configure_capture(self) -> None:
        if self._capture is None or not self._capture.isOpened():
            raise RuntimeError("CameraCapture: unable to open device")
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self._capture.set(cv2.CAP_PROP_FPS, self.fps)

    def _run(self) -> None:
        target_period = 1.0 / float(self.fps or 30)
        fps_alpha = 0.2
        while not self._stop_event.is_set():
            start = time.time()
            timestamp_ns = time.time_ns()
            if self.mock or self._capture is None:
                # Synthetic frame with moving dot and timestamp
                frame_rgb = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                t = time.time()
                x = int((0.5 + 0.4 * np.sin(t)) * self.width)
                y = int((0.5 + 0.4 * np.cos(t)) * self.height)
                cv2.circle(frame_rgb, (x, y), 20, (0, 255, 0), -1)
                cv2.putText(
                    frame_rgb,
                    time.strftime("%H:%M:%S"),
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
                health_state.camera = "mock"
                health_state.mock_camera = True
                health_state.camera_error = self.last_error
                gray = cv2.cvtColor(cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
            else:
                ok, frame_bgr = self._capture.read()
                if not ok:
                    # brief pause then try again
                    time.sleep(0.05)
                    continue
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
                health_state.camera = "on"
                health_state.mock_camera = False
                health_state.camera_error = None

            luminance = float(gray.mean())
            lighting = "ok" if luminance > 60 else "dim"
            health_state.lighting = lighting

            with self._frame_lock:
                self._latest_frame = frame_rgb
                self._latest_ts = timestamp_ns
                # Preview expects BGR
                prev_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                _, buffer = cv2.imencode(".jpg", prev_bgr)
                set_preview_frame(bytes(buffer))

            elapsed = time.time() - start
            current_fps = 1.0 / elapsed if elapsed > 0 else float(self.fps)
            health_state.fps = (
                fps_alpha * current_fps + (1 - fps_alpha) * health_state.fps
            )
            sleep_time = max(0.0, target_period - elapsed)
            time.sleep(sleep_time)

    def read(self) -> Tuple[np.ndarray, int]:
        with self._frame_lock:
            if self._latest_frame is None or self._latest_ts is None:
                raise RuntimeError("Camera frame not ready")
            frame = self._latest_frame.copy()
            ts = int(self._latest_ts)
        return frame, ts

    def get_preview_jpeg(self) -> Optional[bytes]:
        with self._frame_lock:
            if self._latest_frame is None:
                return None
            frame_bgr = cv2.cvtColor(self._latest_frame, cv2.COLOR_RGB2BGR)
            ok, buffer = cv2.imencode(".jpg", frame_bgr)
            if not ok:
                return None
            return bytes(buffer)

    def close(self) -> None:
        try:
            if hasattr(self, "_stop_event"):
                self._stop_event.set()
            if hasattr(self, "_thread") and getattr(self, "_thread", None) is not None:
                if self._thread.is_alive():
                    self._thread.join(timeout=1.0)
            cap = getattr(self, "_capture", None)
            if cap is not None and hasattr(cap, "isOpened") and cap.isOpened():
                cap.release()
        except Exception as exc:
            # Ensure teardown never crashes
            LOGGER.debug("Camera release error (ignored): %s", exc)
        finally:
            health_state.camera = "off"
            health_state.mock_camera = False
            # keep last error for health visibility

    def __del__(self) -> None:  # pragma: no cover
        try:
            self.close()
        except Exception as exc:
            LOGGER.debug("Camera cleanup error (ignored): %s", exc)
