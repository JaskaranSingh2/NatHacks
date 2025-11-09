# Live Demo Checklist - AssistiveCoach Smart Mirror

## 🎯 Pre-Demo Setup (10 minutes before)

### 1. Hardware Setup

- [ ] Mirror/display positioned at comfortable height
- [ ] Camera facing user (built-in Mac camera or external)
- [ ] Adequate lighting (avoid backlighting)
- [ ] Audio output working (speakers/headphones)
- [ ] Optional: Printed ArUco markers ready (see `markers/` directory)

### 2. Software Setup

```bash
# Check everything is running
./scripts/quick_status.sh

# If not running, start everything
./scripts/restart_all.sh

# Run live demo setup script
./scripts/live_demo.sh
```

### 3. Camera Permissions (macOS)

- [ ] System Settings → Privacy & Security → Camera
- [ ] Enable camera for Terminal app (or whichever app runs backend)
- [ ] Restart backend if camera was just enabled

### 4. Verify Vision Pipeline

```bash
# Check camera and vision status
curl http://127.0.0.1:8000/health | jq '{camera, vision, fps}'

# Should show:
# {
#   "camera": "on",
#   "vision": "running",
#   "fps": 15-30
# }
```

### 5. Test Overlays

```bash
# Quick overlay test
./scripts/test_display.sh

# Should see ring + HUD on MagicMirror for 10 seconds
```

---

## 🎬 Demo Script

### Opening (1 minute)

**Say:**

> "This is AssistiveCoach, a smart mirror that helps people with daily tasks using computer vision and voice guidance. Watch as it tracks my face and hands in real-time."

**Do:**

- Stand in front of mirror
- Wave hands to show tracking
- Point out the ring overlay and HUD

### Task Demo: Draw Eyebrows (2-3 minutes)

#### Step 1: Open Task Menu

**Say:**

> "I can use keyboard shortcuts or voice commands. Let me select a task."

**Do:**

- Press **T** to open task menu
- Show all 4 available tasks

**Point out:**

- Icons for each task (🪥 🧼 💇 💄)
- Number of steps and duration
- Keyboard shortcuts (1-4)

#### Step 2: Start Draw Eyebrows

**Say:**

> "I'll demonstrate the makeup task - drawing eyebrows. This is a 6-step process."

**Do:**

- Press **4** (or click "Draw Eyebrows")
- Wait for voice prompt to speak

**Point out:**

- Voice speaks: "Step 1: Get your eyebrow pencil, powder, and brush ready"
- HUD shows step title, instruction, and hint
- Ring overlay appears (anchored to face or ArUco marker)
- Progress bar at bottom

#### Step 3: Walkthrough Steps

**For each step, do:**

1. Read the instruction aloud
2. Simulate the action (even without actual makeup)
3. Press **N** to advance

**6 Steps:**

1. **Prepare Tools** - "Getting tools ready..."
2. **Brush Brows** - Simulate brushing motion with spoolie
3. **Fill Sparse Areas** - Simulate pencil strokes
4. **Define Shape** - Show defining arch and tail
5. **Blend and Set** - Simulate blending and gel application
6. **Final Check** - Step back, check symmetry

**Point out:**

- Voice guidance at each step
- HUD updates automatically
- Ring color/size may change per step
- Progress bar advances
- Time estimate shown

#### Step 4: Complete Task

**Say:**

> "Task complete! The system tracked me through all 6 steps with voice and visual guidance."

**Point out:**

- Completion message
- HUD clears
- Ready for next task

### Advanced Features Demo (Optional, 1-2 minutes)

#### ArUco Marker Tracking

**If you have printed markers:**

- Hold marker in camera view
- Show how overlay anchors to marker
- Move marker around, overlay follows

**Say:**

> "The system can track physical markers for precise positioning. This is useful for anchoring instructions to specific objects like a toothbrush or makeup tools."

#### Other Tasks Quick Demo

**Press 1 (Brush Teeth):**

- Show first step
- Press N to advance
- Press Shift+S to stop

**Say:**

> "Each task has its own steps. The system adapts the guidance based on what you're doing."

---

## 🎯 Key Features to Highlight

### Computer Vision

- ✅ Real-time face and hand tracking (MediaPipe)
- ✅ ArUco marker detection and 6-DOF pose estimation
- ✅ Smooth filtering to reduce jitter
- ✅ Overlay anchoring to face or markers

