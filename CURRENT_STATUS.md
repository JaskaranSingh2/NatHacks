# AssistiveCoach System Status - November 9, 2025

## 🎯 **WHAT WE'RE TRYING TO DO**

Build a smart mirror that:

1. Uses a camera to detect your face and hands
2. Shows AR overlays to guide you through daily tasks (brushing teeth, washing face, etc.)
3. Displays a live preview of what the camera sees with detection visualizations

## 🔥 **CRITICAL CURRENT ISSUE**

**The camera preview panel in the bottom-right corner is showing up BUT IT'S EMPTY/BLACK.**

### Why It's Empty

The preview endpoint `/preview.jpg` returns `{"detail": "Preview unavailable"}` (404 error) because `_preview_buffer` in `backend/app.py` is `None`.

### The Root Problem

There's a **mysterious code execution issue** in `backend/vision_pipeline.py`:

```python
# Lines 446-457 in vision_pipeline.py
if frame_count % 30 == 0:
    LOGGER.info(f"Encoding preview frame {frame_count}")  # ✅ THIS LOG APPEARS
try:
    from backend.app import set_preview_frame
    LOGGER.info(f"Imported set_preview_frame: {set_preview_frame}")  # ❌ THIS NEVER APPEARS
    prev_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode(".jpg", prev_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
    LOGGER.info(f"Encoded {len(buffer)} bytes")  # ❌ THIS NEVER APPEARS
    set_preview_frame(bytes(buffer))
    LOGGER.info("set_preview_frame called successfully")  # ❌ THIS NEVER APPEARS
except Exception as e:
    LOGGER.error(f"Preview encode failed: {e}")  # ❌ THIS NEVER APPEARS
```

**LOGS SHOW:**

- ✅ "Encoding preview frame 30" - appears every 30 frames
- ❌ None of the logs INSIDE the try block ever appear
- ❌ No exceptions are being caught

**This means:** The code execution somehow stops or skips after the first LOGGER.info but before entering the try block. This is extremely weird and suggests either:

1. An indentation issue (but we checked, it looks correct)
2. A bytecode/compilation issue
3. Some Python runtime weirdness
4. The file isn't being reloaded properly

---

## 📦 **WHAT'S INSTALLED AND RUNNING**

### Backend (Port 8000)

- **Status:** ✅ Running (PID varies)
- **Framework:** FastAPI + Uvicorn
- **Camera:** ✅ Working at ~60 FPS (Mac camera, AVFoundation backend)
- **Vision Processing:** ✅ MediaPipe NOW installed and initialized
  - MediaPipe Face Mesh: ✅ Initialized
  - MediaPipe Hands: ✅ Initialized
  - ArUco markers: ✅ Available
- **Issues:**
  - Preview encoding code not executing properly
  - `_preview_buffer` stays None

### Frontend (Port 8080)

- **Status:** ✅ Running (MagicMirror)
- **Framework:** Electron + MagicMirror²
- **Issues:**
  - Preview panel exists but shows nothing (waiting for backend to provide images)

---

## 🗂️ **KEY FILES AND THEIR STATUS**

### `backend/app.py` (FastAPI server)

**Lines 282-348: Preview system**

```python
# Line 282: Global preview buffer (currently None)
_preview_buffer: Optional[bytes] = None
_preview_lock = threading.Lock()

# Line 339-342: Function to update preview (MODIFIED with logging)
def set_preview_frame(jpeg_bytes: bytes) -> None:
    global _preview_buffer
    import logging
    logger = logging.getLogger("assistivecoach.backend")
    with _preview_lock:
        _preview_buffer = jpeg_bytes
        if len(jpeg_bytes) > 0:
            logger.info(f"Preview buffer updated: {len(jpeg_bytes)} bytes")  # ❌ Never logs

# Line 345-348: Function to get preview
async def get_preview_frame() -> Optional[bytes]:
    global _preview_buffer
    with _preview_lock:
        return _preview_buffer  # Always returns None

# Line 632-636: Preview endpoint
@app.get("/preview.jpg")
async def get_preview() -> Response:
    frame = await get_preview_frame()
    if frame is None:  # ❌ Always None
        raise HTTPException(status_code=404, detail="Preview unavailable")
    return Response(content=frame, media_type="image/jpeg")
```

**Current State:**

- ✅ Preview endpoint registered
- ✅ `set_preview_frame()` function exists and is importable
- ❌ Never gets called from vision_pipeline
- ❌ `_preview_buffer` stays None forever

### `backend/vision_pipeline.py` (Camera + CV processing)

**Lines 265-275: Main processing loop**

