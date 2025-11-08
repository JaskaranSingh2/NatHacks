"""Google Cloud Vision helper client for optional landmark refinement."""
from __future__ import annotations

import logging
import os
import threading
import time
from collections import OrderedDict, deque
from typing import Any, Deque, Dict, Optional, Tuple

import cv2
import numpy as np


LOGGER = logging.getLogger("assistivecoach.cloud")


class CloudVisionClient:
    """Wrapper around Google Cloud Vision FACE_DETECTION with rate limits and caching."""

    _CACHE_TTL_S = 10.0
    _CACHE_MAX = 32
    _BREAKER_OPEN_SECONDS = 10

    def __init__(
        self,
        rps: int = 2,
        timeout_s: float = 0.8,
        min_interval_ms: int = 600,
    ) -> None:
        self.enabled = False
        self.rps = max(1, int(rps))
        self.timeout_s = max(0.1, float(timeout_s))
        self.min_interval_ms = max(0, int(min_interval_ms))

        self.ok_count = 0
        self.fail_count = 0
        self.last_ok_ns: Optional[int] = None
        self.breaker_open = False

        self._lock = threading.Lock()
        self._call_times: Deque[float] = deque()
        self._last_call_ns = 0
        self._consecutive_failures = 0
        self._breaker_until_ns = 0
        self._last_latency_ms: float = 0.0
        self._cache: OrderedDict[str, Tuple[float, Optional[Dict[str, Any]]]] = OrderedDict()

        self._vision: Any = None
        self._client: Any = None

        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        # creds_path = "backend/eminent-will-477604-h6-d9d50a6b65d4.json"
        print(f"\n\n{creds_path}\n\n")
        try:
            from google.cloud import vision  # type: ignore[import]

            if creds_path:
                self._vision = vision
                self._client = vision.ImageAnnotatorClient()  # type: ignore[attr-defined]
                self.enabled = True
                LOGGER.info("CloudVisionClient enabled (credentials detected)")
                
                # print("\033[31mREACHED\033[0m")
                
            else:
                self._vision = None
                self._client = None
                LOGGER.info("CloudVisionClient disabled (GOOGLE_APPLICATION_CREDENTIALS missing)")
                
                # print("\033[31mHELP\033[0m")
                
        except Exception as exc:  # pragma: no cover - optional dependency
            
            # print(f"\033[31m CloudVisionClient unavailable \033[0m")
            # print(exc)
            
            
            self._vision = None
            self._client = None
            LOGGER.debug("CloudVisionClient unavailable: %s", exc)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def update_limits(self, rps: int, timeout_s: float, min_interval_ms: int) -> None:
        with self._lock:
            self.rps = max(1, int(rps))
            self.timeout_s = max(0.1, float(timeout_s))
            self.min_interval_ms = max(0, int(min_interval_ms))

    def detect_faces(self, image_bytes: bytes) -> Optional[Dict[str, Any]]:
        if not self.enabled or not image_bytes:
            return None

        now_ns = time.time_ns()
        now = time.time()

        with self._lock:
            if self.breaker_open and now_ns < self._breaker_until_ns:
                LOGGER.debug("CloudVisionClient breaker open; skipping request")
                return None
            if self.breaker_open and now_ns >= self._breaker_until_ns:
                LOGGER.info("CloudVisionClient breaker reset after cooldown")
                self.breaker_open = False
                self._consecutive_failures = 0

        roi_bgr = self._decode(image_bytes)
        if roi_bgr is None:
            return None

        height, width = roi_bgr.shape[:2]
        if height == 0 or width == 0:
            return None

        cache_key = self._cache_key(roi_bgr)

        with self._lock:
            cached = self._cache.get(cache_key)
            if cached and (now - cached[0]) <= self._CACHE_TTL_S:
                LOGGER.debug("CloudVisionClient returning cached result")
                return cached[1]

            if not self._reserve_slot_locked(now, now_ns):
                LOGGER.debug("CloudVisionClient rate limited")
                return None

        delays = (0.0, 0.2, 0.4, 0.8)
        image = self._vision.Image(content=image_bytes)  # type: ignore[attr-defined]
        start_ns = time.time_ns()
        last_error: Optional[Exception] = None

        for delay in delays:
            if delay:
                time.sleep(delay)
            try:
                response = self._client.face_detection(image=image, timeout=self.timeout_s)  # type: ignore[attr-defined]
                if response.error.message:  # type: ignore[attr-defined]
                    raise RuntimeError(response.error.message)  # noqa: TRY003
                result = self._parse_response(response, width, height)
                latency_ms = (time.time_ns() - start_ns) / 1e6
                if result:
                    result["latency_ms"] = latency_ms
                self._register_success(cache_key, result)
                return result
            except Exception as exc:  # pragma: no cover - external dependency errors
                last_error = exc
                LOGGER.debug("CloudVisionClient request failed: %s", exc)

        self._register_failure()
        if last_error:
            LOGGER.warning("CloudVisionClient failure after retries: %s", last_error)
        return None

    def metrics(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "enabled": self.enabled,
                "rps": self.rps if self.enabled else 0,
                "last_ok_ns": self.last_ok_ns,
                "ok_count": self.ok_count,
                "fail_count": self.fail_count,
                "breaker_open": self.breaker_open,
                "latency_ms": self._last_latency_ms,
            }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def roi_bytes(
        frame_bgr: np.ndarray,
        bbox: Tuple[int, int, int, int],
        pad: float = 0.2,
        jpeg_quality: int = 70,
    ) -> bytes:
        x, y, w, h = bbox
        pad_w = int(w * pad)
        pad_h = int(h * pad)
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(frame_bgr.shape[1], x + w + pad_w)
        y2 = min(frame_bgr.shape[0], y + h + pad_h)
        roi = frame_bgr[y1:y2, x1:x2]
        if roi.size == 0:
            return b""
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), int(jpeg_quality)]
        ok, buffer = cv2.imencode(".jpg", roi, encode_params)
        if not ok:
            return b""
        return bytes(buffer)

    def _register_success(self, cache_key: str, result: Optional[Dict[str, Any]]) -> None:
        now = time.time()
        with self._lock:
            self._consecutive_failures = 0
            self.breaker_open = False
            if result and result.get("ok"):
                self.ok_count += 1
                self.last_ok_ns = time.time_ns()
                self._last_latency_ms = float(result.get("latency_ms", 0.0))
                self._cache[cache_key] = (now, result)
                self._cache.move_to_end(cache_key)
                while len(self._cache) > self._CACHE_MAX:
                    self._cache.popitem(last=False)
            elif result is not None:
                # Still cache negative results to avoid repeat hits.
                self._cache[cache_key] = (now, result)
                self._cache.move_to_end(cache_key)
                while len(self._cache) > self._CACHE_MAX:
                    self._cache.popitem(last=False)

    def _register_failure(self) -> None:
        with self._lock:
            self.fail_count += 1
            self._consecutive_failures += 1
            if self._consecutive_failures >= 3:
                self.breaker_open = True
                self._breaker_until_ns = time.time_ns() + int(self._BREAKER_OPEN_SECONDS * 1e9)

    def _reserve_slot_locked(self, now: float, now_ns: int) -> bool:
        while self._call_times and (now - self._call_times[0]) > 1.0:
            self._call_times.popleft()

        if len(self._call_times) >= self.rps:
            return False

        if self._last_call_ns and ((now_ns - self._last_call_ns) / 1e6) < self.min_interval_ms:
            return False

        self._call_times.append(now)
        self._last_call_ns = now_ns
        return True

    def _cache_key(self, roi_bgr: np.ndarray) -> str:
        phash = self._perceptual_hash(roi_bgr)
        bucket = self._lighting_bucket(roi_bgr)
        return f"{phash}:{bucket}"

    @staticmethod
    def _lighting_bucket(roi_bgr: np.ndarray) -> int:
        gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
        mean_val = float(gray.mean())
        return int(mean_val // 20)

    @staticmethod
    def _perceptual_hash(roi_bgr: np.ndarray) -> str:
        gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
        resized32 = resized.astype(np.float32)
        dct = cv2.dct(resized32)
        dct_low = np.asarray(dct[:8, :8], dtype=np.float32)
        median_val = float(np.median(dct_low))
        bit_array = np.greater(dct_low, median_val).flatten()
        bits = ''.join('1' if bit else '0' for bit in bit_array)
        return format(int(bits, 2), "016x")

    @staticmethod
    def _decode(data: bytes) -> Optional[np.ndarray]:
        np_arr = np.frombuffer(data, np.uint8)
        if np_arr.size == 0:
            return None
        roi_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return roi_bgr

    def _parse_response(
        self,
        response: Any,
        width: int,
        height: int,
    ) -> Optional[Dict[str, Any]]:
        annotations = getattr(response, "face_annotations", None)
        if not annotations:
            return {
                "ok": False,
                "landmarks": {},
                "confidence": 0.0,
                "ts_ns": time.time_ns(),
            }

        face = annotations[0]
        landmark_map = {
            "mouth_center": self._vision.FaceAnnotation.Landmark.Type.MOUTH_CENTER,  # type: ignore[attr-defined]
            "mouth_left": self._vision.FaceAnnotation.Landmark.Type.MOUTH_LEFT,  # type: ignore[attr-defined]
            "mouth_right": self._vision.FaceAnnotation.Landmark.Type.MOUTH_RIGHT,  # type: ignore[attr-defined]
            "cheek_left": self._vision.FaceAnnotation.Landmark.Type.LEFT_CHEEK_CENTER,  # type: ignore[attr-defined]
            "cheek_right": self._vision.FaceAnnotation.Landmark.Type.RIGHT_CHEEK_CENTER,  # type: ignore[attr-defined]
            "left_of_left_eyebrow": self._vision.FaceAnnotation.Landmark.Type.LEFT_OF_LEFT_EYEBROW,
            "right_of_left_eyebrow": self._vision.FaceAnnotation.Landmark.Type.RIGHT_OF_LEFT_EYEBROW,
            "left_of_right_eyebrow": self._vision.FaceAnnotation.Landmark.Type.LEFT_OF_RIGHT_EYEBROW,
            "right_of_right_eyebrow": self._vision.FaceAnnotation.Landmark.Type.RIGHT_OF_RIGHT_EYEBROW,
        }

        coords: Dict[str, Tuple[float, float]] = {}
        for name, landmark_type in landmark_map.items():
            lm = self._find_landmark(face, landmark_type)
            if lm is None or lm.position is None:
                continue
            coords[name] = (
                float(lm.position.x) / float(width),
                float(lm.position.y) / float(height),
            )

        ok = bool(coords)
        confidence = float(getattr(face, "landmarking_confidence", 0.0) or 0.0)
        detection_confidence = float(getattr(face, "detection_confidence", 0.0) or 0.0)
        if confidence == 0.0:
            confidence = detection_confidence
        else:
            confidence = float((confidence + detection_confidence) / 2.0)

        return {
            "ok": ok,
            "landmarks": coords,
            "confidence": confidence,
            "ts_ns": time.time_ns(),
        }

    @staticmethod
    def _find_landmark(face: Any, landmark_type: Any) -> Optional[Any]:
        for landmark in getattr(face, "landmarks", []) or []:
            if getattr(landmark, "type_", None) == landmark_type or getattr(landmark, "type", None) == landmark_type:
                return landmark
        return None


if __name__ == "__main__":  # pragma: no cover - manual utility
    client = CloudVisionClient()
    print(f"CloudVisionClient enabled={client.enabled}")