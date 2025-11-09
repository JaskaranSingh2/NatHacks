# Assistive Coach Smart Mirror – Product Pitch

## 1. The Problem

Neurodivergent kids and patients working on daily living skills (e.g., brushing teeth) often lack **timely, contextual, and adaptive guidance**. Caregivers cannot always be present; generic reminder timers or static posters fail to reinforce technique quality (coverage, duration, sequence) and can overstimulate with unnecessary motion. Existing “smart mirror” concepts focus on vanity metrics, not _skill acquisition_, _accessibility_, or _low-latency embodied feedback_.

## 2. The Solution

Assistive Coach is a **privacy-first, on-device vision coach** with optional burst “cloud assist” that never blocks the local loop. It overlays **gentle AR guidance** (rings, arrows, HUD steps) aligned to the user’s face and ArUco tool markers, pacing a routine with adaptive timing and reduced-motion UX for sensitive users. A web viewer and MagicMirror² module enable fast iteration and remote display integration.

## 3. Core Value Props

| Pillar               | What It Delivers                                                                                                                                    |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Low Latency          | <150 ms camera → overlay path with debounced 15 Hz UI updates; adaptive stride + dynamic downscale maintain responsiveness on constrained hardware. |
| Accessibility        | Reduced-motion mode (pref + runtime toggle), high-contrast HUD, keyboard demo triggers, fallback TTS chain (system → espeak → pyttsx3).             |
| Reliability          | Non-blocking cloud FACE_DETECTION assist (breaker + RPS gating), camera watchdog, synthetic fallback if camera init fails.                          |
| Guidance Quality     | ArUco-based tool anchoring (2D now / pose when calibrated); auto rings around mouth/tool; HUD routine progression with time + hints.                |
| Developer Ergonomics | Hot-reload friendly FastAPI, rich /health JSON, CSV latency logs, portable scripts (python/python3), viewer file:// WS fallback.                    |
| Extensibility        | Pluggable detectors (face / hands / aruco / pose) via settings; queue-based broadcast decouples producers & clients.                                |

## 4. Feature Highlights

1. Vision Pipeline
   - OpenCV + MediaPipe (Face Mesh, Hands) with **thread pinning** and **scaled detection** (detect_scale 0.5–1.0).
   - ArUco detection every N frames (aruco_stride) with resolution downscaling and pixel rescale for overlays.
   - Adaptive performance controller adjusts stride & scale on latency pressure (hysteresis to avoid thrash).
2. Augmented Reality Overlays
   - Auto-drawn guidance rings around markers / mouth center with idle expiry.
   - Unified overlay message schema (`overlay.set`, `status`, `tts`, `safety.alert`).
   - HUD: title, step N of M, subtitle, hint, countdown + progress bar.
3. Session Engine
   - `/session/start` loads routine steps (config/tasks.json) & immediately pushes Step 1 HUD.
   - Step navigation endpoints; session state serialized safely (ISO datetimes).
4. Cloud Assist (Optional)
   - Burst FACE_DETECTION calls under rate / timeout / min-interval guards; breaker metrics surfaced without blocking frame loop.
5. Metrics & Observability
   - `/health` surfaces fps, latency, cloud stats, pose availability, intrinsics errors, accessibility flags, detection parameters.
   - `logs/latency.csv` with per-frame timings (capture, detect, cloud, end-to-end) for offline profiling.
6. Accessibility & Inclusive Design
   - Reduced-motion propagated live to viewer; animation fallbacks (pulse → static).
   - Keyboard demo overlays (1/2/3) in viewer; high-contrast chip states (camera / lighting / mic).
7. Resilience
   - Synthetic camera fallback if device open fails; watchdog triggers soft reset on sustained latency spikes.
   - Graceful WebSocket origin policy (dev-friendly) and queue-based broadcaster.
8. Tooling & Scripts
   - Calibration utility (robust chessboard flags); ArUco marker generator with multi-API fallback.
   - Smoke scripts: overlay, TTS, ArUco enable, full vision pipeline test.