```python
while self._running and not self._stop_event.is_set():
    frame_rgb, capture_ts_ns = self.camera.read()  # ✅ Working
    frame_count += 1
    if frame_count % 120 == 0:
        LOGGER.info(f"Processing frame {frame_count}")  # ❌ Never logs (why?)
```

**Lines 437-457: Debug overlay and preview encoding (THE PROBLEM AREA)**

```python
# Line 437-443: Draw debug overlays
shapes_end_perf = time.perf_counter()

if frame_count % 60 == 0:
    LOGGER.info(f"About to draw overlays, frame {frame_count}")  # ✅ Logs appear
self._draw_debug_overlays(frame_rgb, landmarks, hand_landmarks, ar_anchors)  # ❓ Executes?

# Line 445-457: Encode preview (THE BROKEN PART)
if frame_count % 30 == 0:
    LOGGER.info(f"Encoding preview frame {frame_count}")  # ✅ Logs appear
try:
    from backend.app import set_preview_frame
    LOGGER.info(f"Imported set_preview_frame: {set_preview_frame}")  # ❌ NEVER LOGS
    # ... rest of code never executes
```

**Lines 731-796: Debug overlay drawing method**

```python
def _draw_debug_overlays(self, frame_rgb, landmarks, hand_landmarks, ar_anchors):
    """Draw green dots for face, blue for hands, red for ArUco, status HUD."""
    # Draws on frame_rgb in-place
    # Should show face landmarks, hand landmarks, ArUco markers, FPS counter
    # ❓ Is this executing? No logs to confirm.
```

**Current State:**

- ✅ Camera capturing at 60 FPS
- ✅ MediaPipe processing frames
- ✅ Face/hand detection working
- ✅ "Encoding preview frame" log appears
- ❌ Code inside try block NEVER executes (no logs, no exceptions)
- ❌ Preview not being generated

### `backend/camera_capture.py` (Camera interface)

**Lines 21-30: Constructor (FIXED)**

```python
def __init__(self, width: int = 1280, height: int = 720, fps: int = 30,
             device: int = 0, health_state: Any = None, set_preview_fn: Any = None):
    self.health_state = health_state  # ✅ Fixed circular import
    self.set_preview_fn = set_preview_fn  # ✅ Accepts preview function
```

**Lines 158-160: Old preview encoding (NOW OBSOLETE)**

```python
# This used to encode preview, but now vision_pipeline should do it AFTER drawing overlays
prev_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
_, buffer = cv2.imencode(".jpg", prev_bgr)
self.set_preview_fn(bytes(buffer))  # ⚠️ This still runs but gets OVERWRITTEN by vision_pipeline
```

**Current State:**

- ✅ Camera working
- ✅ No circular import issues
- ⚠️ Still creates preview frames WITHOUT overlays (but should be overwritten by vision_pipeline)

### `mirror/modules/MMM-AssistiveCoach/MMM-AssistiveCoach.js` (Frontend UI)

**Lines 78-94: Camera preview panel (ADDED)**

```javascript
// Create preview panel
const preview = document.createElement("img");
preview.id = "camera-preview";
preview.style.cssText = `
  position: fixed; bottom: 20px; right: 20px;
  width: 320px; height: 240px;
  border: 3px solid #00bcd4;  // Cyan border
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  z-index: 9999;
`;
preview.src = `${apiBase}/preview.jpg?t=${Date.now()}`;
setInterval(() => {
	preview.src = `${apiBase}/preview.jpg?t=${Date.now()}`;
}, 100); // Refresh every 100ms (10 FPS)
```

**Current State:**

- ✅ Preview panel renders on screen (bottom-right corner)
- ✅ Border and styling correct
- ❌ Empty/black because backend returns 404

---

## 🔍 **DEBUGGING JOURNEY**

### Issue #1: MediaPipe Not Installed ✅ FIXED

**Symptom:** Vision pipeline running in "synthetic mode"
**Log:** `WARNING assistivecoach.vision MediaPipe not available; using synthetic mode`
**Cause:** MediaPipe package not installed
**Fix:** `pip3 install mediapipe` (via install_python_packages tool)
**Result:** MediaPipe now loads successfully

### Issue #2: Preview Code Not Executing ❌ CURRENT PROBLEM

**Symptom:** Preview endpoint returns 404, `_preview_buffer` is None
**Logs:**

- ✅ "Encoding preview frame 30" appears
- ❌ "Imported set_preview_frame" NEVER appears
- ❌ "Preview buffer updated" NEVER appears
  **Debugging attempts:**

1. Added detailed logging inside try block - logs never appear
2. Added exception handler - never catches anything
3. Checked for import errors - none found
4. Verified set_preview_frame exists and is importable - it is
5. Added logging in set_preview_frame itself - never called

