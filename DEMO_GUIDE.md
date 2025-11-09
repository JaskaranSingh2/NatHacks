# 🎯 Complete Demo Guide - AssistiveCoach Smart Mirror

## Quick Start (< 30 seconds)

```bash
# 1. Start everything
cd /Users/jaskaran/Documents/Engineering/Coding/NatHacks
bash scripts/restart_all.sh

# 2. Open MagicMirror in browser
open http://localhost:8080

# 3. Press 'T' to see task menu OR press '1-4' to start tasks directly
```

## ✅ System Status

**Backend**: Running on port 8000  
**MagicMirror**: Running on port 8080  
**Vision Pipeline**: Active with MediaPipe Face Mesh + Hands  
**Task System**: ✅ WORKING

## 🎮 Keyboard Controls

| Key         | Action                                 |
| ----------- | -------------------------------------- |
| **T**       | Toggle task menu (shows all 4 tasks)   |
| **1**       | Start "Brush Teeth" (6 steps, 2 min)   |
| **2**       | Start "Wash Face" (5 steps, 90 sec)    |
| **3**       | Start "Comb Hair" (4 steps, 60 sec)    |
| **4**       | Start "Draw Eyebrows" (6 steps, 2 min) |
| **N**       | Next step (advances current task)      |
| **Shift+S** | Stop current task                      |

## 📋 Available Tasks

### 1. Brush Teeth 🪥 (120s)

**Steps:**

1. Prepare Toothbrush - Wet brush and apply toothpaste (15s)
2. Brush Upper Teeth - Small circles, gentle pressure (30s)
3. Brush Lower Teeth - Don't forget molars (30s)
4. Brush Tongue - Front to back (15s)
5. Rinse - Swish and spit (15s)
6. Clean Up - Rinse brush, store upright (15s)

### 2. Wash Face 🧼 (90s)

**Steps:**

1. Wet Face - Splash with lukewarm water (10s)
2. Apply Cleanser - Dime-sized amount (10s)
3. Massage Face - Gentle circles, avoid eyes (30s)
4. Rinse Thoroughly - Remove all soap (20s)
5. Pat Dry - Gentle pats with clean towel (10s)

### 3. Comb Hair 💇 (60s)

**Steps:**

1. Section Hair - Divide into manageable sections (10s)
2. Detangle Ends - Work out knots slowly (20s)
3. Brush from Roots - Smooth, even strokes (20s)
4. Style - Your preferred style (10s)

### 4. Draw Eyebrows ✏️ (120s)

**Steps:**

1. Prepare Tools - Get pencil, powder, brush (10s)
2. Brush Brows - Upward with spoolie (15s)
3. Fill Sparse Areas - Light strokes from inner brow (30s)
4. Define Shape - Arch and tail (30s)
5. Blend and Set - Spoolie + brow gel (20s)
6. Final Check - Check symmetry (15s)

## 🔍 Testing Sequence

### Basic Functionality Test

```bash
# 1. Check backend health
curl http://localhost:8000/health

# 2. List available tasks
curl http://localhost:8000/tasks | python3 -m json.tool

# 3. Start a task
curl -X POST http://localhost:8000/tasks/brush_teeth/start | python3 -m json.tool

# 4. Advance to next step
curl -X POST http://localhost:8000/tasks/next_step | python3 -m json.tool

# 5. Stop task
curl -X POST http://localhost:8000/tasks/stop | python3 -m json.tool
```

### Full Demo Walkthrough

```bash
# Run automated test of all tasks
bash scripts/test_all_tasks.sh
```

## 🎬 Demo Script for Judges

### Opening (30s)

