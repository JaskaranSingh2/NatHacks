#!/usr/bin/env bash
# Test overlay display with ring + HUD
set -e

BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8000}"

echo "🎨 Testing Overlay Display"
echo "=========================="
echo ""

# First, enable vision features
echo "1️⃣ Enabling camera/vision features..."
curl -s -X POST "${BACKEND_URL}/settings" \
  -H 'Content-Type: application/json' \
  -d '{
    "pose": true,
    "hands": false,
    "aruco": true,
    "detect_scale": 0.75,
    "aruco_stride": 2
  }' | jq -c '{pose, hands, aruco}'

echo ""
sleep 2

# Send overlay with ring and HUD
echo "2️⃣ Sending ring + HUD overlay..."
curl -s -X POST "${BACKEND_URL}/overlay" \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "overlay.set",
    "shapes": [
      {
        "kind": "ring",
        "anchor": {
          "pixel": {
            "x": 640,
            "y": 360
          }
        },
        "radius_px": 150,
        "accent": "info"
      }
    ],
    "hud": {
      "title": "Brush Teeth",
      "step": "Step 2 of 5",
      "subtitle": "Small circular motions",
      "time_left_s": 15,
      "max_time_s": 30,
      "hint": "Gentle pressure on gums"
    }
  }'

echo "   ✅ Overlay sent!"
echo ""
echo "👀 Check MagicMirror - you should see:"
echo "   • Blue pulsing ring in center"
echo "   • HUD card in top-left with task info"
echo "   • Control chips in top-right (Camera/Lighting/Mic)"
echo ""
echo "🖱️  Try clicking the Camera chip to toggle vision on/off"
echo ""
sleep 10

# Clear overlay
echo "3️⃣ Clearing overlay..."
curl -s -X POST "${BACKEND_URL}/overlay" \
  -H 'Content-Type: application/json' \
  -d '{"type": "overlay.clear"}'

echo "   ✅ Cleared!"
echo ""
echo "✅ Test complete!"
