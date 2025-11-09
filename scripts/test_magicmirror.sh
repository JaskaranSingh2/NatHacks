#!/usr/bin/env bash
# Test script for MagicMirror + AssistiveCoach integration
set -e

BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8000}"

echo "🔍 MagicMirror + AssistiveCoach Test Suite"
echo "==========================================="
echo ""

# Test 1: Backend health
echo "1️⃣ Testing backend health endpoint..."
if curl -s -f "${BACKEND_URL}/health" > /dev/null 2>&1; then
    echo "   ✅ Backend is running on port 8000"
    curl -s "${BACKEND_URL}/health" | jq -c '{camera, pose_available, hands_available, aruco_available}'
else
    echo "   ❌ Backend not responding on port 8000"
    echo "   💡 Start backend with: cd backend && python app.py"
    exit 1
fi
echo ""

# Test 2: Settings endpoint
echo "2️⃣ Testing settings configuration..."
SETTINGS=$(curl -s "${BACKEND_URL}/settings")
echo "   Current settings:"
echo "   $(echo $SETTINGS | jq -c '{pose, hands, aruco, detect_scale, aruco_stride}')"
echo ""

# Test 3: Optimize settings for demo
echo "3️⃣ Applying optimal demo settings..."
curl -s -X POST "${BACKEND_URL}/settings" \
    -H 'Content-Type: application/json' \
    -d '{
        "aruco": true,
        "pose": true,
        "hands": false,
        "aruco_stride": 2,
        "detect_scale": 0.70,
        "reduce_motion": true,
        "overlay_from_aruco": true
    }' | jq -c '{aruco, pose, hands, detect_scale}'
echo "   ✅ Settings updated for optimal performance"
echo ""

# Test 4: Test overlay endpoint
echo "4️⃣ Testing overlay.set with ring + HUD..."
curl -s -X POST "${BACKEND_URL}/overlay" \
    -H 'Content-Type: application/json' \
    -d '{
        "type": "overlay.set",
        "shapes": [
            {
                "kind": "ring",
                "anchor": {"pixel": {"x": 640, "y": 360}},
                "radius_px": 120
            }
        ],
        "hud": {
            "title": "Test Task",
            "step": "Step 1 of 1",
            "subtitle": "Checking overlay",
            "time_left_s": 5,
            "max_time_s": 10,
            "hint": "You should see a ring and this HUD"
        }
    }'
echo "   ✅ Overlay sent (check MagicMirror display)"
sleep 2
echo ""

# Test 5: Clear overlay
echo "5️⃣ Clearing overlay..."
curl -s -X POST "${BACKEND_URL}/overlay" \
    -H 'Content-Type: application/json' \
    -d '{"type": "overlay.clear"}'
echo "   ✅ Overlay cleared"
echo ""

echo "✅ All tests passed!"
echo ""
echo "📝 Troubleshooting:"
echo "   • No HUD visible? Check CSS z-index in styles.css"
echo "   • 5055 errors? Update config with apiBase: 'http://127.0.0.1:8000'"
echo "   • WS not connecting? Check ALLOW_WS_ORIGINS includes 'http://localhost:8080'"
echo ""
echo "🎬 Run demo: ./scripts/demo_overlay.sh"
