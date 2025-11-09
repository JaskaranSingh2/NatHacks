#!/bin/bash
# Quick status check of entire system

BACKEND_URL="http://127.0.0.1:8000"
MM_URL="http://localhost:8080"

echo "🚀 AssistiveCoach System Status"
echo "================================"
echo ""

# Check backend
echo "1️⃣ Backend Status:"
if curl -s --max-time 2 "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo "   ✅ Running on port 8000"
    HEALTH=$(curl -s "$BACKEND_URL/health")
    echo "   • Camera: $(echo "$HEALTH" | jq -r '.camera')"
    echo "   • Vision: $(echo "$HEALTH" | jq -r '.vision')"
    echo "   • FPS: $(echo "$HEALTH" | jq -r '.fps // "N/A"')"
else
    echo "   ❌ Backend not responding"
fi
echo ""

# Check MagicMirror
echo "2️⃣ MagicMirror Status:"
if curl -s --max-time 2 "$MM_URL" > /dev/null 2>&1; then
    echo "   ✅ Running on port 8080"
    echo "   🌐 Open: $MM_URL"
else
    echo "   ❌ MagicMirror not responding"
fi
echo ""

# Check tasks
echo "3️⃣ Available Tasks:"
TASKS=$(curl -s "$BACKEND_URL/tasks" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "$TASKS" | jq -r '.tasks[] | "   \(.task_id): \(.name) \(.icon) (\(.num_steps) steps)"'
else
    echo "   ❌ Could not fetch tasks"
fi
echo ""

# Check active task
echo "4️⃣ Active Task:"
CURRENT=$(curl -s "$BACKEND_URL/tasks/current" 2>/dev/null)
if echo "$CURRENT" | jq -e '.task_id' > /dev/null 2>&1; then
    echo "   🎯 $(echo "$CURRENT" | jq -r '.task_id')"
    echo "   📝 Step $(echo "$CURRENT" | jq -r '.step_number')/$(echo "$CURRENT" | jq -r '.total_steps'): $(echo "$CURRENT" | jq -r '.current_step.title')"
else
    echo "   ℹ️  No active task"
fi
echo ""

# Check processes
echo "5️⃣ Process Status:"
BACKEND_PID=$(pgrep -f "python.*app.py" | head -1)
MM_PID=$(pgrep -f "npm.*MagicMirror" | head -1)
if [ -n "$BACKEND_PID" ]; then
    echo "   ✅ Backend PID: $BACKEND_PID"
else
    echo "   ❌ Backend process not found"
fi
if [ -n "$MM_PID" ]; then
    echo "   ✅ MagicMirror PID: $MM_PID"
else
    echo "   ❌ MagicMirror process not found"
fi
echo ""

# Git status
echo "6️⃣ Git Status:"
GIT_BRANCH=$(git branch --show-current 2>/dev/null)
GIT_STATUS=$(git status --short 2>/dev/null | wc -l | tr -d ' ')
if [ -n "$GIT_BRANCH" ]; then
    echo "   🌿 Branch: $GIT_BRANCH"
    if [ "$GIT_STATUS" -eq 0 ]; then
        echo "   ✅ Working tree clean"
    else
        echo "   📝 $GIT_STATUS file(s) changed"
    fi
else
    echo "   ℹ️  Not a git repository"
fi
echo ""

echo "📋 Quick Commands:"
echo "   • Restart: ./scripts/restart_all.sh"
echo "   • Test tasks: ./scripts/test_all_tasks.sh"
echo "   • Check OpenCV: ./scripts/check_opencv.sh"
echo "   • Test keyboards: ./scripts/test_keyboard_shortcuts.sh"
