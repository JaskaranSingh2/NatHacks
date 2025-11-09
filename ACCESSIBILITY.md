# Accessibility Features

This project incorporates a growing set of accessibility enhancements to keep the Assistive Mirror experience inclusive and comfortable.

## Goals

- High contrast, legible HUD at typical viewing distances
- Motion sensitivity support (respect reduced-motion preferences & server override)
- Clear keyboard shortcuts for local/demo testing
- Focus visibility for interactive prototypes
- Scalable typography for future font size adjustments

## Implemented

### 1. Design Tokens

Defined in `mirror/modules/MMM-AssistiveCoach/styles.css` and `tools/viewer.html`:

- Color variables: `--bg`, `--fg`, `--accent`, semantic status (`--ok`, `--warn`, `--err`)
- Typography clamp: `--title-size` ensures large readable headings
- Easing variables allow animation tuning without hunting hard-coded curves

### 2. Reduced Motion

Client-side: Detects `prefers-reduced-motion` and adds `.prefers-reduced-motion` class removing animations/transitions.
Server-side: New `reduce_motion` setting (FastAPI `/settings`) surfaces in `/health` and broadcasts a status message when changed so UIs can opt out of animation regardless of OS preference.

Example request:

```bash
curl -X POST http://localhost:5055/settings \
  -H 'Content-Type: application/json' \
  -d '{"reduce_motion": true}'
```

### 3. Keyboard Demo Shortcuts

`MMM-AssistiveCoach.js` & `tools/viewer.html` bind keys `1`, `2`, `3` to local demo overlays (`_demoStep`). Facilitates offline iteration without camera or ArUco markers.

### 4. Focus Rings

Global `:focus-visible` outline using `--accent` for clarity on tabbable elements (used primarily in mock viewer; MagicMirror module reserved for future interactive controls).

### 5. Animation Fallbacks

Progress bar and ring pulse animations instantly switch to static states when reduced-motion is active, avoiding distracting pulsing or sliding effects for sensitive users.

## Backend Fields

- `/settings` accepts `reduce_motion: bool`
- `/health` returns `reduce_motion` flag for clients
- Status broadcast includes `reduce_motion` when toggled

## Testing Checklist

- Toggle OS-level reduced motion on macOS or Windows and confirm pulses stop.
- POST `{"reduce_motion": true}` then verify HUD enters without animation and ring pulses stop even if OS preference allows motion.
- Press keys `1`, `2`, `3` to ensure local demo overlays appear without camera.
- Inspect color contrast (e.g., use browser dev tools Lighthouse) — aim for WCAG AA for text & UI components.

## Planned Improvements

- User-adjustable `fontScale` via `/settings` for dynamic text enlargement
- Voice command or tactile input mapping to demo steps for non-keyboard environments
- Alt text / ARIA labels for future interactive controls
- Automatic dark/light theme variant based on ambient light sensor data

## Contributing

When adding new UI motion:

- Gate animations behind `!reduceMotion` checks
- Provide a static fallback style
- Avoid large abrupt translations (>40px) in a single frame

When introducing new colors or surfaces:

- Reuse existing tokens or extend with carefully named semantic variables
- Test contrast ratio with target foreground/background (AA large text ≥ 3:1, normal ≥ 4.5:1)

---

Last updated: 2025-11-08
