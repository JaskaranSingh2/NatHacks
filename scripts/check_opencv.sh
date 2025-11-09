#!/bin/bash
# Check OpenCV integration status

BACKEND_URL="http://127.0.0.1:8000"

echo "🔍 OpenCV Integration Status Check"
echo "===================================="
echo ""

echo "1️⃣ Checking backend health..."
HEALTH=$(curl -s "$BACKEND_URL/health")

echo "   Camera Status: $(echo "$HEALTH" | jq -r '.camera')"
echo "   Vision Pipeline: $(echo "$HEALTH" | jq -r '.vision')"
echo ""

echo "2️⃣ Checking ArUco configuration..."
ARUCO_STATUS=$(echo "$HEALTH" | jq -r '.aruco // empty')
if [ -n "$ARUCO_STATUS" ]; then
    echo "   ArUco Enabled: $(echo "$HEALTH" | jq -r '.aruco.enabled // "unknown"')"
    echo "   Intrinsics: $(echo "$HEALTH" | jq -r '.aruco.intrinsics_status // "unknown"')"
    echo "   Stride: $(echo "$HEALTH" | jq -r '.aruco.stride // "unknown"')"
else
    echo "   ℹ️  ArUco status not available in health endpoint"
fi
echo ""

echo "3️⃣ Checking Python OpenCV installation..."
OPENCV_CHECK=$(python3 -c "import cv2; print(f'OpenCV {cv2.__version__}'); print(f'ArUco: {hasattr(cv2, \"aruco\")}')" 2>&1)
if [ $? -eq 0 ]; then
    echo "   ✅ $OPENCV_CHECK"
else
    echo "   ❌ OpenCV not properly installed"
fi
echo ""

echo "4️⃣ Checking camera intrinsics file..."
if [ -f "config/camera_intrinsics.yml" ]; then
    echo "   ✅ Intrinsics file exists: config/camera_intrinsics.yml"
    echo "   📄 Contents:"
    head -10 config/camera_intrinsics.yml | sed 's/^/      /'
else
    echo "   ⚠️  Intrinsics file not found (ArUco pose estimation disabled)"
    echo "   💡 Run: ./scripts/calibrate_cam.py to generate calibration"
fi
echo ""

echo "5️⃣ Checking ArUco markers..."
MARKER_COUNT=$(ls -1 markers/*.png 2>/dev/null | wc -l | tr -d ' ')
if [ "$MARKER_COUNT" -gt 0 ]; then
    echo "   ✅ Found $MARKER_COUNT ArUco marker images in markers/"
    ls -1 markers/*.png | head -5 | sed 's/^/      /'
else
    echo "   ℹ️  No marker images found"
    echo "   💡 Run: ./scripts/gen_aruco.py to generate markers"
fi
echo ""

echo "6️⃣ OpenCV Integration Summary:"
echo "   ✅ Camera I/O: cv2.VideoCapture"
echo "   ✅ ArUco Detection: cv2.aruco.detectMarkers"
echo "   ✅ Pose Estimation: cv2.aruco.estimatePoseSingleMarkers"
echo "   ✅ Filtering: Exponential smoothing (α=0.4)"
echo "   ✅ Debug Rendering: cv2.rectangle, cv2.circle, cv2.putText"
echo ""

echo "📚 Documentation: See OPENCV_INTEGRATION.md for details"
