# Bash Testing Scripts

Quick reference for all available bash test scripts in `scripts/` directory.

## 🚀 Quick Commands

### System Control
```bash
# Restart backend + MagicMirror
./scripts/restart_all.sh

# Quick system status check
./scripts/quick_status.sh

# Reload MagicMirror only
./scripts/reload_mm.sh
```

### Testing Scripts

#### Test All Tasks
```bash
./scripts/test_all_tasks.sh
```
Tests all 4 tasks (Brush Teeth, Wash Face, Comb Hair, Draw Eyebrows) by starting, advancing steps, and stopping.

#### Test Keyboard Shortcuts
```bash
./scripts/test_keyboard_shortcuts.sh
```
Simulates keyboard shortcuts 1-4 by calling task API endpoints directly.

#### Test New Eyebrows Task
```bash
./scripts/test_eyebrows_task.sh
```
Complete test of the Draw Eyebrows task (the new makeup task that replaced "Put on Shirt").

#### Test All Tasks
```bash
./scripts/test_all_tasks.sh
```
Sequential test of all 4 tasks with step advancement.

### Vision & OpenCV

#### Check OpenCV Integration
```bash
./scripts/check_opencv.sh
```
Verifies:
- OpenCV installation and version
- ArUco module availability
- Camera intrinsics calibration
- Available marker images
- Integration summary

#### Test ArUco Detection
```bash
./scripts/test_aruco.sh
```
Tests ArUco marker detection (requires physical marker).

#### Test Vision Pipeline
```bash
./scripts/test_vision_pipeline.sh
```
Tests complete vision pipeline with overlays.

### Development

#### Test Display/Overlays
```bash
./scripts/test_display.sh
```
Tests ring + HUD overlay rendering.

#### Complete Demo
```bash
./scripts/demo_complete.sh
```
Runs automated demo of complete task system.

#### Disable Compliments
```bash
./scripts/disable_compliments.sh
```
Removes "Hey there sexy" compliment module.

## 📊 Output Examples

### Quick Status
```
🚀 AssistiveCoach System Status
================================

1️⃣ Backend Status:
   ✅ Running on port 8000
   • Camera: off
   • Vision: null
   • FPS: 0.0

2️⃣ MagicMirror Status:
   ✅ Running on port 8080

3️⃣ Available Tasks:
   brush_teeth: Brush Teeth 🪥 (6 steps)
   wash_face: Wash Face 🧼 (5 steps)
   comb_hair: Comb Hair 💇 (4 steps)
   draw_eyebrows: Draw Eyebrows 💄 (6 steps)

4️⃣ Active Task:
   ℹ️  No active task
```

### Test Keyboard Shortcuts
```
🧪 Testing Keyboard Shortcuts (Simulating via API)
==================================================

   Key 1 → Starting 'Brush Teeth'...
   ✅ Task started

   Key 2 → Starting 'Wash Face'...
   ✅ Task started

   Key 3 → Starting 'Comb Hair'...
   ✅ Task started

   Key 4 → Starting 'Draw Eyebrows' (NEW TASK!)...
   ✅ Task started
```

### OpenCV Check
```
🔍 OpenCV Integration Status Check
====================================

3️⃣ Checking Python OpenCV installation...
   ✅ OpenCV 4.9.0
   ArUco: True

4️⃣ Checking camera intrinsics file...
   ✅ Intrinsics file exists

5️⃣ Checking ArUco markers...
   ✅ Found 2 ArUco marker images
```

## 🎯 Typical Workflow

### Starting Development
```bash
# Check system status
./scripts/quick_status.sh

# Restart if needed
./scripts/restart_all.sh
```

### Testing Features
```bash
# Test all tasks work
./scripts/test_all_tasks.sh

# Test keyboard shortcuts
./scripts/test_keyboard_shortcuts.sh

# Verify OpenCV integration
./scripts/check_opencv.sh
```

### Debugging
```bash
# Check logs
tail -f /tmp/assistive-backend.log
tail -f /tmp/magicmirror.log

# Test specific task
curl -s -X POST http://127.0.0.1:8000/tasks/draw_eyebrows/start | jq

# Check health endpoint
curl -s http://127.0.0.1:8000/health | jq
```

## 📝 Script Maintenance

All scripts are located in `scripts/` directory and are executable:
```bash
chmod +x scripts/*.sh
```

To add a new script:
1. Create script in `scripts/`
2. Add shebang: `#!/bin/bash`
3. Make executable: `chmod +x scripts/your_script.sh`
4. Document in this file

## 🔧 Dependencies

Scripts require:
- `curl` - HTTP requests
- `jq` - JSON parsing
- `python3` - Backend runtime
- `npm` - MagicMirror runtime

Install jq if missing:
```bash
brew install jq  # macOS
```

## 📚 Related Documentation

- **OPENCV_INTEGRATION.md** - OpenCV technical details
- **FUTURE_FEATURES.md** - Potential features roadmap
- **VERTEX_AI_INTEGRATION.md** - Voice assistant integration
- **ALL_FIXES_SUMMARY.md** - Complete fixes summary
