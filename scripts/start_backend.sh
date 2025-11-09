#!/usr/bin/env bash
# Start backend on port 8000
set -e

cd "$(dirname "$0")/.."
cd backend

echo "🚀 Starting AssistiveCoach Backend..."
echo "   Port: 8000"
echo "   Host: 0.0.0.0"
echo ""

# Set WebSocket origins if not already set
export ALLOW_WS_ORIGINS="${ALLOW_WS_ORIGINS:-http://localhost:8080,file://}"

# Start the backend
python3 app.py
