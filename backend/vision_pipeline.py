"""
Vision Pipeline for CV Smart Mirror
Processes camera frames with MediaPipe Face Mesh & Hands for real-time AR overlays.
"""
import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import cv2
import numpy as np

LOGGER = logging.getLogger("assistivecoach.vision")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEATURES_PATH = PROJECT_ROOT / "config" / "features.json"
TASKS_PATH = PROJECT_ROOT / "config" / "tasks.json"
LOGS_PATH = PROJECT_ROOT / "logs" / "latency.csv"


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        LOGGER.warning("Missing configuration file: %s", path)
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class VisionPipeline:
    """
    Processes camera frames with MediaPipe Face Mesh & Hands.
    Emits overlay messages via broadcast callback.
    Target: <150ms capture→overlay latency on Pi 4/5.
    """

    def __init__(
        self,
        broadcast_fn: Callable[[Dict[str, Any]], None],
        settings: Any,
        session: Any,
        health: Any,
        camera_width: int = 1280,
        camera_height: int = 720,
        camera_fps: int = 24,
        camera_device: int = 0,
    ) -> None:
        """
        Initialize vision pipeline.
        
        Args:
            broadcast_fn: Callback to send overlay messages (queue_broadcast from app.py)
            settings: Settings state object with flags (use_cloud, face, hands, aruco)
            session: Session state object (routine_id, step_index)
            health: Health state object to update (fps, latency_ms, etc.)
            camera_width: Camera resolution width (default 1280 for 720p)
            camera_height: Camera resolution height (default 720)
            camera_fps: Target FPS (24-30 recommended for Pi)
            camera_device: Camera device index
        """
        self.broadcast_fn = broadcast_fn
        self.settings = settings
        self.session = session
        self.health = health
        
        # Initialize camera
        from backend.camera_capture import CameraCapture
        self.camera = CameraCapture(camera_width, camera_height, camera_fps, camera_device)
        self.frame_w = camera_width
        self.frame_h = camera_height
        
        # Load configuration
        features_raw = _load_json(FEATURES_PATH)
        tasks_raw = _load_json(TASKS_PATH)
        self._features: Dict[str, Any] = features_raw if isinstance(features_raw, dict) else {}
        self._tasks: Dict[str, Any] = tasks_raw if isinstance(tasks_raw, dict) else {}
        
        # Thread control
        self._running = False
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        
        # EMA smoothing state (alpha=0.4 for good responsiveness vs stability)
        self._ema: Dict[str, Tuple[float, float]] = {}
        self._alpha = 0.4
        
        # Face detection state for ROI optimization
        self._last_face_bbox: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)
        self._no_face_since: Optional[float] = None
        
        # Initialize MediaPipe models
        self._mediapipe = self._init_mediapipe()
        self._hand_detector = self._init_hands()
        self._cloud_client = self._detect_cloud_client()
        
        # Ensure logs directory exists
        LOGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize CSV header if file doesn't exist
        if not LOGS_PATH.exists():
            with LOGS_PATH.open("w", encoding="utf-8") as f:
                f.write("capture_ts,landmark_ts,overlay_ts,e2e_ms,fps,use_cloud\n")
        
        LOGGER.info("VisionPipeline initialized: %dx%d @ %dfps", camera_width, camera_height, camera_fps)

    def _init_mediapipe(self) -> Any:  # pragma: no cover
        """Initialize MediaPipe Face Mesh detector."""
        try:
            import mediapipe as mp  # type: ignore[import]
            face_mesh = mp.solutions.face_mesh.FaceMesh(
                refine_landmarks=True,
                max_num_faces=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            LOGGER.info("MediaPipe Face Mesh initialized")
            return face_mesh
        except ImportError:
            LOGGER.warning("MediaPipe not available; using synthetic mode")
            return None

    def _init_hands(self) -> Any:  # pragma: no cover
        """Initialize MediaPipe Hands detector."""
        try:
            import mediapipe as mp  # type: ignore[import]
            hands = mp.solutions.hands.Hands(
                max_num_hands=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            LOGGER.info("MediaPipe Hands initialized")
            return hands
        except ImportError:
            LOGGER.warning("MediaPipe Hands not available")
            return None

    def _detect_cloud_client(self) -> Any:  # pragma: no cover
        """Detect Google Cloud Vision client (optional)."""
        try:
            from google.cloud import vision  # type: ignore[import]
            client = vision.ImageAnnotatorClient()  # type: ignore[attr-defined]
            LOGGER.info("Google Cloud Vision client available")
            return client
        except Exception as exc:
            LOGGER.debug("Google Cloud Vision unavailable: %s", exc)
            return None

    def start(self) -> None:
        """Start the vision pipeline background thread."""
        if self._running:
            LOGGER.warning("Vision pipeline already running")
            return
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="VisionPipeline")
        self._thread.start()
        LOGGER.info("Vision pipeline started")

    def stop(self) -> None:
        """Stop the vision pipeline and clean up resources."""
        if not self._running:
            return
        LOGGER.info("Stopping vision pipeline...")
        self._running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self.camera.close()
        LOGGER.info("Vision pipeline stopped")

    def _run(self) -> None:  # pragma: no cover - involves hardware
        """Main processing loop running in background thread."""
        LOGGER.info("Vision pipeline processing loop started")
        frame_count = 0
        
        while self._running and not self._stop_event.is_set():
            try:
                # Grab latest frame
                frame_rgb, capture_ts_ns = self.camera.read()
                capture_ts = capture_ts_ns / 1e9  # Convert to seconds
            except RuntimeError:
                # Camera not ready yet
                if not self._stop_event.wait(0.05):
                    continue
                break
            
            frame_count += 1
            landmark_start = time.time()
            
            # Get frame dimensions
            frame_h, frame_w = frame_rgb.shape[:2]
            self.frame_w = frame_w
            self.frame_h = frame_h
            
            # ROI optimization: crop around last known face
            roi_frame, roi_offset = self._apply_roi(frame_rgb)
            
            # Process landmarks (MediaPipe or synthetic mode)
            landmarks = self._process_landmarks(roi_frame, roi_offset)
            
            # Process hands if enabled
            hand_landmarks = {}
            if self.settings.hands and self._hand_detector:
                hand_landmarks = self._process_hands(roi_frame, roi_offset)
            
            # Detect ArUco markers if enabled
            ar_anchors = []
            if self.settings.aruco:
                try:
                    from backend.ar_overlay import detect_aruco_anchors
                    ar_anchors = detect_aruco_anchors(frame_rgb)
                except (RuntimeError, ImportError) as exc:
                    LOGGER.debug("ArUco detection unavailable: %s", exc)
            
            landmark_ts = time.time()
            
            # Build overlay message
            all_landmarks = {**landmarks, **hand_landmarks}
            overlay_shapes = self._build_shapes(all_landmarks, frame_w, frame_h, ar_anchors)
            hud = self._build_hud()
            
            message = {
                "type": "overlay.set",
                "shapes": overlay_shapes,
                "hud": hud,
            }
            
            # Broadcast overlay
            self.broadcast_fn(message)
            overlay_ts = time.time()
            
            # Update health metrics
            e2e_ms = (overlay_ts - capture_ts) * 1000.0
            self.health.latency_ms = e2e_ms
            
            # Log to CSV
            self._log_latency(capture_ts, landmark_ts, overlay_ts, e2e_ms)
            
            # Check for "no face" condition
            if not landmarks and self.settings.face:
                if self._no_face_since is None:
                    self._no_face_since = time.time()
                elif (time.time() - self._no_face_since) > 2.0:
                    # No face for 2 seconds - send hint
                    if frame_count % 30 == 0:  # Don't spam, send every ~1 sec at 30fps
                        self._send_no_face_hint()
            else:
                self._no_face_since = None
            
            # Frame drop handling: if processing is lagging, we naturally drop frames
            # because camera.read() always returns latest frame
            if e2e_ms > 150:
                LOGGER.warning("Frame %d exceeded latency target: %.1fms", frame_count, e2e_ms)
        
        LOGGER.info("Vision pipeline processing loop exited")

    def _apply_roi(self, frame: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int]]:
        """
        Apply ROI crop around last known face for faster processing.
        Returns: (cropped_frame, (x_offset, y_offset))
        """
        if self._last_face_bbox is None:
            # First frame or lost tracking - use full frame
            return frame, (0, 0)
        
        # Expand bbox by 20% with padding
        x, y, w, h = self._last_face_bbox
        pad_w = int(w * 0.2)
        pad_h = int(h * 0.2)
        
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(frame.shape[1], x + w + pad_w)
        y2 = min(frame.shape[0], y + h + pad_h)
        
        roi = frame[y1:y2, x1:x2]
        return roi, (x1, y1)
    
    def _process_landmarks(
        self, 
        frame_rgb: np.ndarray, 
        roi_offset: Tuple[int, int] = (0, 0)
    ) -> Dict[str, Tuple[float, float]]:
        """
        Extract facial landmarks using MediaPipe Face Mesh.
        Returns normalized (x, y) coordinates [0, 1] in full-frame space.
        """
        if not self.settings.face or not self._mediapipe:
            # Synthetic mode: place mouth at center with small pulse
            if not self._mediapipe:
                pulse = 0.5 + 0.02 * np.sin(time.time() * 2.0)
                return {"mouth_center": (pulse, 0.5)}
            return {}
        
        # Process frame with MediaPipe
        results = self._mediapipe.process(frame_rgb)
        if not results.multi_face_landmarks:
            self._last_face_bbox = None
            return {}
        
        face_landmarks = results.multi_face_landmarks[0]
        
        # Update face bbox for ROI tracking
        h, w = frame_rgb.shape[:2]
        x_coords = [lm.x * w for lm in face_landmarks.landmark]
        y_coords = [lm.y * h for lm in face_landmarks.landmark]
        bbox_x = int(min(x_coords))
        bbox_y = int(min(y_coords))
        bbox_w = int(max(x_coords) - bbox_x)
        bbox_h = int(max(y_coords) - bbox_y)
        
        # Convert ROI coords back to full frame
        x_offset, y_offset = roi_offset
        self._last_face_bbox = (
            bbox_x + x_offset,
            bbox_y + y_offset,
            bbox_w,
            bbox_h
        )
        
        # Extract configured landmarks
        coords: Dict[str, Tuple[float, float]] = {}
        face_map = self._features.get("face", {})
        if not isinstance(face_map, dict):
            return {}
        
        for name, spec in face_map.items():
            if not isinstance(spec, dict):
                continue
            indices_raw = spec.get("indices")
            if not isinstance(indices_raw, list):
                continue
            valid_indices = [int(i) for i in indices_raw if isinstance(i, int)]
            if not valid_indices:
                continue
            
            # Average landmark positions (normalized coords)
            xs = [face_landmarks.landmark[i].x for i in valid_indices]
            ys = [face_landmarks.landmark[i].y for i in valid_indices]
            avg_x = float(sum(xs) / len(xs))
            avg_y = float(sum(ys) / len(ys))
            
            # Convert from ROI space to full frame space
            roi_h, roi_w = frame_rgb.shape[:2]
            full_x = (avg_x * roi_w + x_offset) / self.frame_w
            full_y = (avg_y * roi_h + y_offset) / self.frame_h
            
            # Apply EMA smoothing
            coords[name] = self._smooth(name, (full_x, full_y))
        
        return coords
    
    def _process_hands(
        self,
        frame_rgb: np.ndarray,
        roi_offset: Tuple[int, int] = (0, 0)
    ) -> Dict[str, Tuple[float, float]]:
        """
        Extract hand landmarks using MediaPipe Hands.
        Returns normalized (x, y) coordinates [0, 1] in full-frame space.
        """
        if not self._hand_detector:
            return {}
        
        results = self._hand_detector.process(frame_rgb)
        if not results.multi_hand_landmarks:
            return {}
        
        coords: Dict[str, Tuple[float, float]] = {}
        hands_map = self._features.get("hands", {})
        if not isinstance(hands_map, dict):
            return {}
        
        # Process each detected hand
        for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handedness = results.multi_handedness[hand_idx].classification[0].label
            
            for name, spec in hands_map.items():
                if not isinstance(spec, dict):
                    continue
                indices_raw = spec.get("indices")
                if not isinstance(indices_raw, list):
                    continue
                valid_indices = [int(i) for i in indices_raw if isinstance(i, int)]
                if not valid_indices:
                    continue
                
                # Get landmark position
                idx = valid_indices[0]  # Hands typically use single index
                lm = hand_landmarks.landmark[idx]
                
                # Convert from ROI space to full frame space
                roi_h, roi_w = frame_rgb.shape[:2]
                x_offset, y_offset = roi_offset
                full_x = (lm.x * roi_w + x_offset) / self.frame_w
                full_y = (lm.y * roi_h + y_offset) / self.frame_h
                
                # Apply EMA smoothing
                smooth_name = f"{name}_{handedness}"
                coords[smooth_name] = self._smooth(smooth_name, (full_x, full_y))
        
        return coords

    def _smooth(self, name: str, value: Tuple[float, float]) -> Tuple[float, float]:
        prev = self._ema.get(name)
        if not prev:
            self._ema[name] = value
            return value
        smoothed = (
            self._alpha * value[0] + (1 - self._alpha) * prev[0],
            self._alpha * value[1] + (1 - self._alpha) * prev[1],
        )
        self._ema[name] = smoothed
        return smoothed

    def _build_shapes(
        self,
        landmarks: Dict[str, Tuple[float, float]],
        width: int,
        height: int,
        ar_anchors: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Build overlay shapes based on current routine step and detected landmarks.
        """
        shapes: List[Dict[str, Any]] = []
        routine = self.session.routine_id or ""
        current_step = self.session.step_index
        routine_steps = self._tasks.get(routine, []) if isinstance(self._tasks, dict) else []
        active_step = None
        if isinstance(routine_steps, list) and 0 <= current_step < len(routine_steps):
            candidate = routine_steps[current_step]
            if isinstance(candidate, dict):
                active_step = candidate

        if active_step:
            # Draw rings at target anchors for current step
            anchors = active_step.get("target_anchors", [])
            if not isinstance(anchors, list):
                anchors = []
            for anchor_name in anchors:
                if anchor_name in landmarks:
                    px = landmarks[anchor_name][0] * width
                    py = landmarks[anchor_name][1] * height
                    shapes.append(
                        {
                            "kind": "ring",
                            "anchor": {"pixel": {"x": px, "y": py}},
                            "radius_px": 90,
                            "accent": "info",
                        }
                    )
            
            # Optional: Draw arrow from hand to mouth target
            if self.settings.hands and "hand_right_index_tip_Right" in landmarks:
                # Find primary mouth target
                mouth_target = None
                for anchor_name in anchors:
                    if "mouth" in anchor_name and anchor_name in landmarks:
                        mouth_target = anchor_name
                        break
                
                if mouth_target:
                    hand_x = landmarks["hand_right_index_tip_Right"][0] * width
                    hand_y = landmarks["hand_right_index_tip_Right"][1] * height
                    mouth_x = landmarks[mouth_target][0] * width
                    mouth_y = landmarks[mouth_target][1] * height
                    shapes.append(
                        {
                            "kind": "arrow",
                            "anchor": {"pixel": {"x": hand_x, "y": hand_y}},
                            "to": {"pixel": {"x": mouth_x, "y": mouth_y}},
                        }
                    )
        else:
            # Default fallback ring at screen center (no active routine)
            shapes.append(
                {
                    "kind": "ring",
                    "anchor": {"pixel": {"x": width / 2, "y": height / 2}},
                    "radius_px": 80,
                    "accent": "neutral",
                }
            )

        # Add ArUco marker badges
        for anchor in ar_anchors:
            aruco_val = anchor.get("aruco_id")
            center = anchor.get("center_px")
            if not isinstance(center, dict):
                continue
            if isinstance(aruco_val, (int, float)):
                aruco_id = int(aruco_val)
            else:
                continue
            
            # Create badge manually (avoiding import)
            shapes.append(
                {
                    "kind": "badge",
                    "anchor": {"pixel": center},
                    "text": "Hold here",
                    "offset_px": {"x": 0, "y": -120},
                }
            )
        
        return shapes

    def _build_hud(self) -> Dict[str, Any]:
        """Build HUD payload from current routine step."""
        routine = self.session.routine_id or ""
        steps = self._tasks.get(routine, []) if isinstance(self._tasks, dict) else []
        idx = self.session.step_index
        
        if not isinstance(steps, list) or idx >= len(steps):
            return {}
        
        step_candidate = steps[idx]
        if not isinstance(step_candidate, dict):
            return {}
        
        step = step_candidate
        hud = {
            "title": step.get("title"),
            "step": f"Step {idx + 1} of {len(steps)}",
            "subtitle": step.get("subtitle"),
            "time_left_s": step.get("min_time_s"),
            "max_time_s": step.get("min_time_s"),  # For progress bar calculation
            "hint": step.get("hint"),
        }
        return hud
    
    def _send_no_face_hint(self) -> None:
        """Send a hint message when no face is detected for a while."""
        hint_msg = {
            "type": "overlay.set",
            "shapes": [],
            "hud": {
                "title": "Position Yourself",
                "subtitle": "Move closer to camera",
                "hint": "Ensure good lighting",
            },
        }
        self.broadcast_fn(hint_msg)

    def _log_latency(
        self,
        capture_ts: float,
        landmark_ts: float,
        overlay_ts: float,
        e2e_ms: float
    ) -> None:
        """Append latency metrics to CSV log."""
        use_cloud = self.settings.use_cloud
        fps = self.health.fps
        record = f"{capture_ts:.6f},{landmark_ts:.6f},{overlay_ts:.6f},{e2e_ms:.2f},{fps:.1f},{int(use_cloud)}\n"
        try:
            with LOGS_PATH.open("a", encoding="utf-8") as handle:
                handle.write(record)
        except Exception as exc:
            LOGGER.warning("Failed to log latency: %s", exc)


# CLI entrypoint for standalone testing
if __name__ == "__main__":
    import signal
    import sys
    
    # Simple stub classes for standalone mode
    class StubSettings:
        use_cloud = False
        face = True
        hands = False
        aruco = False
    
    class StubSession:
        routine_id = "brush_teeth"
        step_index = 0
    
    class StubHealth:
        fps = 0.0
        latency_ms = 0.0
        camera = "off"
        lighting = "unknown"
    
    def stub_broadcast(msg: Dict[str, Any]) -> None:
        """Stub broadcast that just logs."""
        msg_type = msg.get("type", "unknown")
        shape_count = len(msg.get("shapes", []))
        hud = msg.get("hud", {})
        LOGGER.info(
            "Broadcast: type=%s shapes=%d hud_title=%s",
            msg_type,
            shape_count,
            hud.get("title", "N/A")
        )
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d %(levelname)s %(name)s %(message)s",
        datefmt="%H:%M:%S"
    )
    
    LOGGER.info("Starting vision pipeline in standalone mode...")
    LOGGER.info("Press Ctrl+C to stop")
    
    settings = StubSettings()
    session = StubSession()
    health = StubHealth()
    
    # Create pipeline
    pipeline = VisionPipeline(
        broadcast_fn=stub_broadcast,
        settings=settings,
        session=session,
        health=health,
        camera_width=1280,
        camera_height=720,
        camera_fps=24,
        camera_device=0
    )
    
    # Handle graceful shutdown
    def signal_handler(sig: int, frame: Any) -> None:
        LOGGER.info("\nShutting down...")
        pipeline.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start pipeline
    pipeline.start()
    
    # Keep alive and print stats
    try:
        while True:
            time.sleep(2.0)
            LOGGER.info(
                "Stats: fps=%.1f latency=%.1fms camera=%s lighting=%s",
                health.fps,
                health.latency_ms,
                health.camera,
                health.lighting
            )
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.stop()
        LOGGER.info("Vision pipeline stopped")