**Theories:**

1. **Code not being reloaded:** Python might be running old bytecode (.pyc files)
2. **Indentation corruption:** Whitespace issue invisible in editor
3. **Runtime issue:** Some weird Python threading or scoping problem
4. **Early return:** Code path doesn't reach this point (but "Encoding preview" logs say it does)

---

## 📝 **CODE MODIFICATIONS MADE TODAY**

### Attempt 1: Move preview encoding to vision_pipeline

- **Goal:** Encode frames AFTER drawing debug overlays
- **Changes:**
  - `vision_pipeline.py:439-449`: Added preview encoding after `_draw_debug_overlays()`
  - Imports `set_preview_frame` from `backend.app`
  - Converts RGB to BGR, encodes as JPEG, calls `set_preview_frame()`
- **Result:** ❌ Code doesn't execute (logs don't appear)

### Attempt 2: Add extensive logging

- **Goal:** Figure out where execution stops
- **Changes:**
  - Added `LOGGER.info()` before import, after import, after encode, after call
  - Added logging inside `set_preview_frame()` function
  - Added frame count logging at loop start
- **Result:** ❌ Only logs BEFORE the try block appear

### Attempt 3: Install MediaPipe

- **Goal:** Fix "synthetic mode" issue
- **Changes:** `pip3 install mediapipe`
- **Result:** ✅ SUCCESS - MediaPipe now working
  - Face Mesh initialized
  - Hands initialized
  - Detection processing at 60 FPS

---

## 🎨 **EXPECTED BEHAVIOR (What SHOULD happen)**

1. **Camera captures frame** → 60 FPS ✅ WORKING
2. **MediaPipe processes frame** → Face/hand landmarks detected ✅ WORKING
3. **`_draw_debug_overlays()` called** → Draws green dots on face, blue on hands, red on ArUco ❓ UNKNOWN
4. **Frame encoded as JPEG** → Convert RGB→BGR, encode with quality 85 ❌ NOT EXECUTING
5. **`set_preview_frame()` called** → Updates `_preview_buffer` ❌ NEVER CALLED
6. **Frontend requests `/preview.jpg`** → Returns JPEG from buffer ❌ RETURNS 404
7. **Preview panel displays image** → Shows camera with overlays ❌ EMPTY/BLACK

**Current reality:** Steps 1-2 work, steps 4-7 fail, step 3 unknown.

---

## 🛠️ **NEXT STEPS TO TRY**

### Option A: Force Python to reload

```bash
# Clear Python cache and restart
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
./scripts/restart_all.sh
```

### Option B: Check file encoding/indentation

```bash
# Check for weird whitespace
cat -A backend/vision_pipeline.py | sed -n '445,457p'

# Or use Python to check indentation
python3 -m py_compile backend/vision_pipeline.py
```

### Option C: Move preview encoding to a separate method

Instead of inline code, create a method:

```python
def _update_preview(self, frame_rgb):
    try:
        from backend.app import set_preview_frame
        prev_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode(".jpg", prev_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
        set_preview_frame(bytes(buffer))
    except Exception as e:
        LOGGER.error(f"Preview failed: {e}")
```

### Option D: Use camera_capture's preview (workaround)

The camera already creates preview frames. We could:

1. Pass the annotated frame back to camera_capture
2. Let camera_capture handle JPEG encoding
3. Use its existing preview mechanism

### Option E: Global function instead of import

Make `set_preview_frame` available globally when vision pipeline starts:

```python
# In vision_pipeline.__init__
from backend.app import set_preview_frame
self.set_preview_fn = set_preview_frame

# Then in processing loop
self.set_preview_fn(bytes(buffer))
```

---

## 📊 **SYSTEM ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────┐
│                    MagicMirror (Port 8080)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  MMM-AssistiveCoach.js                               │   │
│  │  - Shows overlays (blue ring, task steps)            │   │
│  │  - Camera preview panel (bottom-right, 320x240)      │   │
│  │  - Refreshes preview every 100ms from backend        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP / WebSocket
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Port 8000)               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  app.py (FastAPI endpoints)                          │   │
│  │  - GET /health (camera status, FPS)                  │   │
│  │  - GET /preview.jpg ← ❌ RETURNS 404                 │   │
│  │  - POST /tasks/{id}/start                            │   │
│  │  - WebSocket /ws (overlay updates)                   │   │
│  │  - _preview_buffer: None ← ❌ NEVER UPDATED          │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  vision_pipeline.py (CV processing thread)           │   │
│  │  - MediaPipe Face Mesh ✅ 60 FPS                     │   │
│  │  - MediaPipe Hands ✅ Detecting                      │   │
│  │  - ArUco markers ✅ Available                        │   │
│  │  - _draw_debug_overlays() ❓ Executing?             │   │
│  │  - Preview encoding ❌ CODE NOT RUNNING              │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  camera_capture.py (Camera interface)                │   │
│  │  - Mac camera via OpenCV ✅ 60 FPS                   │   │
│  │  - Provides RGB frames ✅                            │   │
│  │  - Old preview encoding ⚠️ Still runs                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 **VERIFICATION COMMANDS**

