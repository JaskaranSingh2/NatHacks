# 🎉 Live Demo Ready!

## ✅ System Status

**Backend:** Running on port 8000  
**MagicMirror:** Running on port 8080 (http://localhost:8080)  
**Vision Pipeline:** Initialized with pose estimation available  
**Camera Intrinsics:** Loaded successfully  
**Tasks:** All 4 tasks available (including Draw Eyebrows 💄)

## 📋 Pre-Demo Checklist

### System is Running ✅

- [x] Backend started successfully
- [x] MagicMirror opened in browser
- [x] Vision pipeline initialized
- [x] Camera intrinsics file loaded
- [x] WebSocket connection established
- [x] All 4 tasks available

### Features Configured ✅

- [x] Keyboard shortcuts (1-4, N, T) working
- [x] Draw Eyebrows task (6 steps, 120s)
- [x] OpenCV integration complete
- [x] Face/hands/pose detection enabled
- [x] ArUco marker detection enabled

### Ready for Demo ⏳

- [ ] **Camera permissions granted** (see below)
- [ ] Camera status shows "on"
- [ ] Vision FPS > 0
- [ ] Face detection working
- [ ] Overlays rendering

## 🎥 Enable Camera (REQUIRED)

The camera is currently "off" because macOS requires explicit permission. Follow these steps:

### Method 1: Grant Permission via System Settings

1. Open **System Settings** → **Privacy & Security** → **Camera**
2. Look for **Terminal** or **Python** in the list
3. Toggle permission **ON** for the app running the backend
4. Restart the backend: `./scripts/restart_all.sh`

### Method 2: Trigger Permission Dialog

1. The backend will automatically request camera access
2. When you see the permission dialog, click **OK** or **Allow**
3. If dialog doesn't appear, try Method 1

### Verify Camera is Working

```bash
curl http://127.0.0.1:8000/health 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'Camera: {d.get(\"camera\")}\nFPS: {d.get(\"fps\", 0):.1f}')"
```

Expected output when working:

```
Camera: on
FPS: 15.0  (or higher)
```

## 🎬 Running the Live Demo

### Step 1: Prepare the Environment

1. **Position yourself** in front of the camera
2. **Good lighting** - face should be clearly visible
3. **ArUco markers** ready (optional, in `markers/` directory)
4. **MagicMirror** visible on screen (http://localhost:8080)

### Step 2: Demo Flow

1. **Open Task Menu** - Press `T` key
2. **Select Draw Eyebrows** - Press `4` key
3. **Follow the 6 steps:**

   - Step 1: Prepare Tools (gather makeup)
   - Step 2: Brush Brows (upward strokes)
   - Step 3: Fill Sparse Areas (light strokes)
   - Step 4: Define Shape (outline brows)
   - Step 5: Blend and Set (blending powder)
   - Step 6: Final Check (compare with mirror)

4. **Advance steps** - Press `N` key for next step
5. **Watch the overlays:**
   - Ring overlay follows your face
   - HUD shows task name, step number, timer
   - Voice guidance speaks each step
   - Progress bar updates

### Step 3: Show Features

- **Face Tracking:** Move your head - ring follows
- **Keyboard Shortcuts:** Press 1-4 to switch tasks
- **Voice Feedback:** Audio guidance for each step
- **Progress Tracking:** Visual timer and step counter
- **Task Completion:** Complete all 6 steps

### Step 4: Demo Other Tasks (Optional)

- Press `T` to open menu
- Press `1` for Brush Teeth (6 steps)
- Press `2` for Wash Face (5 steps)
- Press `3` for Comb Hair (4 steps)

## 🐛 Troubleshooting

### Camera Still Showing "off"

```bash
# Check camera permission
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Camera"

# Restart everything
./scripts/restart_all.sh

# Wait 3 seconds, then enable vision
curl -X POST http://127.0.0.1:8000/settings \
  -H "Content-Type: application/json" \
  -d '{"pose": true, "hands": true, "aruco": true, "face": true}'
```

### Vision FPS is 0

- Camera permissions not granted
- Camera in use by another app
- Check logs: `tail -f /tmp/assistive-backend.log`

### MagicMirror Not Responding

```bash
# Check if running
curl http://localhost:8080 2>&1 | head -5

# Restart if needed
./scripts/restart_all.sh
```

### Overlays Not Showing

- WebSocket disconnected - refresh browser (F5)
- Check browser console for errors (F12)
- Verify backend is sending data: `tail -f /tmp/assistive-backend.log | grep "WS"`

### Keyboard Shortcuts Not Working

- Click on the MagicMirror window to focus
- Check browser console (F12) for logs
- Keys should log: "Keyboard shortcut pressed: X"

## 📊 System Commands

### Quick Status Check

```bash
./scripts/quick_status.sh
```

### Restart Everything

```bash
./scripts/restart_all.sh
```

### Test All Tasks

```bash
./scripts/test_all_tasks.sh
```

### Test Draw Eyebrows

```bash
./scripts/test_eyebrows_task.sh
```

### Check OpenCV Integration

```bash
./scripts/check_opencv.sh
```

## 🎯 Demo Script

### Introduction (30 seconds)

"Welcome! This is AssistiveCoach - an AI-powered system that helps people with ADL (Activities of Daily Living) tasks using computer vision and AR overlays. Today I'll demonstrate the Draw Eyebrows task."

### Show the Interface (30 seconds)

"Here's the MagicMirror interface. I can use keyboard shortcuts to navigate:

- Press T to open the task menu
- Press 1-4 to select different tasks
- Press N to advance to the next step"

### Run Draw Eyebrows Task (2 minutes)

"Let me show you the Draw Eyebrows task - it has 6 steps and takes about 2 minutes:

1. First, prepare your tools
2. Brush your brows upward
3. Fill in sparse areas
4. Define the shape
5. Blend and set
6. Final check

Watch as the system:

- Tracks my face in real-time
- Shows step-by-step instructions
- Provides voice guidance
- Displays a visual timer"

### Highlight Features (30 seconds)

"Key features:

- Real-time face tracking with OpenCV
- ArUco marker detection for precision
- Voice feedback for accessibility
- Visual overlays anchored to your face
- Multiple ADL tasks (grooming, hygiene)"

### Q&A (remainder)

"Happy to answer questions about:

- Technical architecture
- Vision pipeline
- Task system
- Future features
- Accessibility considerations"

## 📁 Important Files

- **Backend:** `/backend/app.py` (FastAPI server)
- **Frontend:** `/mirror/modules/MMM-AssistiveCoach/`
- **Tasks:** `/backend/task_system.py`
- **Vision:** `/backend/vision_pipeline.py`
- **Scripts:** `/scripts/` (all automation)
- **Docs:** `LIVE_DEMO_CHECKLIST.md`, `OPENCV_INTEGRATION.md`

## 🚀 Next Steps After Demo

1. Grant camera permissions (if not done)
2. Verify FPS > 0 (camera working)
3. Test all 4 tasks
4. Show face tracking with overlays
5. Demonstrate keyboard shortcuts
6. Complete full Draw Eyebrows walkthrough
7. Q&A with audience

## 📝 Demo Notes

**Completed:**

- ✅ System running (backend + MagicMirror)
- ✅ Vision pipeline initialized
- ✅ Camera intrinsics loaded
- ✅ All tasks available
- ✅ Keyboard shortcuts working
- ✅ OpenCV fully integrated

**Pending:**

- ⏳ Camera permissions (macOS security)
- ⏳ Camera status = "on"
- ⏳ Vision FPS > 0

**Once camera is enabled, the demo is 100% ready!**

---

_Last updated: 2025-11-09 01:00 AM_
_System: macOS | Python 3.12 | OpenCV 4.9.0 | FastAPI | MagicMirror | Electron_
