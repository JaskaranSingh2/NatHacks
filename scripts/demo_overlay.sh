#!/usr/bin/env bash
# Demo overlay script for testing MagicMirror overlays
set -e

BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8000}"

post() {
    curl -s -X POST "${BACKEND_URL}/overlay" \
        -H 'Content-Type: application/json' \
        -d "$1" >/dev/null
    echo "✓ Sent overlay update"
}

echo "🎭 AssistiveCoach Demo Overlay Sequence"
echo "========================================"
echo ""

# Step 1: Show HUD only
echo "📋 Step 1: HUD with task info..."
post '{
  "type": "overlay.set",
  "hud": {
    "title": "Face Wash",
    "subtitle": "Rinse & lather",
    "step": "Step 1 of 3",
    "time_left_s": 15,
    "max_time_s": 30,
    "hint": "Avoid eyes, gentle circular motion"
  }
}'
sleep 3

# Step 2: Add ring overlay
echo "💍 Step 2: Adding ring overlay..."
post '{
  "type": "overlay.set",
  "shapes": [
    {
      "kind": "ring",
      "anchor": {"pixel": {"x": 640, "y": 360}},
      "radius_px": 150,
      "accent": "info"
    }
  ],
  "hud": {
    "title": "Brush Teeth",
    "subtitle": "Small circles",
    "step": "Step 2 of 5",
    "time_left_s": 10,
    "max_time_s": 20,
    "hint": "Gentle pressure on gums"
  }
}'
sleep 3

# Step 3: Different position and size
echo "🎯 Step 3: Repositioned ring..."
post '{
  "type": "overlay.set",
  "shapes": [
    {
      "kind": "ring",
      "anchor": {"pixel": {"x": 320, "y": 240}},
      "radius_px": 200,
      "accent": "success"
    }
  ],
  "hud": {
    "title": "Hair Brush",
    "subtitle": "Even strokes",
    "step": "Step 3 of 4",
    "time_left_s": 8,
    "max_time_s": 15,
    "hint": "Start from roots to tips"
  }
}'
sleep 3

# Step 4: Clear overlay
echo "🧹 Step 4: Clearing overlay..."
post '{"type": "overlay.clear"}'
sleep 1

echo ""
echo "✅ Demo sequence complete!"
echo ""
echo "Test endpoints:"
echo "  Health: curl -s ${BACKEND_URL}/health | jq ."
echo "  Settings: curl -s ${BACKEND_URL}/settings | jq ."
