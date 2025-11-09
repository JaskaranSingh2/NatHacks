# Contextual Overlay System

## Overview

The contextual overlay system provides step-specific visual guidance for ADL (Activities of Daily Living) tasks by highlighting relevant facial regions based on the current task step. The system uses MediaPipe FaceMesh (468 landmarks) to compute facial region coordinates and generates dynamic overlays synchronized with the task progress.

## Architecture

### Components

1. **Vision Pipeline** (`backend/vision_pipeline.py`)

   - `_compute_face_regions()`: Maps FaceMesh landmarks to 17 facial regions
   - `_task_overlay_shapes()`: Returns step-specific overlay configurations per task
   - Integrated in main processing loop when `session.routine_id` present

2. **Frontend Display** (`mirror/modules/MMM-AssistiveCoach/`)

   - Renders overlay shapes (rings, arrows, text labels) received via WebSocket
   - Accent color system for visual distinction

3. **Task System** (`backend/task_system.py`)
   - Defines 6 ADL tasks with multi-step workflows
   - Tracks current step via session state

## Facial Regions (17 total)

### Mouth Regions (5)

- `mouth_upper`: Upper lip area (landmarks 0, 11, 12, 13)
- `mouth_lower`: Lower lip area (landmarks 17, 14, 15, 16)
- `mouth_left`: Left corner (landmarks 61, 409)
- `mouth_right`: Right corner (landmarks 291, 308)
- `mouth_center`: Entire mouth (landmarks 13, 14)

### Eye Regions (2)

- `eye_left`: Left eye area (landmarks 33, 133, 159, 145)
- `eye_right`: Right eye area (landmarks 362, 263, 386, 374)

### Cheek Regions (2)

- `cheek_left`: Left cheek (landmarks 116, 123)
- `cheek_right`: Right cheek (landmarks 345, 352)

### Brow Regions (2)

- `brow_left`: Left eyebrow (landmarks 70, 63, 105, 66)
- `brow_right`: Right eyebrow (landmarks 300, 293, 334, 296)

### Forehead (1)

- `forehead_center`: Central forehead (landmarks 6, 9)

### Chin/Jaw (3)

- `chin_center`: Central chin (landmarks 136, 152)
- `jaw_left`: Left jaw line (landmarks 234, 227)
- `jaw_right`: Right jaw line (landmarks 454, 447)

### Nose (2)

- `nose_tip`: Nose tip (landmark 1)
- `nose_bridge`: Nose bridge (landmarks 197, 168)

## Task Mappings

### 1. Brush Teeth (4 steps)

| Step | Region       | Radius | Arrow      | Purpose           |
| ---- | ------------ | ------ | ---------- | ----------------- |
| 0    | mouth_center | 80     | None       | Position brush    |
| 1    | mouth_upper  | 110    | Horizontal | Brush upper teeth |
| 2    | mouth_lower  | 110    | Horizontal | Brush lower teeth |
| 3    | mouth_center | 90     | None       | Rinse             |

### 2. Wash Face (5 steps)

| Step | Region(s)                     | Radius | Arrow      | Purpose             |
| ---- | ----------------------------- | ------ | ---------- | ------------------- |
| 0    | mouth_center, forehead_center | 100    | None       | Wet face            |
| 1    | cheek_left                    | 120    | Diagonal ↘ | Massage left cheek  |
| 2    | cheek_right                   | 120    | Diagonal ↙ | Massage right cheek |
| 3    | forehead_center               | 110    | None       | Clean forehead      |
| 4    | mouth_center                  | 90     | None       | Rinse               |

### 3. Comb Hair (4 steps)

| Step | Region          | Radius | Arrow | Purpose          |
| ---- | --------------- | ------ | ----- | ---------------- |
| 0    | forehead_center | 100    | None  | Position comb    |
| 1    | forehead_center | 120    | Up ↑  | Brush from roots |
| 2    | forehead_center | 110    | None  | Middle section   |
| 3    | forehead_center | 100    | None  | Final pass       |

### 4. Draw Eyebrows (6 steps)

| Step | Region     | Radius | Arrow   | Purpose                         |
| ---- | ---------- | ------ | ------- | ------------------------------- |
| 0-2  | brow_left  | 70-90  | Right → | Left brow (start, fill, blend)  |
| 3-5  | brow_right | 70-90  | Left ←  | Right brow (start, fill, blend) |

### 5. Shave (4 steps)

| Step | Region       | Radius | Arrow  | Purpose             |
| ---- | ------------ | ------ | ------ | ------------------- |
| 0    | chin_center  | 90     | None   | Apply cream to chin |
| 1    | cheek_left   | 110    | Down ↓ | Shave left cheek    |
| 2    | cheek_right  | 110    | Down ↓ | Shave right cheek   |
| 3    | mouth_center | 80     | None   | Rinse               |

### 6. Moisturize (4 steps)

