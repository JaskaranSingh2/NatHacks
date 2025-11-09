# MagicMirror + AssistiveCoach Setup Guide

## ✅ Fixes Applied

This guide documents the fixes applied to get AssistiveCoach working properly with MagicMirror on macOS.

### Issues Fixed

1. **Health poll spam to port 5055** → Now uses configurable `apiBase` (default: `http://127.0.0.1:8000`)
2. **HUD not rendering** → Fixed CSS z-index and positioning
3. **Module dependencies** → WebSocket library (`ws`) properly configured
4. **CORS/WS origins** → Configured via `ALLOW_WS_ORIGINS` env var

---

## 🚀 Quick Start

### 1. Install Module Dependencies

```bash
cd ~/MagicMirror
npm --prefix modules/MMM-AssistiveCoach install
```

This installs the `ws` package required by `node_helper.js`.

### 2. Update MagicMirror Config

Edit `~/MagicMirror/config/config.js` to include:

```javascript
{
  module: "MMM-AssistiveCoach",
  position: "bottom_left",
  config: {
    wsUrl: "ws://127.0.0.1:8000/ws",
    apiBase: "http://127.0.0.1:8000",  // Important: points to FastAPI backend
    reduceMotion: true,
    showHints: true,
    showControls: true
  }
}
```

### 3. Set Backend Environment Variables

```bash
export ALLOW_WS_ORIGINS="http://localhost:8080,file://"
```

Add this to your shell profile (`~/.zshrc`) to persist across sessions.

### 4. Start Backend

```bash
cd ~/Documents/Engineering/Coding/NatHacks/backend
python app.py
```

The backend should start on `http://127.0.0.1:8000`.

### 5. Start MagicMirror

```bash
cd ~/MagicMirror
npm start
```

Or in development mode:

```bash
npm run start:dev
```

---

## 🧪 Testing

### Test Backend Health

```bash
curl -s http://127.0.0.1:8000/health | jq .
```

Expected output includes:

```json
{
	"camera": "on",
	"pose_available": true,
	"hands_available": true,
	"aruco_available": true
}
```

### Test Overlay Rendering

Run the test script:

```bash
cd ~/Documents/Engineering/Coding/NatHacks
./scripts/test_magicmirror.sh
```

This will:

- Check backend health
- Configure optimal settings
- Send a test overlay with ring + HUD
- Verify the overlay clears properly

### Demo Sequence

Run a full demo sequence:

```bash
./scripts/demo_overlay.sh
```

This cycles through multiple overlay states to showcase functionality.

---

## 🎨 What Should You See?

### HUD Card (Top Left)

- **Title**: Large bold text (e.g., "Brush Teeth")
- **Step**: Blue text showing progress (e.g., "Step 2 of 5")
- **Subtitle**: Additional context
- **Progress bar**: Animated progress indicator
- **Hint**: Yellow hint text at bottom

### Ring Overlay (Center)

- **Blue ring** with pulsing animation
- Position controlled by `anchor.pixel` coordinates
- Radius controlled by `radius_px`

### Control Chips (Top Right)

- Camera status indicator
- Lighting status indicator
- Microphone status indicator

---

## 🐛 Troubleshooting

| Symptom                   | Cause                          | Solution                                              |
| ------------------------- | ------------------------------ | ----------------------------------------------------- |
| `ECONNREFUSED ::1:5055`   | Module polling wrong port      | Verify `apiBase: "http://127.0.0.1:8000"` in config   |
| Blue ring but no HUD      | CSS z-index or missing handler | Applied in this fix (z-index: 10000)                  |
| `Cannot find module 'ws'` | Missing dependency             | Run `npm --prefix modules/MMM-AssistiveCoach install` |
| WS connection fails       | CORS/origin issue              | Set `ALLOW_WS_ORIGINS` environment variable           |
| High latency (>500ms)     | Heavy vision processing        | Disable `hands` or lower `detect_scale` to 0.6        |
| Health timeout            | Backend not running            | Start backend with `python backend/app.py`            |

---

## ⚙️ Performance Tuning

For optimal performance on macOS (M-series):

```bash
curl -s -X POST http://127.0.0.1:8000/settings \
  -H 'Content-Type: application/json' \
  -d '{
    "aruco": true,
    "pose": true,
    "hands": false,
    "aruco_stride": 2,
    "detect_scale": 0.70,
    "reduce_motion": true,
    "overlay_from_aruco": true
  }' | jq .
```

