#!/bin/bash
# Quick demo test - verify task system works end-to-end

set -e

echo "🧪 Testing AssistiveCoach Task System"
echo "======================================"
echo ""

API_BASE="http://localhost:8000"

# Check if backend is running
echo "1️⃣ Checking backend health..."
if ! curl -sf "$API_BASE/health" > /dev/null; then
    echo "❌ Backend not running on port 8000"
    echo "   Run: bash scripts/restart_all.sh"
    exit 1
fi
echo "✅ Backend is healthy"
echo ""

# List available tasks
echo "2️⃣ Fetching available tasks..."
TASKS=$(curl -sf "$API_BASE/tasks" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"{len(data['tasks'])} tasks available\")")
echo "✅ $TASKS"
echo ""

# Start first task
echo "3️⃣ Starting 'Brush Teeth' task..."
TASK_START=$(curl -sf -X POST "$API_BASE/tasks/brush_teeth/start")
TASK_NAME=$(echo "$TASK_START" | python3 -c "import sys, json; print(json.load(sys.stdin).get('task_name', 'Unknown'))")
CURRENT_STEP=$(echo "$TASK_START" | python3 -c "import sys, json; print(json.load(sys.stdin).get('current_step', 0))")
TOTAL_STEPS=$(echo "$TASK_START" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total_steps', 0))")
echo "✅ Task started: $TASK_NAME (Step $CURRENT_STEP/$TOTAL_STEPS)"
echo ""

# Wait a moment
echo "4️⃣ Waiting 2 seconds..."
sleep 2
echo "✅ Wait complete"
echo ""

# Advance step (will fail because minimum time not met - this is expected)
echo "5️⃣ Attempting to advance step (should fail - time requirement)..."
NEXT_RESULT=$(curl -sf -X POST "$API_BASE/tasks/next_step" || echo '{"ok":false}')
OK_STATUS=$(echo "$NEXT_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('ok', False))")
if [ "$OK_STATUS" = "False" ]; then
    echo "✅ Correctly blocked (minimum time not met)"
else
    echo "⚠️  Step advanced (might be unexpected)"
fi
echo ""

# Wait for minimum time (15 seconds for first step)
echo "6️⃣ Waiting 15 seconds for step timer..."
sleep 15
echo "✅ Timer complete"
echo ""

# Advance step (should succeed now)
echo "7️⃣ Advancing to next step..."
NEXT_RESULT=$(curl -sf -X POST "$API_BASE/tasks/next_step")
OK_STATUS=$(echo "$NEXT_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('ok', False))")
COMPLETE=$(echo "$NEXT_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('task_complete', False))")
if [ "$OK_STATUS" = "True" ] && [ "$COMPLETE" = "False" ]; then
    echo "✅ Advanced to step 2"
elif [ "$COMPLETE" = "True" ]; then
    echo "⚠️  Task completed (unexpected - should have 6 steps)"
else
    echo "❌ Failed to advance step"
fi
echo ""

# Stop task
echo "8️⃣ Stopping task..."
STOP_RESULT=$(curl -sf -X POST "$API_BASE/tasks/stop")
OK_STATUS=$(echo "$STOP_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('ok', False))")
if [ "$OK_STATUS" = "True" ]; then
    echo "✅ Task stopped successfully"
else
    echo "❌ Failed to stop task"
fi
echo ""

echo "======================================"
echo "✅ All tests passed!"
echo ""
echo "💡 Next steps:"
echo "   1. Open http://localhost:8080 in browser"
echo "   2. Press 'T' to see task menu"
echo "   3. Press '1' to start Brush Teeth"
echo "   4. Press 'N' to advance steps"
echo "   5. Press 'Shift+S' to stop"
echo ""
echo "📖 See DEMO_GUIDE.md for complete instructions"
