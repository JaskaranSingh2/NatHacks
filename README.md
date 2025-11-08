# NatHacks Assistive Mirror

Plain-English snapshot of the prototype for customers and non-engineers.

## What We Built

An assistive smart mirror that guides morning grooming (e.g. brushing teeth) using a camera, real‑time face landmark tracking, and a clean animated heads‑up display (HUD). Runs on Raspberry Pi hardware + MagicMirror² with no heavy frameworks.

## Key Capabilities

- Real-time face landmark tracking (mouth, cheeks, brows) with MediaPipe Face Mesh (optimized via region-of-interest cropping).
- Clear HUD: large text, progress bar, pulsing guidance rings placed at target facial regions for each routine step.
- Reduced-motion accessibility: detects `prefers-reduced-motion` and disables animations automatically.
- Low-latency pipeline (<150 ms target capture→overlay) using a background vision thread + WebSocket streaming.
- CSV performance logging (latency + FPS) for validation on device.

## Why It Matters

- Helps older adults or anyone with routine adherence challenges by turning abstract timing into visual guidance.
- Designed for inexpensive hardware (Pi 4/5) with careful optimizations: ROI cropping, EMA smoothing, single long-lived MediaPipe graph.
- High contrast, senior-friendly typography and motion choices that avoid visual overload.

## Running the Prototype

### Prerequisites

- Python 3.10+
- Node.js + MagicMirror² (for the display module)

### Backend (FastAPI)

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

1. Install dependencies (minimal example):

```bash
pip install mediapipe opencv-python numpy fastapi uvicorn
```

1. Start the API (port 5055 by default):

```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 5055
```

### Vision Standalone Smoke Test

```bash
python backend/vision_pipeline.py
```

Watch console stats for FPS and latency; press Ctrl+C to stop.

### Frontend (MagicMirror Module)

Add `MMM-AssistiveCoach` to your MagicMirror `config.js`, then start MagicMirror. The module connects to the backend WebSocket and renders incoming `overlay.set` messages.

## What You’ll See

- A cyan ring near the mouth that tracks movement smoothly.
- A HUD card: title, current step, remaining time, hint.
- Progress bar growing over the step duration.
- Status chips (camera / lighting / mic) changing color as conditions change.
- Graceful fallback hint if face not detected for a short period.

## Notable Files

- `backend/vision_pipeline.py` – Vision loop, ROI crop, smoothing, CSV logging.
- `backend/app.py` – FastAPI app and WebSocket broadcast integration.
- `mirror/modules/MMM-AssistiveCoach/` – Frontend module (animations + rendering).
- `config/features.json` – Landmark groups (mouth, cheeks, brows, etc.).
- `config/tasks.json` – Routine steps and target anchors.
- `logs/latency.csv` – Generated performance log (created at runtime).

## Suggested Next Steps Before Public Release

- Add `backend/requirements.txt` locking minimal versions.
- Include a lightweight `README-DEV.md` with deeper setup + testing details.
- Decide on enabling optional cloud vision fallback (flag currently dormant).
- Add a license file (e.g. MIT, Apache 2.0, or proprietary notice).

## Contact

For technical or partnership inquiries, refer to repository ownership metadata or project lead.

## License

Internal prototype (unlicensed). Add a formal license prior to distribution.