### User Experience

- ✅ Voice guidance at every step (macOS TTS)
- ✅ Clear visual HUD with instructions
- ✅ Keyboard shortcuts for quick navigation
- ✅ Progress tracking and time estimates

### Accessibility

- ✅ High-contrast UI
- ✅ Large, readable text
- ✅ Voice prompts for visually impaired
- ✅ Reduced motion option
- ✅ Helpful hints for each step

### Technology Stack

- ✅ **Backend**: Python, FastAPI, OpenCV, MediaPipe
- ✅ **Frontend**: MagicMirror (Electron/Node.js)
- ✅ **Vision**: OpenCV for ArUco, MediaPipe for face/hands
- ✅ **Communication**: WebSocket for real-time overlays

---

## 🐛 Troubleshooting During Demo

### Camera not working

```bash
# Check camera status
curl http://127.0.0.1:8000/health | jq '.camera'

# Enable vision
curl -X POST http://127.0.0.1:8000/settings \
  -H "Content-Type: application/json" \
  -d '{"pose": true, "hands": true, "aruco": true}'

# Restart backend
./scripts/restart_all.sh
```

### No overlays showing

```bash
# Test overlay directly
curl -X POST http://127.0.0.1:8000/settings \
  -H "Content-Type: application/json" \
  -d '{"overlay_from_aruco": true}'

# Test display script
./scripts/test_display.sh
```

### Voice not speaking

- Check system volume
- Test TTS: `say "Hello, this is a test"`
- Verify macOS TTS is enabled in System Settings

### Keyboard shortcuts not working

- Click on MagicMirror window to focus it
- Check console for logs (F12 in Electron)
- Test via API: `./scripts/test_keyboard_shortcuts.sh`

### Low FPS / Laggy

```bash
# Check current FPS
curl http://127.0.0.1:8000/health | jq '.fps'

# Increase ArUco stride (process less frequently)
curl -X POST http://127.0.0.1:8000/settings \
  -H "Content-Type: application/json" \
  -d '{"aruco_stride": 4}'

# Close other apps
```

---

## 📋 Post-Demo Notes

### Audience Questions to Prepare For

**Q: Does it work with other tasks?**
A: Yes! We have 4 tasks now (brushing teeth, washing face, combing hair, drawing eyebrows). The system is extensible - we can add any ADL task.

**Q: What if someone can't use keyboard?**
A: We're integrating voice commands with Google Vertex AI. Users will be able to say "Hey Mirror, start brushing teeth" or ask questions during tasks.

**Q: How accurate is the tracking?**
A: Face tracking is very accurate (MediaPipe). Hand tracking works well in good lighting. ArUco markers provide <1cm positioning accuracy for objects.

**Q: Can it detect if user completed step correctly?**
A: Not yet - that's future work. Currently manual advancement, but vision pipeline can validate marker presence and hand motions.

**Q: What about privacy?**
A: All processing is local - no video/audio sent to cloud. User can disable camera anytime. Optional cloud features require explicit consent.

**Q: Who is this for?**
A:

- People with cognitive impairments (dementia, brain injury)
- Elderly needing daily routine support
- People learning ADL skills
- Anyone who wants guided assistance

**Q: What's the hardware requirement?**
A:

- Raspberry Pi 4/5 (4GB+ RAM) or any computer
- USB camera or built-in webcam
- Display/monitor (can be two-way mirror)
- ~$200 total for full setup

---

## 🎥 Demo Recording Tips

If recording demo:

- [ ] Start recording before opening MagicMirror
- [ ] Position camera to capture both you and the mirror display
- [ ] Use external mic for better audio
- [ ] Narrate what you're doing in real-time
- [ ] Show closeup of HUD and overlays
- [ ] Demo at least 2 different tasks
- [ ] End with task completion

---

## 🚀 Quick Start Command

```bash
# One command to prepare everything
./scripts/live_demo.sh

# Then in MagicMirror:
# Press T → Press 4 → Follow prompts!
```

---

## ✅ Success Criteria

Demo is successful if:

- ✅ Camera captures video feed
- ✅ Face/hand tracking visible (even without debug view)
- ✅ Task starts when selected
- ✅ Voice speaks instructions at each step
- ✅ HUD updates with each step
- ✅ Ring overlay renders and follows face
- ✅ Can advance through all steps
- ✅ Task completes successfully

**Good luck with the demo! 🎉**