### Check if backend is running

```bash
curl -s http://127.0.0.1:8000/health | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'Camera: {d[\"camera\"]}\nFPS: {d.get(\"fps\", 0):.1f}')"
```

**Expected:** Camera: on, FPS: 60+
**Actual:** ✅ Working

### Check if preview is available

```bash
curl -s -o /tmp/test.jpg http://127.0.0.1:8000/preview.jpg && file /tmp/test.jpg
```

**Expected:** /tmp/test.jpg: JPEG image data
**Actual:** ❌ /tmp/test.jpg: JSON data (404 error)

### Check backend logs for preview activity

```bash
tail -100 /tmp/assistive-backend.log | grep -E "Preview|Encoding|set_preview"
```

**Expected:** See "Preview buffer updated" messages
**Actual:** ❌ Only see "Encoding preview frame" (code stops before import)

### Check if MediaPipe is loaded

```bash
head -60 /tmp/assistive-backend.log | grep -E "MediaPipe|synthetic"
```

**Expected:** "MediaPipe Face Mesh initialized"
**Actual:** ✅ Shows MediaPipe initialized (after installing package)

---

## 🐛 **KNOWN BUGS AND ISSUES**

### HIGH PRIORITY

1. **Preview encoding code not executing** ❌ BLOCKING

   - Logs before try block appear
   - Logs inside try block never appear
   - No exceptions thrown
   - Unknown cause

2. **`_preview_buffer` stays None** ❌ BLOCKING
   - `set_preview_frame()` never called
   - Preview endpoint returns 404
   - Frontend shows empty panel

### MEDIUM PRIORITY

3. **Blue ring stuck in center** ⚠️ VISUAL BUG

   - Should track face center
   - Currently positioned at screen center
   - Needs face landmark → screen coordinate mapping

4. **Task system not triggering overlays** ⚠️ FUNCTIONALITY
   - Starting a task doesn't change overlay behavior
   - session_state updated but overlays don't respond
   - Needs verification of task → vision pipeline connection

### LOW PRIORITY

5. **Pydantic deprecation warnings** ⚠️ TECHNICAL DEBT

   - Using V1 `@validator` syntax
   - Should migrate to V2 `@field_validator`
   - Non-critical, just warnings

6. **FastAPI deprecation warnings** ⚠️ TECHNICAL DEBT
   - `@app.on_event()` deprecated
   - Should use lifespan handlers
   - Non-critical, just warnings

---

## 🗺️ **PROJECT FILE STRUCTURE**

```
NatHacks/
├── backend/
│   ├── app.py                    # FastAPI server, endpoints, preview buffer
│   ├── vision_pipeline.py        # Camera + MediaPipe processing ❌ ISSUE HERE
│   ├── camera_capture.py         # Camera interface ✅ FIXED
│   ├── task_system.py            # Task management
│   ├── cloud_vision.py           # Google Cloud Vision integration
│   ├── ar_overlay.py             # ArUco marker handling
│   ├── drawing_overlay.py        # Overlay shape generation
│   └── requirements.txt          # Python dependencies
├── mirror/
│   └── modules/
│       └── MMM-AssistiveCoach/
│           ├── MMM-AssistiveCoach.js  # Frontend module ✅ PREVIEW PANEL ADDED
│           ├── node_helper.js         # Node backend
│           └── styles.css             # Styling
├── config/
│   ├── features.json             # Feature flags
│   ├── tasks.json                # ADL task definitions
│   ├── tools.json                # Tool/object tracking
│   └── camera_intrinsics.yml     # Camera calibration
├── scripts/
│   ├── restart_all.sh            # Restart both servers
│   ├── calibrate_cam.py          # Camera calibration
│   └── gen_aruco.py              # Generate ArUco markers
├── logs/
│   └── latency.csv               # Performance metrics
├── CURRENT_STATUS.md             # ← YOU ARE HERE
├── CAMERA_FIXED.md               # Previous fix documentation
├── SYSTEM_WORKING.md             # System overview
├── ACCESSIBILITY.md              # Accessibility features
├── ARUCO_GUIDE.md                # ArUco marker guide
└── README.md                     # Project overview
```

