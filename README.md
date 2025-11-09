# NatHacks Assistive Mirror

Raspberry Pi smart mirror that guides morning routines with on-device computer vision and an optional Google Cloud Vision assist. Built for <150 ms capture→overlay latency while keeping the UX senior-friendly.

## System At A Glance

- **Edge-first loop:** MediaPipe Face Mesh + hands run locally for low jitter overlays and resilient offline behaviour.
- **Cloud assist (optional):** Non-blocking Google Cloud Vision fallback refines mouth/cheek landmarks when credentials are present.
- **HUD overlays:** Animated rings, progress bars, and routine hints streamed to the MagicMirror module via WebSocket.
- **Observability:** `logs/latency.csv` captures FPS, latency, and new cloud metrics; `/health` exposes a structured status payload for the frontend.

## Repository Map

- `backend/app.py` – FastAPI service, REST/WebSocket endpoints, settings/state management.
- `backend/vision_pipeline.py` – Camera loop, MediaPipe processing, cloud fusion, CSV logging.
- `backend/cloud_vision.py` – Rate-limited Google Cloud Vision client with caching + circuit breaker.
- `config/` – Feature indices (`features.json`) and scripted routines (`tasks.json`).
- `mirror/` – MagicMirror module that renders the overlay stream.
- `scripts/` – Shell helpers (`test_vision_pipeline.sh`, `test_animations.sh`).

## Getting Started

### 1. Backend setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Run the API (default :5055)
uvicorn backend.app:app --host 0.0.0.0 --port 5055
```

Use `python backend/vision_pipeline.py` for a ten-second standalone smoke test (writes to `logs/latency.csv`).

### 2. Optional Google Cloud Vision assist

1. Provision a Vision API credential and point `GOOGLE_APPLICATION_CREDENTIALS` at the JSON key file.
2. Start the backend; the client auto-enables when credentials are readable.
3. Toggle runtime behaviour via `POST /settings`:

```bash
curl -X POST http://localhost:5055/settings \
  -H 'Content-Type: application/json' \
  -d '{
        "use_cloud": true,
        "cloud_rps": 2,
        "cloud_timeout_s": 0.8,
        "cloud_min_interval_ms": 600
      }'
```

Cloud requests run in a background worker. The edge loop keeps broadcasting even if the Cloud Vision rate limiter trips or the circuit breaker opens.

### 3. MagicMirror module

Install the `MMM-AssistiveCoach` module under MagicMirror², configure the backend URL (`ws://<host>:5055/ws/mirror`), and start MagicMirror. The module automatically renders `overlay.set` messages and surfaces `/health` status chips.

## Operating Notes

### Key FastAPI endpoints

- `GET /health` – Returns camera status, FPS/latency, and a `cloud` block (`enabled`, `latency_ms`, `ok_count`, `fail_count`, `breaker_open`, `last_ok_ns`).
- `POST /settings` – Toggle detectors (`face`, `hands`, `aruco`, `use_cloud`) and adjust cloud rate limits.
- `POST /session/start` – Begin a guided routine; pipeline pushes HUD metadata immediately.
- `POST /tts` – Queue speech output via eSpeak-NG or PyTTSx3.
- `WebSocket /ws/mirror` – Overlay stream for the MagicMirror client.

### Observability

`logs/latency.csv` (auto-created) now includes:

```text
capture_ts,landmark_ts,overlay_ts,e2e_ms,fps,use_cloud,cloud_latency_ms,cloud_confidence,cloud_ok,cloud_breaker_open
```

Use `scripts/test_vision_pipeline.sh` to exercise standalone and integrated modes; it reports average latency, CSV growth, and cloud assist statistics.

### Development & Testing

#### Running Unit Tests

Pytest covers cloud blending and client caching/rate limiting logic. Run all tests:

```bash
python3 -m pytest -q backend/tests
```

#### Hardware Independence

`VisionPipeline` supports a dummy camera via `camera_enabled=False` so CI and local tests don't require `/dev/video0`.

```python
pipeline = VisionPipeline(camera_enabled=False)
```

You can also inject a custom stub with `camera_override` exposing a minimal `read()` returning `(True, frame)`.

#### Focused Iteration

Run a single test module or increase verbosity while developing:

```bash
python3 -m pytest backend/tests/test_cloud_blending.py -vv
```

#### Adding Tests

Place new files under `backend/tests/` named `test_*.py`. Keep tests deterministic: mock time-sensitive cloud calls and fix random seeds. Prefer unit-level checks over full frame loops unless explicitly benchmarking latency.

### Troubleshooting

### Tool Guidance (ArUco)

The mirror can guide tool positioning using printed ArUco markers (OpenCV dictionary **DICT_5X5_250**). Place marker **23** near a toothbrush and marker **42** near a razor. Guidance has two modes:

1. 2D fallback (no calibration): distance-only states SEARCHING → ALIGNING → GOOD.
2. Pose-enabled (after chessboard calibration): adds tilt hints (rotate / tilt) when yaw/pitch exceed tolerances.

Enable guidance:

```bash
curl -X POST http://localhost:5055/settings -H 'Content-Type: application/json' \
  -d '{"aruco": true, "pose": true}'
```

Calibrate (optional for 6DoF): run `python scripts/calibrate_cam.py` and save `config/camera_intrinsics.yml`; then restart backend so pose estimation activates.

Performance: detection subsampled to ~15 Hz and centers / angles smoothed with EMA (α=0.4) to keep CPU low and jitter under ~5 px.

Marker printing: `python scripts/gen_aruco.py --ids 23 42 --size 500 --out markers/`.

If pose disabled or intrinsics missing, pipeline automatically falls back to 2D distance guidance.

- **No camera frames:** Ensure `/dev/video0` is accessible; `backend/camera_capture.py` logs when it cannot open the device.
- **Cloud assist not engaging:** Verify `GOOGLE_APPLICATION_CREDENTIALS`, then inspect `/health` → `cloud.breaker_open` and the `cloud_*` columns in `logs/latency.csv`.
- **High latency (>150 ms):** Check for throttled hardware (Pi running in powersave) and confirm that ROI cropping is active by watching the log warnings.

## Roadmap

- Expand automated tests around the cloud fusion path and CSV parsing.
- Add configurable overlay themes within the MagicMirror module.
- Package scripts into a simple installer for Raspberry Pi images.

## Accessibility

The Assistive Mirror integrates:

- High contrast HUD with semantic color tokens (`--ok`, `--warn`, `--err`, `--accent`).
- Typography clamps for large titles (`--title-size`) ensuring distant readability.
- Reduced motion support: respects OS `prefers-reduced-motion` and a server override (`reduce_motion` via `POST /settings`). Clients remove pulsing/slide animations when active.
- Keyboard demo shortcuts (1, 2, 3) generate local overlays for offline testing without camera/markers.
- Focus-visible outlines for clarity when navigating interactive surfaces.

Toggle reduced motion at runtime:

```bash
curl -X POST http://localhost:5055/settings -H 'Content-Type: application/json' -d '{"reduce_motion": true}'
```

`/health` includes `reduce_motion` so UIs can synchronize animation state.

See `ACCESSIBILITY.md` for details and guidance when adding new UI motion or colors.

## License

Internal prototype (unlicensed). Add a formal license before external distribution.
