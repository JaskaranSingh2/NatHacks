# MagicMirror Integration - Complete File List

## 🔧 Modified Files

### 1. Module Backend Helper

**File**: `mirror/modules/MMM-AssistiveCoach/node_helper.js`

- Added `apiBase` property (default: `http://127.0.0.1:8000`)
- Fixed health polling to use `${this.apiBase}/health`
- Accept `apiBase` from frontend config

### 2. Module Frontend

**File**: `mirror/modules/MMM-AssistiveCoach/MMM-AssistiveCoach.js`

- Added `apiBase` to module defaults
- Pass `apiBase` to node_helper on init

### 3. Module Styles

**File**: `mirror/modules/MMM-AssistiveCoach/styles.css`

- Fixed z-index layering for overlay (9999), HUD (10000), chips (10001)
- Changed positioning to `fixed` for proper layering
- Added backdrop-filter for better HUD visibility
- Removed margin from HUD card

---

## 📄 New Files Created

### Documentation

1. **MAGICMIRROR_SETUP.md**

   - Complete setup guide
   - Installation instructions
   - Configuration examples
   - Troubleshooting table
   - Performance tuning guide

2. **MAGICMIRROR_FIXES.md** (this file)

   - Summary of all changes
   - Before/after comparison
   - Testing commands
   - Success checklist

3. **config/magicmirror-example.js**
   - Reference configuration
   - All options documented
   - Full config.js structure

### Test Scripts

4. **scripts/test_magicmirror.sh**

   - Automated test suite
   - Health check
   - Settings optimization
   - Overlay testing
   - Troubleshooting tips

5. **scripts/demo_overlay.sh**

   - Demo sequence script
   - Multiple overlay states
   - HUD + ring combinations
   - Clear overlay test

6. **scripts/quick_check.sh**
   - Fast health verification
   - Port check (5055 vs 8000)
   - Backend status display

---

## 📁 File Structure

```
NatHacks/
├── MAGICMIRROR_SETUP.md          ← NEW: Complete setup guide
├── MAGICMIRROR_FIXES.md          ← NEW: This file
├── config/
│   └── magicmirror-example.js    ← NEW: Config reference
├── scripts/
│   ├── test_magicmirror.sh       ← NEW: Test suite
│   ├── demo_overlay.sh           ← NEW: Demo sequence
│   └── quick_check.sh            ← NEW: Quick health check
└── mirror/
    └── modules/
        └── MMM-AssistiveCoach/
            ├── node_helper.js    ← MODIFIED: Fixed health polling
            ├── MMM-AssistiveCoach.js ← MODIFIED: Added apiBase config
            ├── styles.css        ← MODIFIED: Fixed z-index
            └── package.json      ← Existing (ws dep)
```

---

## 🎯 What Each File Does

### Modified Module Files

| File                    | Purpose                        | Key Changes                                     |
| ----------------------- | ------------------------------ | ----------------------------------------------- |
| `node_helper.js`        | Backend helper for WS & health | Added configurable `apiBase`, fixed polling URL |
| `MMM-AssistiveCoach.js` | Frontend module                | Pass `apiBase` to helper                        |
| `styles.css`            | Visual styling & layout        | Fixed z-index, positioning for overlays         |

### New Documentation

| File                            | Purpose                    | Audience                        |
| ------------------------------- | -------------------------- | ------------------------------- |
| `MAGICMIRROR_SETUP.md`          | Installation & setup guide | Users setting up for first time |
| `MAGICMIRROR_FIXES.md`          | Technical change summary   | Developers/maintainers          |
| `config/magicmirror-example.js` | Config reference           | Anyone configuring module       |

### New Scripts

| File                  | Purpose                  | When to Use                |
| --------------------- | ------------------------ | -------------------------- |
| `test_magicmirror.sh` | Comprehensive test suite | After changes, before demo |
| `demo_overlay.sh`     | Visual demo sequence     | Showcase functionality     |
| `quick_check.sh`      | Fast health check        | Quick verification         |

---

## 🚀 Quick Start Command Reference

### First Time Setup

```bash
# 1. Install dependencies
cd ~/MagicMirror
npm --prefix modules/MMM-AssistiveCoach install

# 2. Set environment
export ALLOW_WS_ORIGINS="http://localhost:8080,file://"

# 3. Start backend
cd ~/Documents/Engineering/Coding/NatHacks/backend
python app.py &

# 4. Start MagicMirror
cd ~/MagicMirror
npm start
```

### Testing