---

## 🎯 **ULTIMATE GOALS (Why we're doing this)**

1. **Assistive Technology:** Help people with cognitive/motor impairments complete daily tasks
2. **Real-time Feedback:** Visual cues appear exactly where needed (on toothbrush, near face, etc.)
3. **Task Guidance:** Step-by-step instructions with progress tracking
4. **Accessibility:** Voice feedback, high contrast, motion-reduced mode
5. **Demo-ready:** Working end-to-end demo for hackathon/presentation

**Current Status:** 70% there

- ✅ Camera working
- ✅ MediaPipe face/hand detection working
- ✅ Task system functional
- ✅ Frontend UI rendering
- ❌ Preview visualization broken (main blocker)
- ❌ Face tracking overlay needs work
- ⚠️ End-to-end flow not verified

---

## 💡 **THINGS THAT ACTUALLY WORK**

1. **Camera Capture** - 60 FPS, Mac camera, AVFoundation
2. **MediaPipe Detection** - Face Mesh + Hands running at 60 FPS
3. **FastAPI Backend** - All endpoints responding
4. **MagicMirror Frontend** - Rendering, WebSocket connected
5. **Task System** - Can start/stop/advance tasks
6. **ArUco Detection** - Marker tracking available
7. **Circular Import Fix** - camera_capture no longer has import issues
8. **Preview Panel UI** - Exists on screen, styled correctly, just empty

---

## 🚨 **IMMEDIATE ACTION NEEDED**

**The ONE thing blocking everything:** Figure out why the preview encoding code in `vision_pipeline.py` lines 448-456 doesn't execute even though:

- The code before it runs (logs appear)
- The code after it runs (broadcasts work)
- No exceptions are thrown
- The function exists and is importable
- The try block should catch everything

**This is bizarre and needs investigation of:**

- Python bytecode cache (.pyc files)
- File encoding issues
- Indentation corruption
- Some weird Python runtime behavior
- Whether `_draw_debug_overlays()` crashes silently

**RESTART FROM SCRATCH OPTION:**
If nothing works, rewrite the preview system from scratch:

1. Create new `preview_manager.py` module
2. Simple function that takes frame, encodes, stores
3. Import at top of vision_pipeline, not inside loop
4. Call it directly, no try/except initially

---

## 📈 **PERFORMANCE METRICS**

- **Camera FPS:** 60-63 FPS (excellent)
- **Vision Processing:** 60 FPS (real-time)
- **Preview Refresh Rate:** Should be 10 FPS (100ms interval) - NOT WORKING
- **Overlay Broadcast:** ~15 Hz (debounced)
- **WebSocket Latency:** <50ms (good)
- **Memory Usage:** Stable (no leaks detected)
- **CPU Usage:** ~20% single core (acceptable)

---

## 🔧 **ENVIRONMENT INFO**

- **OS:** macOS (M4 Pro chip)
- **Python:** 3.12
- **OpenCV:** 4.9.0 with AVFoundation backend
- **MediaPipe:** Latest (just installed)
- **Node.js:** Latest (for MagicMirror)
- **Ports:** 8000 (backend), 8080 (MagicMirror)
- **Camera:** Mac built-in camera, permissions granted

---

## 📞 **WHEN YOU COME BACK**

1. **First, try this quick fix:**

   ```bash
   cd /Users/jaskaran/Documents/Engineering/Coding/NatHacks
   find . -name "*.pyc" -delete
   find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
   ./scripts/restart_all.sh
   sleep 5
   curl -s http://127.0.0.1:8000/preview.jpg -o /tmp/test.jpg && file /tmp/test.jpg
   ```

   If it says "JPEG image data", YOU'RE DONE! 🎉

2. **If that doesn't work, read `vision_pipeline.py` lines 445-457 carefully**

   - Check if there's weird whitespace
   - Check if indentation is actually spaces not tabs
   - Try deleting the whole block and rewriting it

3. **If still broken, try Option E from "NEXT STEPS TO TRY"**

   - Import `set_preview_frame` once at init, not in loop
   - Store as instance variable
   - Call directly without try/except

4. **Check the logs:**
   ```bash
   tail -f /tmp/assistive-backend.log | grep -E "Preview|Encoding|MediaPipe"
   ```

Good luck! The system is SO CLOSE to working. Just this one weird Python execution issue...

---

_Last updated: November 9, 2025, 1:38 AM_
_Status: MediaPipe installed ✅, Preview broken ❌_
_Frustration level: HIGH_
_Progress: 70%_
