#!/bin/bash

# Test script for MMM-AssistiveCoach animations
# Usage: ./test_animations.sh

echo "Testing MMM-AssistiveCoach Animation Kit..."
echo ""

# Test 1: Send overlay with ring and HUD
echo "1. Sending overlay with pulsing ring..."
curl -X POST http://localhost:5055/overlay \
  -H "Content-Type: application/json" \
  -d @test_animation.json

echo ""
echo ""

# Test 2: Update status (should trigger chip color changes)
echo "2. Testing device status chips..."
echo "   - Camera OK"
curl -X POST http://localhost:5055/status \
  -H "Content-Type: application/json" \
  -d '{"camera":"ok","lighting":"ok","mic":"ok"}'

sleep 2

echo ""
echo "   - Lighting Warning"
curl -X POST http://localhost:5055/status \
  -H "Content-Type: application/json" \
  -d '{"camera":"ok","lighting":"dim","mic":"ok"}'

sleep 2

echo ""
echo "   - Camera Off"
curl -X POST http://localhost:5055/status \
  -H "Content-Type: application/json" \
  -d '{"camera":"off","lighting":"ok","mic":"ok"}'

echo ""
echo ""
echo "3. Testing progress bar animation..."
curl -X POST http://localhost:5055/overlay \
  -H "Content-Type: application/json" \
  -d '{
    "type": "overlay.set",
    "shapes": [{
      "kind": "ring",
      "anchor": {"pixel": {"x": 640, "y": 360}},
      "radius_px": 120
    }],
    "hud": {
      "title": "Brush Teeth",
      "step": "Step 4 of 5",
      "subtitle": "Back molars",
      "time_left_s": 5,
      "max_time_s": 30,
      "hint": "Dont forget the gum line"
    }
  }'

echo ""
echo ""
echo "Animation tests complete!"
echo ""
echo "Expected results:"
echo "  ✓ Ring should pulse smoothly (or static if prefers-reduced-motion)"
echo "  ✓ HUD should slide in from bottom (or appear instantly if reduced motion)"
echo "  ✓ Progress bar should animate from previous value to new value"
echo "  ✓ Chips should change colors smoothly (green→amber→gray)"
echo "  ✓ No frame drops or jank"
echo "  ✓ Overlay updates within 1 frame (~16ms)"
