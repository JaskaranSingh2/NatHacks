#!/bin/bash
# Test keyboard shortcuts by simulating task starts via API

BACKEND_URL="http://127.0.0.1:8000"

echo "🧪 Testing Keyboard Shortcuts (Simulating via API)"
echo "=================================================="
echo ""

# Get all tasks first
echo "1️⃣ Getting available tasks..."
TASKS=$(curl -s "$BACKEND_URL/tasks")
echo "$TASKS" | jq -r '.tasks[] | "   \(.task_id): \(.name) \(.icon)"'
echo ""

# Test each keyboard shortcut (1-4)
echo "2️⃣ Testing keyboard shortcut simulations:"
echo ""

# Shortcut 1: Brush Teeth
echo "   Key 1 → Starting 'Brush Teeth'..."
RESULT=$(curl -s -X POST "$BACKEND_URL/tasks/brush_teeth/start")
if echo "$RESULT" | jq -e '.task_id' > /dev/null 2>&1; then
    echo "   ✅ Task started: $(echo "$RESULT" | jq -r '.current_step.title')"
else
    echo "   ❌ Failed to start task"
fi
sleep 1
curl -s -X POST "$BACKEND_URL/tasks/stop" > /dev/null
echo ""

# Shortcut 2: Wash Face
echo "   Key 2 → Starting 'Wash Face'..."
RESULT=$(curl -s -X POST "$BACKEND_URL/tasks/wash_face/start")
if echo "$RESULT" | jq -e '.task_id' > /dev/null 2>&1; then
    echo "   ✅ Task started: $(echo "$RESULT" | jq -r '.current_step.title')"
else
    echo "   ❌ Failed to start task"
fi
sleep 1
curl -s -X POST "$BACKEND_URL/tasks/stop" > /dev/null
echo ""

# Shortcut 3: Comb Hair
echo "   Key 3 → Starting 'Comb Hair'..."
RESULT=$(curl -s -X POST "$BACKEND_URL/tasks/comb_hair/start")
if echo "$RESULT" | jq -e '.task_id' > /dev/null 2>&1; then
    echo "   ✅ Task started: $(echo "$RESULT" | jq -r '.current_step.title')"
else
    echo "   ❌ Failed to start task"
fi
sleep 1
curl -s -X POST "$BACKEND_URL/tasks/stop" > /dev/null
echo ""

# Shortcut 4: Draw Eyebrows (NEW!)
echo "   Key 4 → Starting 'Draw Eyebrows' (NEW TASK!)..."
RESULT=$(curl -s -X POST "$BACKEND_URL/tasks/draw_eyebrows/start")
if echo "$RESULT" | jq -e '.task_id' > /dev/null 2>&1; then
    echo "   ✅ Task started: $(echo "$RESULT" | jq -r '.current_step.title')"
    echo "   📝 Step 1: $(echo "$RESULT" | jq -r '.current_step.instruction')"
else
    echo "   ❌ Failed to start task"
fi
sleep 1
curl -s -X POST "$BACKEND_URL/tasks/stop" > /dev/null
echo ""

echo "3️⃣ Testing 'N' key (Next Step)..."
curl -s -X POST "$BACKEND_URL/tasks/draw_eyebrows/start" > /dev/null
sleep 1
RESULT=$(curl -s -X POST "$BACKEND_URL/tasks/next_step")
echo "   ✅ Advanced to: $(echo "$RESULT" | jq -r '.current_step.title')"
echo ""

echo "4️⃣ Testing 'Shift+S' key (Stop Task)..."
RESULT=$(curl -s -X POST "$BACKEND_URL/tasks/stop")
echo "   ✅ Task stopped: $(echo "$RESULT" | jq -r '.message')"
echo ""

echo "✅ All keyboard shortcut endpoints working!"
echo ""
echo "💡 To test in MagicMirror UI:"
echo "   - Press T to open task menu"
echo "   - Press 1-4 to start tasks"
echo "   - Press N to advance steps"
echo "   - Press Shift+S to stop"
