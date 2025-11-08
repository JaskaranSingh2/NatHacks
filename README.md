NatHacks — Assistive Mirror (Customer Snapshot)

## What we built

A self-contained assistive smart mirror prototype that helps people complete morning grooming routines using a camera, real-time computer vision, and a simple animated HUD on a MagicMirror² display.

Key capabilities

- Real-time face landmark tracking (mouth, cheeks, brows) using MediaPipe Face Mesh. The system focuses on a single user and crops the camera image to a small region around the face to run faster on modest hardware.
- Smooth, senior-friendly HUD and overlays (rings, progress bar, large readable text) implemented with vanilla JavaScript, SVG and GPU-friendly CSS animations. Respects users' reduced-motion settings.
- A backend service (FastAPI) that streams overlay messages to the MagicMirror module via a thread-safe queue + WebSockets. The vision component runs in a background thread and publishes overlay messages as JSON.
- CSV latency logging for capture→landmark→overlay timing, and a compact test-suite for local verification.

Why this matters

- Designed for low-cost devices (Raspberry Pi 4/5) with careful performance optimizations (ROI crop, EMA smoothing, single MediaPipe graph) so overlays feel responsive and stable.
- UI is high-contrast and readable for older adults and supports accessibility via `prefers-reduced-motion`.

## Quick start (developer)

Prerequisites

- Python 3.10+ (or your system Python)
- Node.js + MagicMirror² if running the frontend module locally

Backend (quick run)

1. Install Python deps (use a virtualenv):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt  # if present
pip install mediapipe opencv-python numpy
```

2. Start the backend API (default port 5055):

```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 5055
```

3. Run the MagicMirror with the `MMM-AssistiveCoach` module loaded, or point any WebSocket-capable client at the backend to receive `overlay.set` messages.

Standalone vision test

```bash
# runs the vision pipeline in CLI mode (prints lightweight stats)
python backend/vision_pipeline.py
```

What to expect

- A pulsing ring overlay near the user's mouth and a large HUD card describing the current routine step.
- Smooth progress bar animations and non-jarring color changes for device status.
- If no face is detected, the system will show a gentle hint asking the user to reposition.

Files of interest

- `backend/vision_pipeline.py` — Vision loop, ROI optimization, EMA smoothing, CSV logging
- `backend/app.py` — FastAPI integration and startup/shutdown lifecycle
- `mirror/modules/MMM-AssistiveCoach/` — MagicMirror frontend module (animations + overlay rendering)
- `config/features.json` & `config/tasks.json` — Landmarks mapping and routine definitions
- `logs/latency.csv` — Capture/processing/broadcast timing data

Next steps (recommended before a public push)

- Run the included `test_vision_pipeline.sh` on a Raspberry Pi to validate <150ms capture→overlay latency and jitter targets.
- Decide whether to include cloud-based fallbacks (Google Vision) — currently flagged but not enabled by default.
- Add a minimal `requirements.txt` in `backend/` (if missing) and a short `README-DEV.md` with environment setup steps for CI.

Contact

- For technical questions about this prototype, see the module source or contact the engineering lead listed in the repo.

License

- Internal prototype. Add an explicit license file before public release.