| Step | Region(s)               | Radius | Arrow | Purpose            |
| ---- | ----------------------- | ------ | ----- | ------------------ |
| 0    | cheek_left, cheek_right | 100    | None  | Apply to cheeks    |
| 1    | forehead_center         | 110    | None  | Apply to forehead  |
| 2    | chin_center             | 90     | None  | Apply to neck/chin |
| 3    | mouth_center            | 80     | None  | Final blending     |

## Arrow Guidance System

Arrow overlays provide directional cues for motion-based actions:

- **Horizontal (→/←)**: Side-to-side brushing motions (teeth, eyebrows)
- **Vertical (↑/↓)**: Up/down strokes (combing, shaving)
- **Diagonal (↘/↙)**: Circular massage motions (face washing)
- **None**: Static positioning or area-focused actions

## Implementation Details

### Region Computation

```python
def _compute_face_regions(self, landmarks_px: list) -> dict:
    """
    Maps FaceMesh landmarks to facial region pixel coordinates.
    Returns dict with region names as keys, (x, y) tuples as values.
    Handles missing landmarks gracefully.
    """
```

### Overlay Generation

```python
def _task_overlay_shapes(self, regions: dict, step: int, routine_id: str) -> list:
    """
    Returns contextual overlay shapes for current task step.
    Each shape contains: anchor_px (x,y), radius, arrow_direction, text_label.
    Appended to base overlay shapes when task active.
    """
```

### Integration Flow

1. Vision pipeline detects face → populates `_last_face_mesh`
2. Session state has active `routine_id` and `current_step`
3. `_compute_face_regions()` called with landmark coordinates
4. `_task_overlay_shapes()` queries task_mappings for step config
5. Contextual shapes appended to overlay data sent to frontend
6. Frontend renders rings + arrows + labels at specified coordinates

## Testing & Verification

### Manual Testing

```bash
# Start a task
curl -X POST http://localhost:8000/tasks/brush_teeth/start

# Monitor overlays via WebSocket
python3 backend/tests/test_contextual_overlays.py

# Advance to next step
curl -X POST http://localhost:8000/tasks/step/next

# Stop task
curl -X POST http://localhost:8000/tasks/stop
```

### Expected Results (brush_teeth example)

- **Step 0**: Single "Mouth Center" ring at ~(654, 615), radius 80px
- **Step 1**: "Mouth Upper" ring at ~(654, 570), radius 110px + horizontal arrow
- **Step 2**: "Mouth Lower" ring at ~(654, 660), radius 110px + horizontal arrow
- **Step 3**: "Mouth Center" ring at ~(654, 615), radius 90px

### Known Requirements

- **Face detection required**: Overlays only appear when MediaPipe FaceMesh detects a face
- **Camera active**: Mock/empty camera feeds won't trigger contextual overlays
- **Session state**: Task must be started via API to populate `routine_id`

## Performance

- **Latency**: <250ms typical (overlay generation + WebSocket broadcast)
- **FPS**: Maintains 100 FPS with overlay computation enabled
- **Region computation**: ~5-10ms per frame (negligible overhead)

## Future Enhancements

1. **Dynamic Radius Scaling**: Adjust overlay size based on face distance from camera
2. **Multi-Region Highlighting**: Support overlapping regions for complex steps
3. **Animation Sequences**: Animate arrows to demonstrate motion patterns
4. **Confidence Thresholds**: Only show overlays when landmark confidence high
5. **Region Tracking**: Detect if user looking at correct facial area during step
6. **Adaptive Guidance**: Increase overlay prominence if step taking longer than expected

## API Integration

### Start Task with Contextual Overlays

```bash
curl -X POST http://localhost:8000/tasks/{routine_id}/start
```

### Check Overlay Status

```bash
curl http://localhost:8000/status
# Returns session.routine_id and current_step
```

### Stop Task (Clears Overlays)

```bash
curl -X POST http://localhost:8000/tasks/stop
```

## Troubleshooting

### No Overlays Appearing

1. **Check face detection**: Ensure camera sees a face (MediaPipe FaceMesh active)
2. **Verify task started**: Check `session.routine_id` in status response
3. **Review backend logs**: `tail -f backend/logs/backend.log | grep overlay`
4. **Test with brush_teeth**: Most reliable task for initial testing

### Overlays in Wrong Location

1. **Camera calibration**: Run `scripts/calibrate_cam.py` to update intrinsics
2. **Landmark quality**: Check MediaPipe FaceMesh confidence scores
3. **Coordinate mapping**: Verify `landmarks_px` conversion from normalized coordinates

### Performance Issues

1. **High latency**: Check backend logs for MediaPipe processing time
2. **Frame drops**: Reduce overlay complexity or disable non-essential shapes
3. **WebSocket lag**: Verify network latency between backend and frontend

## Code References

- **Implementation**: `backend/vision_pipeline.py` lines 233-425
- **Task Definitions**: `backend/task_system.py`
- **Frontend Rendering**: `mirror/modules/MMM-AssistiveCoach/MMM-AssistiveCoach.js`
- **Testing**: `backend/tests/test_contextual_overlays.py`

---

**Status**: ✅ Fully implemented and deployed (verified with brush_teeth task)  
**Last Updated**: 2025-01-19  
**Contributors**: Vision pipeline team
