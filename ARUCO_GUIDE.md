# ArUco Tool Guidance Guide

This guide walks through enabling live tool guidance on the Assistive Mirror using ArUco markers.

## 1. Print Markers

Generate markers for IDs 23 (toothbrush) and 42 (razor):

```bash
python scripts/gen_aruco.py --ids 23 42 --size 500 --out markers
```

Print the resulting PNGs at ~40–50 mm physical size. Matte paper works best; avoid glossy reflections.

## 2. Place Markers Near Tools

- Toothbrush: tape marker 23 on the handle near the grip.
- Razor: tape marker 42 on the end of the handle.

Position tools near the sink such that the camera sees both face and tool simultaneously. Typical working distance: 40–70 cm from camera.

## 3. (Optional) Calibrate Camera for Pose

Pose (tilt hints) requires camera intrinsics.

```bash
python scripts/calibrate_cam.py --rows 6 --cols 9 --square 0.024 --out config/camera_intrinsics.yml
```

Tips:

- Capture at least 10 clear chessboard frames (press space for each).
- Ensure even lighting; avoid motion blur.
- After writing `camera_intrinsics.yml`, restart the backend.

## 4. Enable Guidance

Toggle ArUco and pose:

```bash
curl -X POST http://localhost:5055/settings -H 'Content-Type: application/json' \
  -d '{"aruco": true, "pose": true}'
```

If intrinsics are missing pose falls back automatically to 2D guidance.

## 5. Expected UI States

| State     | Condition                                                  | Overlay                                             |
| --------- | ---------------------------------------------------------- | --------------------------------------------------- |
| SEARCHING | Marker absent or target landmark missing                   | Ghost ring + "Find tool" badge                      |
| ALIGNING  | Marker detected but outside distance tolerance OR tilt off | Arrow to target + "Align" / "Tilt" / "Rotate" badge |
| GOOD      | Within distance tolerance and tilt acceptable              | Green "Hold tool here" badge                        |

Debounce prevents flicker: transitions require ~250 ms stability.

## 6. Troubleshooting

- Marker not detected: verify dictionary (5x5_250) and adequate contrast; ensure opencv-contrib is installed.
- Excess jitter: improve lighting; check that subsampling (~15 Hz) and smoothing (α=0.4) are active (default).
- Tilt hints missing: confirm `config/camera_intrinsics.yml` exists and `pose` flag enabled.
- False positives: reduce marker size or distance; ensure only target markers are present.

## 7. References

- OpenCV ArUco Detection: <https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html>
- Camera Calibration: <https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html>
- MagicMirror Module Dev: <https://docs.magicmirror.builders/module-development/introduction.html>

## 8. Next Steps

- Add multi-marker board support for aggregated pose stability.
- Persist per-session guidance statistics.
- Provide alternate shapes (SVG arrows) via MagicMirror module assets.