```bash
cd ~/Documents/Engineering/Coding/NatHacks

# Quick check
./scripts/quick_check.sh

# Full test
./scripts/test_magicmirror.sh

# Demo
./scripts/demo_overlay.sh
```

### Manual Testing

```bash
# Health
curl -s http://127.0.0.1:8000/health | jq .

# Test overlay
curl -X POST http://127.0.0.1:8000/overlay \
  -H 'Content-Type: application/json' \
  -d '{"type":"overlay.set","shapes":[{"kind":"ring","anchor":{"pixel":{"x":640,"y":360}},"radius_px":120}],"hud":{"title":"Test","step":"1/1"}}'

# Clear
curl -X POST http://127.0.0.1:8000/overlay \
  -H 'Content-Type: application/json' \
  -d '{"type":"overlay.clear"}'
```

---

## ✅ Verification Checklist

Run through this list to verify everything works:

### Backend

- [ ] Backend running on port 8000
- [ ] `/health` endpoint responds
- [ ] `/settings` endpoint responds
- [ ] `/overlay` endpoint accepts POST

### Module

- [ ] No `ECONNREFUSED :5055` errors in logs
- [ ] Module loads in MagicMirror
- [ ] WebSocket connects successfully
- [ ] Health status updates control chips

### Visual

- [ ] HUD card visible in top-left
- [ ] Control chips visible in top-right
- [ ] Ring overlay renders at correct position
- [ ] Progress bar animates
- [ ] Text readable over other modules

### Testing

- [ ] `quick_check.sh` passes
- [ ] `test_magicmirror.sh` passes all tests
- [ ] `demo_overlay.sh` shows all states
- [ ] Keyboard shortcuts work (1/2/3)

---

## 🔍 Debugging Commands

### Check Process Status

```bash
# Backend
lsof -i :8000

# MagicMirror
lsof -i :8080

# Wrong port (should be empty)
lsof -i :5055
```

### View Logs

```bash
# Backend logs (if running in background)
tail -f nohup.out

# MagicMirror console
# Open DevTools in Electron window (F12 or Cmd+Option+I)
```

### Test Endpoints Individually

```bash
# Health with pretty output
curl -s http://127.0.0.1:8000/health | jq .

# Settings
curl -s http://127.0.0.1:8000/settings | jq .

# Test WS (using websocat if installed)
websocat ws://127.0.0.1:8000/ws
```

---

## 📊 Expected Results

### Health Endpoint

```json
{
	"status": "ok",
	"camera": "on",
	"lighting": "ok",
	"pose_available": true,
	"hands_available": true,
	"aruco_available": true,
	"intrinsics_loaded": true,
	"fps": 15.2,
	"latency_ms": 245
}
```

### Settings Endpoint

```json
{
	"aruco": true,
	"pose": true,
	"hands": false,
	"detect_scale": 0.7,
	"aruco_stride": 2,
	"reduce_motion": true,
	"overlay_from_aruco": true
}
```

### Visual Overlay

- **HUD**: Positioned at `top: 24px, left: 24px`
- **Ring**: Blue circle, pulsing, at specified coordinates
- **Chips**: Top-right corner, showing device status

---

## 🎓 Key Implementation Details

### Z-Index Hierarchy

```
Chips:    10001  (highest - must be clickable)
HUD:      10000  (above everything except chips)
Overlay:   9999  (above MM modules)
MM modules: varies (typically < 100)
```

### Position Strategy

- `fixed` positioning for overlays (not `absolute`)
- Pixel coordinates for precise placement
- `pointer-events: none` for overlay (except chips)

### API Configuration

- Default: `http://127.0.0.1:8000`
- Configurable via module config
- Separate from WebSocket URL

### Health Polling

- Interval: 2000ms (2 seconds)
- Uses HTTP GET to `/health`
- Updates device status in real-time

---

## 🔄 Update Process

If you need to make changes:

1. **Module code**: Edit in `mirror/modules/MMM-AssistiveCoach/`
2. **Restart MM**: Required for JS changes
3. **Reload CSS**: Cmd+R in Electron window (for CSS only)
4. **Test**: Run `./scripts/test_magicmirror.sh`
5. **Verify**: Check browser console for errors

---

## 📞 Support Resources

- **Setup Guide**: `MAGICMIRROR_SETUP.md`
- **Test Scripts**: `scripts/test_magicmirror.sh`, `scripts/demo_overlay.sh`
- **Quick Check**: `scripts/quick_check.sh`
- **Config Example**: `config/magicmirror-example.js`
- **This File**: Complete change summary and reference

---

**Status**: ✅ All files created and ready for use
**Next**: Run `./scripts/test_magicmirror.sh` to verify setup