1. Show MagicMirror interface (http://localhost:8080)
2. Point out camera preview in bottom-right (live feed with face tracking)
3. Explain accessibility features: high contrast, large text, simple UI

### Task Demo (2 min)

1. **Press 'T'** to show task menu

   - Point out 4 ADL tasks with icons, step counts, duration
   - "These are real Activities of Daily Living for older adults"

2. **Press '1'** to start "Brush Teeth"
   - HUD appears with:
     - Task name and icon
     - Current step (1 of 6)
     - Clear instructions
     - Timer countdown
     - Progress indicator
3. **Wait 15 seconds** (or press 'N' to skip)

   - Timer counts down
   - When time elapses, ready for next step

4. **Press 'N'** twice to show step progression

   - Instructions update
   - Progress bar advances
   - Different face landmarks highlighted

5. **Press 'Shift+S'** to stop task
   - Clean return to ready state

### Technical Deep Dive (1 min)

1. Show camera preview:

   - Live face mesh overlay (468 landmarks)
   - Hand tracking overlays
   - AR ring following detected face
   - ~24 FPS, < 150ms latency

2. Explain architecture:
   - **Backend**: FastAPI + MediaPipe (on-device) + optional Google Vision API
   - **Frontend**: MagicMirror² custom module
   - **AR Anchors**: ArUco markers for stable object-relative cues
   - **Accessibility**: WCAG AA contrast, large targets, predictable flow

### Deployment Path (30s)

- Standard Raspberry Pi 4/5 + Camera Module
- MagicMirror² (open-source, widely deployed)
- MediaPipe runs on-device (privacy-first)
- Cloud Vision API optional for enhanced robustness
- Simple install on any Pi-driven smart mirror

## 🚀 GenAI Enhancements (for pitch)

### Current AI Usage

1. **MediaPipe Face Mesh**: Real-time 468-point facial landmark detection
2. **MediaPipe Hands**: 21-point hand tracking for gesture detection
3. **Google Vision API**: Cloud-based face detection for enhanced accuracy (optional)

### Future GenAI Opportunities

1. **Personalized Coaching**

   - LLM-powered adaptive instructions based on user progress
   - Natural language feedback: "Great job! Let's work on reaching the back molars"
   - Difficulty adjustment based on detected confusion or hesitation

2. **Multimodal Understanding**

   - Vision-Language Model (e.g., GPT-4V) analyzing technique quality
   - Real-time form correction: "Tilt the brush at a 45° angle"
   - Detecting emotional state from facial expressions → encouraging prompts

3. **Conversational Interface**

   - Voice-activated task selection: "Help me brush my teeth"
   - Mid-task clarification: "Show me how to reach that spot"
   - Emergency detection: "I dropped the razor" → alert caregiver

4. **Predictive Assistance**

   - Time-of-day task suggestions based on routine
   - Detecting declining motor skills → adjust task complexity
   - Proactive reminders: "You usually brush your teeth at this time"

5. **Caregiver Insights**
   - LLM-generated weekly summaries of ADL performance
   - Anomaly detection: "Brushing duration decreased 30% this week"
   - Personalized care recommendations

## 🛠 Troubleshooting

### Backend won't start

```bash
# Kill any processes on port 8000
lsof -ti:8000 | xargs kill -9
# Restart
bash scripts/restart_all.sh
```

### MagicMirror blank screen

```bash
# Check logs
tail -f /tmp/magicmirror.log
# Reload
bash scripts/reload_mm.sh
```

### Tasks not responding

```bash
# Check backend is running
curl http://localhost:8000/health
# Check available tasks
curl http://localhost:8000/tasks
# Restart if needed
bash scripts/restart_all.sh
```

### Camera preview not updating

```bash
# Check preview endpoint
curl -I http://localhost:8000/preview.jpg
# Should return 200 OK with Content-Type: image/jpeg
# If not, check backend logs:
tail -f /tmp/assistive-backend.log
```

## 📊 Performance Metrics

- **Latency**: < 150ms end-to-end (camera → overlay)
- **FPS**: 24 fps (configurable)
- **Resolution**: 1280x720 (optimized for Pi)
- **Face Detection**: 468 landmarks via MediaPipe
- **Hand Tracking**: 21 landmarks per hand
- **Task Steps**: 4-6 steps per task
- **Task Duration**: 60-120 seconds per task

## 🎯 Success Criteria

✅ Real-time camera feed with overlays  
✅ Task system with step-by-step guidance  
✅ Keyboard controls for demo resilience  
✅ High-contrast, accessible UI  
✅ Low-latency vision pipeline (< 150ms)  
✅ Works on Raspberry Pi 4/5  
✅ MagicMirror² integration  
✅ ArUco marker support for AR anchoring

## 📝 Quick Notes

- WebSocket (port 5055) is optional - HTTP API works fine without it
- Camera permissions may be needed on first run
- All tasks include voice prompts (TTS) when enabled
- ArUco markers (IDs 1-4) can be placed near tools for enhanced AR
- Wizard-of-Oz mode (keyboard shortcuts) ensures demo never fails

## 🔗 Important URLs

- Backend API: http://localhost:8000
- MagicMirror: http://localhost:8080
- Health Check: http://localhost:8000/health
- Camera Preview: http://localhost:8000/preview.jpg
- Task List: http://localhost:8000/tasks
- API Docs: http://localhost:8000/docs

---

**Last Updated**: 2025-11-09  
**Status**: ✅ Fully Working Demo Ready
