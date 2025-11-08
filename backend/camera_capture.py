import threading
import time
from typing import Optional, Tuple

import cv2
import numpy as np

from backend.app import health_state, set_preview_frame


class CameraCapture:
    """Background camera reader keeping a preview buffer and lighting metric."""

    def __init__(self, width: int = 1280, height: int = 720, fps: int = 30, device: int = 0) -> None:
        self.width = width
        self.height = height
        self.fps = fps
        self.device = device
        api_preference = cv2.CAP_V4L2 if hasattr(cv2, "CAP_V4L2") else cv2.CAP_ANY
        self._capture = cv2.VideoCapture(self.device, api_preference)
        self._configure_capture()
        self._frame_lock = threading.Lock()
        self._latest_frame: Optional[np.ndarray] = None
        self._latest_ts: Optional[int] = None
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _configure_capture(self) -> None:
        if not self._capture.isOpened():
            raise RuntimeError("CameraCapture: unable to open device")
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self._capture.set(cv2.CAP_PROP_FPS, self.fps)

    def _run(self) -> None:
        target_period = 1.0 / float(self.fps or 30)
        fps_alpha = 0.2
        while not self._stop_event.is_set():
            start = time.time()
            ok, frame_bgr = self._capture.read()
            timestamp_ns = time.time_ns()
            if not ok:
                time.sleep(0.05)
                continue

            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            luminance = float(gray.mean())
            lighting = "ok" if luminance > 60 else "dim"
            health_state.lighting = lighting
            health_state.camera = "on"

            with self._frame_lock:
                self._latest_frame = frame_rgb
                self._latest_ts = timestamp_ns
                _, buffer = cv2.imencode(".jpg", frame_bgr)
                # Set preview for FastAPI endpoint.
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
        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self._capture.isOpened():
            self._capture.release()
        health_state.camera = "off"

    def __del__(self) -> None:  # pragma: no cover
        self.close()
