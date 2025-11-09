#!/bin/bash
# Test the new Draw Eyebrows task end-to-end

BACKEND_URL="http://127.0.0.1:8000"

echo "💄 Testing Draw Eyebrows Task"
echo "=============================="
echo ""

echo "1️⃣ Checking if task exists..."
TASK=$(curl -s "$BACKEND_URL/tasks" | jq '.tasks[] | select(.task_id=="draw_eyebrows")')
if [ -z "$TASK" ]; then
    echo "   ❌ Task not found!"
    exit 1
fi

echo "   ✅ Task found:"
echo "$TASK" | jq '{name, icon, category, duration: .duration_s, steps: .num_steps}'
echo ""

echo "2️⃣ Starting task..."
RESULT=$(curl -s -X POST "$BACKEND_URL/tasks/draw_eyebrows/start")
echo "   ✅ Started: $(echo "$RESULT" | jq -r '.task_id')"
echo "   📝 Step 1: $(echo "$RESULT" | jq -r '.current_step.title')"
echo "   💬 Instruction: $(echo "$RESULT" | jq -r '.current_step.instruction')"
echo "   🔊 Voice: $(echo "$RESULT" | jq -r '.current_step.voice_prompt')"
echo ""

echo "3️⃣ Advancing through all steps..."
for i in {2..6}; do
    sleep 1
    RESULT=$(curl -s -X POST "$BACKEND_URL/tasks/next_step")
    
    if echo "$RESULT" | jq -e '.task_complete' > /dev/null 2>&1; then
        echo "   🎉 Task completed!"
        break
    fi
    
    echo "   ✅ Step $i: $(echo "$RESULT" | jq -r '.current_step.title')"
    echo "      💬 $(echo "$RESULT" | jq -r '.current_step.instruction')"
done
echo ""

echo "4️⃣ Checking task status..."
STATUS=$(curl -s "$BACKEND_URL/tasks/current")
if echo "$STATUS" | jq -e '.error' > /dev/null 2>&1; then
    echo "   ✅ No active task (completed successfully)"
else
    echo "   ⚠️  Task still active, stopping..."
    curl -s -X POST "$BACKEND_URL/tasks/stop" > /dev/null
fi
echo ""

echo "✅ Draw Eyebrows task test complete!"
echo ""
echo "📋 Task Details:"
echo "   • ID: draw_eyebrows"
echo "   • Name: Draw Eyebrows"
echo "   • Icon: 💄"
echo "   • Category: grooming"
echo "   • Steps: 6"
echo "   • Duration: ~2 minutes"
echo "   • Keyboard: Press 4 to start"