9. Frontend Integration
   - Standalone `tools/viewer.html` (works via file://) with WS auto URL fallback + motion toggle (?motion & "m" key).
   - MagicMirror² module (`mirror/modules/MMM-AssistiveCoach/`).

## 5. Architecture (Text Diagram)

```text
            +----------------------+        +-----------------------+
Camera ---> |  Capture Thread      |  --->  |  Vision Pipeline Loop |--+----> queue_broadcast()
            +----------+-----------+        +----------+------------+  |         (async)
                       |                             |               |
                       v                             v               |
                Preprocess / Scale         MediaPipe / ArUco / Cloud  |
                       |                             |               |
                       +------------- Perf Adapt ----+               |
                                                           +---------v---------+
                                                           |  Broadcast Queue  |---> WebSocket Clients (Viewer/MM)
                                                           +---------+---------+
                                                                     |
                                                         +-----------v-----------+
                                                         | Overlay & HUD Renderer|
                                                         +-----------------------+
```

## 6. Tech Stack

| Layer                 | Tech                                                  |
| --------------------- | ----------------------------------------------------- |
| Backend API           | FastAPI (Python) + Uvicorn                            |
| Vision / CV           | OpenCV (ArUco, capture), MediaPipe (Face Mesh, Hands) |
| Optional Assist       | Google Cloud Vision (non-blocking FACE_DETECTION)     |
| Messaging             | In-process asyncio queue → WebSocket broadcast        |
| Overlay Protocol      | JSON messages (status / overlay / tts / safety)       |
| Frontend Dev Viewer   | Vanilla HTML/JS/SVG (file:// friendly)                |
| Mirror Integration    | MagicMirror² custom module                            |
| Accessibility         | Reduced-motion CSS strategy, multi-tier TTS chain     |
| Performance Telemetry | CSV logging + /health JSON + adaptive throttling      |
| Tooling               | Calibration + ArUco generator (API version resilient) |

## 7. Performance Characteristics

- Target capture→overlay latency: ≤150 ms (validated via CSV averages on dev hardware; adaptive controls maintain budget).
- Overlay dispatch debounced at ~15 Hz for UI smoothness without overloading WS clients.
- Cloud assist isolated to background with breaker so worst-case network stalls do not raise frame latency tail.

## 8. Accessibility Commitments

- Motion reduction is user-driven (settings) and environment-driven (OS preference can be propagated at frontend).
- Clear textual HUD guidance; color-coded but also structured content for screen reader–friendly TTS fallback.
- Avoids rapid flashing; ring pulses eased and disabled in reduced-motion mode.

## 9. Privacy & Safety Notes

- Default operation is fully on-device (no cloud). Cloud assist is opt-in and rate limited; easy kill-switch.
- Potential future local models (e.g., lightweight action classification) can replace cloud dependency entirely.

## 10. Extensibility Roadmap

| Near-Term                             | Mid-Term                       | Longer-Term                           |
| ------------------------------------- | ------------------------------ | ------------------------------------- |
| Pose-guided brushing coverage scoring | Local CLIP-style hint ranking  | Federated personalization (opt-in)    |
| Multi-tool routines (floss, rinse)    | Hand pose gesture classifier   | Adaptive reward / gamification engine |
| Offline markerless tool tracking      | Local tiny ASR for voice hints | Edge GPU acceleration (NPU / TPU)     |

## 11. Why We Win

- Tight **latency discipline** + **non-blocking cloud** yields pleasant feedback loops.
- Designed-in **accessibility** (not bolted on) broadens impact.
- **Configurable & inspectable** (/health + logs) accelerates iteration and trust.
- Lean **dependency surface** avoids heavy monolithic frameworks; easier to deploy on Pi-class hardware.

## 12. Call to Action

Looking for partners to pilot in pediatric occupational therapy contexts. Next sprint focuses on coverage scoring + richer pose cues. Contributions welcome—open an issue or propose new detector modules.
