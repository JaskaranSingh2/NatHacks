from typing import Dict, List, Tuple

import cv2
import numpy as np

LOGGER_NAME = "assistivecoach.ar"


def _get_dictionary():
    if not hasattr(cv2, "aruco"):
        raise RuntimeError("OpenCV ArUco module not available")
    return cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_250)


def detect_aruco_anchors(frame_rgb: np.ndarray) -> List[Dict[str, object]]:
    if not hasattr(cv2, "aruco"):
        return []
    gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
    dictionary = _get_dictionary()
    parameters = cv2.aruco.DetectorParameters()  # type: ignore[attr-defined]
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)  # type: ignore[attr-defined]
    corners, ids, _ = detector.detectMarkers(gray)
    anchors: List[Dict[str, object]] = []
    if ids is None:
        return anchors
    for marker_corners, marker_id in zip(corners, ids.flatten().tolist()):
        points = marker_corners.reshape(-1, 2)
        center = points.mean(axis=0)
        anchors.append(
            {
                "aruco_id": int(marker_id),
                "center_px": {"x": float(center[0]), "y": float(center[1])},
            }
        )
    return anchors


def make_badge(text: str, aruco_id: int, offset_px: Tuple[int, int]) -> Dict[str, object]:
    return {
        "kind": "badge",
        "anchor": {"aruco_id": aruco_id},
        "text": text,
        "offset_px": {"x": offset_px[0], "y": offset_px[1]},
    }