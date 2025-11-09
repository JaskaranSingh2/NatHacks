#!/usr/bin/env bash
# Quick restart script for both backend and MagicMirror
set -e

BACKEND_DIR="${HOME}/Documents/Engineering/Coding/NatHacks/backend"
MM_DIR="${HOME}/MagicMirror"

echo "🔄 Restarting AssistiveCoach + MagicMirror"
echo "=========================================="
echo ""

# Kill existing processes
echo "1️⃣ Stopping existing processes..."
pkill -9 -f "python3 app.py" || true
pkill -9 -f "npm.*MagicMirror" || true
pkill -9 -f "electron.*MagicMirror" || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2

# Set environment
export ALLOW_WS_ORIGINS="http://localhost:8080,file://"

# Start backend
echo ""
echo "2️⃣ Starting backend (port 8000)..."
cd "$BACKEND_DIR"
export PYTHONPATH="${BACKEND_DIR}/..:${PYTHONPATH}"
python3 app.py > /tmp/assistive-backend.log 2>&1 &
BACKEND_PID=$!
sleep 3

# Check if backend started
if ps -p $BACKEND_PID > /dev/null; then
    echo "   ✅ Backend running (PID: $BACKEND_PID)"
else
    echo "   ❌ Backend failed to start"
    echo "   Check logs: tail -f /tmp/assistive-backend.log"
    exit 1
fi

# Start MagicMirror
echo ""
echo "3️⃣ Starting MagicMirror..."
cd "$MM_DIR"
npm start > /tmp/magicmirror.log 2>&1 &
MM_PID=$!

echo "   ✅ MagicMirror starting (PID: $MM_PID)"
echo ""
echo "📊 Status:"
echo "   Backend:      http://127.0.0.1:8000/health"
echo "   MagicMirror:  http://localhost:8080"
echo ""
echo "📝 Logs:"
echo "   Backend:      tail -f /tmp/assistive-backend.log"
echo "   MagicMirror:  tail -f /tmp/magicmirror.log"
echo ""
echo "🛑 To stop:"
echo "   pkill -f 'python3 app.py'"
echo "   pkill -f 'npm.*MagicMirror'"
