#!/usr/bin/env bash
# Quick verification script for MagicMirror + AssistiveCoach
# Run this after making changes to verify everything works

set -e

BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8000}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Quick Health Check"
echo "===================="
echo ""

# Test 1: Backend reachable
printf "Backend (8000): "
if curl -s -f "${BACKEND_URL}/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
    echo "   Start with: cd backend && python app.py"
    exit 1
fi

# Test 2: Check if 5055 is NOT being used
printf "Port 5055 check: "
if lsof -i :5055 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Something running on 5055${NC}"
else
    echo -e "${GREEN}✓ Port 5055 clear${NC}"
fi

# Test 3: MagicMirror running
printf "MagicMirror: "
if lsof -i :8080 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running on 8080${NC}"
else
    echo -e "${YELLOW}⚠ Not detected on 8080${NC}"
fi

echo ""
echo "📊 Backend Status:"
curl -s "${BACKEND_URL}/health" | jq -r '. | "   Camera: \(.camera // "unknown")\n   Pose: \(.pose_available // false)\n   Hands: \(.hands_available // false)\n   ArUco: \(.aruco_available // false)"'

echo ""
echo "✅ Health check complete"
