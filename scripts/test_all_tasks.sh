#!/bin/bash
# Test all 4 tasks sequentially

BACKEND_URL="http://127.0.0.1:8000"

echo "🧪 Testing All 4 Tasks"
echo "====================="
echo ""

# Function to test a task
test_task() {
    TASK_ID=$1
    TASK_NAME=$2
    TASK_ICON=$3
    KEY_NUM=$4
    
    echo "[$KEY_NUM] Testing: $TASK_ICON $TASK_NAME"
    echo "   Starting task: $TASK_ID"
    
    # Start task
    RESULT=$(curl -s -X POST "$BACKEND_URL/tasks/$TASK_ID/start")
    
    if echo "$RESULT" | jq -e '.task_id' > /dev/null 2>&1; then
        STEP_COUNT=$(echo "$RESULT" | jq -r '.total_steps')
        echo "   ✅ Started successfully ($STEP_COUNT steps)"
        echo "   📝 First step: $(echo "$RESULT" | jq -r '.current_step.title')"
        
        # Advance through 2 steps
        sleep 0.5
        curl -s -X POST "$BACKEND_URL/tasks/next_step" > /dev/null
        sleep 0.5
        RESULT=$(curl -s -X POST "$BACKEND_URL/tasks/next_step")
        echo "   ⏩ Advanced to step 3: $(echo "$RESULT" | jq -r '.current_step.title')"
        
        # Stop task
        sleep 0.5
        curl -s -X POST "$BACKEND_URL/tasks/stop" > /dev/null
        echo "   ⏹️  Task stopped"
    else
        echo "   ❌ Failed to start"
        echo "$RESULT" | jq
    fi
    
    echo ""
}

# Test all tasks
test_task "brush_teeth" "Brush Teeth" "🪥" "1"
test_task "wash_face" "Wash Face" "🧼" "2"
test_task "comb_hair" "Comb Hair" "💇" "3"
test_task "draw_eyebrows" "Draw Eyebrows" "💄" "4"

echo "✅ All task tests complete!"
echo ""
echo "💡 Manual UI Test:"
echo "   1. Open MagicMirror (http://localhost:8080)"
echo "   2. Press T to open task menu"
echo "   3. Press 1, 2, 3, or 4 to start tasks"
echo "   4. Press N to advance, Shift+S to stop"
