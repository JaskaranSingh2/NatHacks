#!/bin/bash
# Test script for Vision Pipeline landmarks fast-path
# Tests both standalone and integrated modes

set -e

echo "==================================="
echo "Vision Pipeline Test Suite"
echo "==================================="
echo ""

# Determine Python interpreter (prefer python3)
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN=python
else
    echo "No python interpreter found (python or python3)." >&2
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Standalone Mode
echo -e "${YELLOW}Test 1: Standalone Vision Pipeline${NC}"
echo "Testing vision_pipeline.py in standalone mode (10 seconds)"
echo "This will test camera capture, MediaPipe processing, and CSV logging"
echo ""

cd backend
echo "Using interpreter: $PYTHON_BIN"
timeout 10 $PYTHON_BIN vision_pipeline.py || true
cd ..

if [ -f "logs/latency.csv" ]; then
    echo -e "${GREEN}✓ latency.csv created${NC}"
    echo "First 5 rows:"
    head -n 6 logs/latency.csv
    echo ""
    
    # Check average latency
    AVG_LATENCY=$(tail -n +2 logs/latency.csv | awk -F',' '{sum+=$4; count++} END {print sum/count}')
    echo "Average latency: ${AVG_LATENCY}ms"
    
    if (( $(echo "$AVG_LATENCY < 150" | bc -l) )); then
        echo -e "${GREEN}✓ Latency target met (<150ms)${NC}"
    else
        echo -e "${RED}✗ Latency exceeds target (${AVG_LATENCY}ms > 150ms)${NC}"
    fi

    CLOUD_LATENCY=$(tail -n +2 logs/latency.csv | awk -F',' '{if($7>0){sum+=$7; count++}} END {if(count>0) printf "%.2f", sum/count; else print "0"}')
    CLOUD_OK=$(tail -n +2 logs/latency.csv | awk -F',' '{ok+=$9} END {print ok}')
    CLOUD_BREAKER=$(tail -n +2 logs/latency.csv | awk -F',' '{open+=$10} END {print open}')
    echo "Cloud assist frames (ok): ${CLOUD_OK}"
    echo "Cloud average latency: ${CLOUD_LATENCY}ms"
    echo "Cloud breaker trips: ${CLOUD_BREAKER}"
else
    echo -e "${RED}✗ latency.csv not found${NC}"
fi

echo ""
echo "-----------------------------------"
echo ""

# Test 2: Check file structure
echo -e "${YELLOW}Test 2: File Structure Check${NC}"
FILES=(
    "backend/vision_pipeline.py"
    "backend/app.py"
    "backend/camera_capture.py"
    "config/features.json"
    "config/tasks.json"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file exists${NC}"
    else
        echo -e "${RED}✗ $file missing${NC}"
    fi
done

echo ""
echo "-----------------------------------"
echo ""

# Test 3: Integrated Backend Mode
echo -e "${YELLOW}Test 3: Integrated Backend Test${NC}"
echo "Starting FastAPI backend with vision pipeline..."
echo ""

# Start backend in background
cd backend
$PYTHON_BIN -m uvicorn app:app --host 0.0.0.0 --port 5055 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Test health endpoint
echo "Testing /health endpoint:"
curl -s http://localhost:5055/health | python -m json.tool || echo "Failed to reach /health"
echo ""

# Test session start
echo "Starting brush_teeth routine:"
curl -s -X POST http://localhost:5055/session/start \
    -H "Content-Type: application/json" \
    -d '{"routine_id":"brush_teeth","patient_id":"test_user"}' \
    | python -m json.tool || echo "Failed to start session"
echo ""

# Let it run for a bit
echo "Running vision pipeline for 10 seconds..."
sleep 10

# Test session advance
echo "Advancing to next step:"
curl -s -X POST http://localhost:5055/session/next_step | python -m json.tool
echo ""

# Check health again
echo "Final health check:"
curl -s http://localhost:5055/health | python -m json.tool
echo ""

# Stop backend
echo "Stopping backend..."
kill $BACKEND_PID
wait $BACKEND_PID 2>/dev/null || true

echo ""
echo "-----------------------------------"
echo ""

# Test 4: Verify CSV Growth
echo -e "${YELLOW}Test 4: CSV Log Analysis${NC}"
if [ -f "logs/latency.csv" ]; then
    LINES=$(wc -l < logs/latency.csv)
    echo "Total log entries: $((LINES - 1))"
    
    if [ $LINES -gt 10 ]; then
        echo -e "${GREEN}✓ CSV logging working (${LINES} rows)${NC}"
        
        # Show statistics
        echo ""
        echo "Latency Statistics (last 20 frames):"
        tail -n 20 logs/latency.csv | awk -F',' '
            NR>1 {
                latency=$4; 
                fps=$5; 
                sum+=latency; 
                fps_sum+=fps;
                if(latency>max) max=latency; 
                if(min=="" || latency<min) min=latency;
                count++
            } 
            END {
                printf "  Min: %.1fms\n  Avg: %.1fms\n  Max: %.1fms\n  Avg FPS: %.1f\n", 
                    min, sum/count, max, fps_sum/count
            }'
    else
        echo -e "${YELLOW}⚠ Few log entries (${LINES} rows)${NC}"
    fi
else
    echo -e "${RED}✗ No CSV log found${NC}"
fi

echo ""
echo "==================================="
echo "Test Suite Complete"
echo "==================================="
echo ""

# Acceptance Criteria
echo "Acceptance Criteria:"
echo "  [ ] Ring tracks mouth_center smoothly with jitter < 5px"
echo "  [ ] Average capture→overlay ≤ 150ms on Pi 4/5"
echo "  [ ] No deadlocks; clean shutdown works"
echo "  [ ] latency.csv grows during run"
echo "  [ ] /health returns vision_state with fps/latency_ms"
echo "  [ ] Session start immediately shows Step 1 HUD"
echo "  [ ] Cloud metrics present in /health and latency.csv"
echo ""
echo "Next Steps:"
echo "  1. Review logs/latency.csv for performance metrics"
echo "  2. Test with MagicMirror² frontend (./test_animations.sh)"
echo "  3. Verify smooth ring tracking with real camera"
echo "  4. Test on actual Raspberry Pi hardware"
echo ""
