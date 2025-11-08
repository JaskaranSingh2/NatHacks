# Project Status

## Snapshot — November 2025

- Edge vision loop continues to hit the <150 ms budget on Pi-class hardware using ROI cropping and EMA smoothing.
- Optional Google Cloud Vision assist now runs asynchronously with caching, rate limiting, and a circuit breaker so the edge loop never blocks.
- `/health` exposes a dedicated `cloud` block and `logs/latency.csv` adds latency/confidence columns for quick diagnostics.
- Developer onboarding improved via an updated README and scripted smoke tests (`scripts/test_vision_pipeline.sh`, `scripts/test_animations.sh`).

## Latest Changes

- Added `backend/cloud_vision.py` and wired it into `backend/vision_pipeline.py` through a background worker that blends cloud landmarks with MediaPipe output.
- Extended FastAPI settings and health models to surface cloud rate limits, breaker state, and metrics in real time.
- Refreshed top-level documentation to cover credential setup, health monitoring, and the expanded CSV schema.
- Implemented Step E: ArUco tool guidance with 2D fallback and pose-enabled tilt hints; added subsampled detection, EMA smoothing, and a debounced guidance state machine; created calibration and marker generation scripts.

## Open Risks & Follow-Ups

- Cloud assist still needs sustained testing on low-bandwidth networks to tune retry/backoff strategy choices.
- MagicMirror client should surface cloud availability to end users; today only the backend reports it.
- Automated coverage does not yet exercise the cloud fusion logic; failures would only show up in manual testing.

## Next Actions

1. Run the integrated stack on target Pi hardware, validate ArUco responsiveness and e2e latency ≤150 ms.
2. Add unit tests for ArUco pose gating and state machine transitions; extend coverage for cloud fusion.
3. Surface guidance state and cloud health chips in the MagicMirror HUD; consider SVG icons for tilt arrows.
