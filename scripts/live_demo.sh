#!/bin/bash
# Complete live demo setup with camera and vision pipeline

BACKEND_URL="http://127.0.0.1:8000"

echo "🎬 AssistiveCoach Live Demo Setup"
echo "=================================="
echo ""

# Step 1: Check system status
echo "1️⃣ Checking system status..."
if ! curl -s --max-time 2 "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo "   ❌ Backend not running! Starting..."
    ./scripts/restart_all.sh
    sleep 5
else
    echo "   ✅ Backend running"
fi
echo ""

# Step 2: Enable camera and vision pipeline
echo "2️⃣ Enabling camera and vision pipeline..."
curl -s -X POST "$BACKEND_URL/settings" \
    -H "Content-Type: application/json" \
    -d '{
        "pose": true,
        "hands": true,
        "aruco": true,
        "overlay_from_aruco": true,
        "aruco_stride": 2
    }' > /dev/null

sleep 2

HEALTH=$(curl -s "$BACKEND_URL/health")
CAMERA_STATUS=$(echo "$HEALTH" | jq -r '.camera')
VISION_STATUS=$(echo "$HEALTH" | jq -r '.vision')

echo "   Camera: $CAMERA_STATUS"
echo "   Vision: $VISION_STATUS"

if [ "$CAMERA_STATUS" = "on" ]; then
    echo "   ✅ Camera enabled"
else
    echo "   ⚠️  Camera status: $CAMERA_STATUS"
    echo "   💡 Grant camera permissions if prompted"
fi
echo ""

# Step 3: Check available tasks
echo "3️⃣ Available tasks for demo:"
curl -s "$BACKEND_URL/tasks" | jq -r '.tasks[] | "   [\(.task_id | split("_")[0] | .[0:1])] \(.name) \(.icon) - \(.num_steps) steps"'
echo ""

# Step 4: Print ArUco marker info
echo "4️⃣ ArUco marker setup:"
if [ -d "markers" ] && [ "$(ls -1 markers/*.png 2>/dev/null | wc -l | tr -d ' ')" -gt 0 ]; then
    echo "   ✅ Markers available in markers/ directory"
    echo "   📋 Print markers for physical demo:"
    ls -1 markers/*.png | sed 's/^/      /'
    echo ""
    echo "   💡 Tip: Open markers/aruco_23_5x5_300.png and print for demo"
else
    echo "   ⚠️  No markers found, generating..."
    if [ -f "scripts/gen_aruco.py" ]; then
        python3 scripts/gen_aruco.py
        echo "   ✅ Markers generated!"
    fi
fi
echo ""

# Step 5: Check camera permissions
echo "5️⃣ Camera permissions check:"
echo "   On macOS, grant camera access to:"
echo "   • Terminal app (System Settings → Privacy & Security → Camera)"
echo "   • Or run backend with camera permissions"
echo ""

# Step 6: MagicMirror check
echo "6️⃣ MagicMirror status:"
if curl -s --max-time 2 "http://localhost:8080" > /dev/null 2>&1; then
    echo "   ✅ MagicMirror running on http://localhost:8080"
else
    echo "   ⚠️  MagicMirror not responding"
    echo "   💡 Check: tail -f /tmp/magicmirror.log"
fi
echo ""

# Step 7: Print demo instructions
echo "🎯 LIVE DEMO INSTRUCTIONS"
echo "========================="
echo ""
echo "📹 Camera Setup:"
echo "   1. Position yourself in front of the mirror/camera"
echo "   2. Ensure good lighting (face clearly visible)"
echo "   3. Optional: Hold printed ArUco marker"
echo ""
echo "🎮 Keyboard Controls:"
echo "   T     → Open task menu"
echo "   1-4   → Quick start tasks:"
echo "           1 = Brush Teeth 🪥"
echo "           2 = Wash Face 🧼"
echo "           3 = Comb Hair 💇"
echo "           4 = Draw Eyebrows 💄"
echo "   N     → Next step"
echo "   Shift+S → Stop task"
echo ""
echo "🎬 Demo Flow:"
echo "   1. Press T to show task menu"
echo "   2. Select 'Draw Eyebrows' (press 4 or click)"
echo "   3. Follow voice prompts for each step"
echo "   4. Watch HUD update with instructions"
echo "   5. Ring overlay shows on video feed"
echo "   6. Press N to advance through steps"
echo "   7. Complete all 6 steps"
echo ""
echo "💡 Visual Features to Highlight:"
echo "   • Real-time face/hand tracking overlay"
echo "   • Ring animation anchored to face position"
echo "   • HUD with step title, instruction, hint"
echo "   • Progress bar showing time remaining"
echo "   • Voice guidance for each step"
echo "   • ArUco marker detection (if marker present)"
echo ""
echo "🐛 Troubleshooting:"
echo "   No camera feed? → Grant permissions, restart backend"
echo "   No overlays?    → Check vision status: curl $BACKEND_URL/health | jq '.vision'"
echo "   No voice?       → Check system volume, TTS enabled"
echo "   Laggy?          → Close other apps, check FPS in health endpoint"
echo ""

# Step 8: Start demo mode
echo "🚀 Starting demo mode..."
echo ""
echo "   Backend:      $BACKEND_URL"
echo "   MagicMirror:  http://localhost:8080"
echo "   Logs:         tail -f /tmp/assistive-backend.log"
echo ""
echo "✅ System ready for live demo!"
echo ""
echo "Press Enter to start demo task menu..."
read

# Auto-open MagicMirror if not already visible
if command -v open &> /dev/null; then
    open "http://localhost:8080" 2>/dev/null
fi

echo "🎬 Demo started! Press T in MagicMirror to begin."