**Key settings:**

- `hands: false` - Disable hand tracking if not needed (saves ~100ms)
- `aruco_stride: 2` - Process ArUco detection every 2 frames
- `detect_scale: 0.70` - Scale down images before processing
- `reduce_motion: true` - Disable animations for accessibility

---

## 📝 Configuration Options

### Module Config (`config.js`)

```javascript
{
  wsUrl: "ws://127.0.0.1:8000/ws",        // WebSocket endpoint
  apiBase: "http://127.0.0.1:8000",       // REST API base
  theme: "high-contrast",                 // UI theme
  fontScale: 1.0,                         // Font size multiplier
  reduceMotion: false,                    // Disable animations
  showHints: true,                        // Show hint text
  showControls: true                      // Show control chips
}
```

### Backend Settings

Configure via REST API:

```bash
curl -X POST http://127.0.0.1:8000/settings \
  -H 'Content-Type: application/json' \
  -d '{
    "aruco": true,
    "pose": true,
    "hands": true,
    "detect_scale": 0.70,
    "aruco_stride": 2
  }'
```

---

## 🎯 Manual Testing Commands

### Send Custom Overlay

```bash
curl -s -X POST http://127.0.0.1:8000/overlay \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "overlay.set",
    "shapes": [
      {
        "kind": "ring",
        "anchor": {"pixel": {"x": 640, "y": 360}},
        "radius_px": 150
      }
    ],
    "hud": {
      "title": "Custom Task",
      "step": "Step 1 of 3",
      "subtitle": "Description here",
      "time_left_s": 10,
      "max_time_s": 30,
      "hint": "Helpful hint text"
    }
  }'
```

### Clear Overlay

```bash
curl -s -X POST http://127.0.0.1:8000/overlay \
  -H 'Content-Type: application/json' \
  -d '{"type": "overlay.clear"}'
```

### Check Current Settings

```bash
curl -s http://127.0.0.1:8000/settings | jq .
```

---

## ✅ Success Checklist

- [ ] No more `ECONNREFUSED :5055` errors in logs
- [ ] HUD card visible in top-left corner over other modules
- [ ] Control chips visible and functional in top-right
- [ ] Blue ring overlay renders at correct position
- [ ] Overlay responds to `curl` test commands
- [ ] WebSocket connection stable (check MagicMirror console)
- [ ] Average latency < 300ms (check backend logs)

---

## 📚 Code Changes Summary

### 1. `node_helper.js`

- Added `apiBase` property (default: `http://127.0.0.1:8000`)
- Updated `_pollHealth()` to use `${this.apiBase}/health`
- Pass `apiBase` from frontend config to helper

### 2. `MMM-AssistiveCoach.js`

- Added `apiBase` to defaults
- Pass `apiBase` in `MMM_ASSISTIVECOACH_INIT` notification
- Existing overlay handlers already functional

### 3. `styles.css`

- Changed `#assistive-coach` to `position: fixed` with `z-index: 9999`
- Changed `#overlay` to `z-index: 9999`
- Changed `#hud` to `position: fixed` with `z-index: 10000`
- Changed `#chips` to `position: fixed` with `z-index: 10001`
- Added `backdrop-filter: blur(8px)` to HUD card

---

## 🎥 Demo Mode

Press keyboard shortcuts when MagicMirror has focus:

- **1** - Demo step 1 (small ring)
- **2** - Demo step 2 (medium ring)
- **3** - Demo step 3 (large ring)

These are built into the module for quick testing.

---

## 🔗 Related Documentation

- [ACCESSIBILITY.md](../ACCESSIBILITY.md) - Accessibility features
- [ARUCO_GUIDE.md](../ARUCO_GUIDE.md) - ArUco marker setup
- [README.md](../README.md) - Project overview
- [backend/vision_pipeline.py](../backend/vision_pipeline.py) - Vision processing

---

## 📞 Support

If issues persist:

1. Check MagicMirror console for errors (F12 in Electron)
2. Check backend terminal for latency/errors
3. Verify WebSocket connection in Network tab
4. Test backend endpoints directly with `curl`
5. Review troubleshooting table above

For performance issues, try adjusting `detect_scale` and disabling `hands` detection.
