#!/usr/bin/env bash
# Complete AssistiveCoach Demo Script
set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🎯 COMPLETE ASSISTIVECOACH DEMO                             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

BACKEND_URL="http://127.0.0.1:8000"

# Test 1: Check backend
echo "1️⃣ Checking backend..."
if curl -s -f "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo "   ✅ Backend running"
else
    echo "   ❌ Backend not running - start with ./scripts/restart_all.sh"
    exit 1
fi
echo ""

# Test 2: List available tasks
echo "2️⃣ Loading available tasks..."
TASKS=$(curl -s "$BACKEND_URL/tasks" | jq -r '.tasks[] | "\(.icon) \(.name) (\(.num_steps) steps)"')
echo "$TASKS"
echo ""

# Test 3: Start toothbrushing task
echo "3️⃣ Starting 'Brush Teeth' task..."
curl -s -X POST "$BACKEND_URL/tasks/brush_teeth/start" | jq '{ok, task_name, current_step, total_steps}'
echo ""
echo "   🎤 Voice: 'Step 1: Wet your toothbrush...'"
sleep 5

# Test 4: Advance steps
echo "4️⃣ Simulating task progression..."
for i in {1..5}; do
    echo "   ⏭️  Next step $i..."
    curl -s -X POST "$BACKEND_URL/tasks/next_step" | jq -c '{ok, current_step}'
    sleep 3
done
echo ""

# Test 5: Check current task
echo "5️⃣ Current task status:"
curl -s "$BACKEND_URL/tasks/current" | jq '{active, task_name, current_step, total_steps, time_left_s}'
echo ""

# Test 6: Stop task
echo "6️⃣ Stopping task..."
curl -s -X POST "$BACKEND_URL/tasks/stop" | jq '{ok, message}'
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ DEMO COMPLETE!                                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Available Keyboard Controls in MagicMirror:"
echo "   T           → Toggle task menu"
echo "   1-4         → Quick start task"
echo "   N           → Next step"
echo "   Shift+S     → Stop task"
echo ""
echo "🎯 Live Demo Ready!"
echo "   • Press 'T' in MagicMirror to show task menu"
echo "   • Select a task"
echo "   • Follow voice guidance"
echo "   • Watch HUD + overlays"
echo ""
