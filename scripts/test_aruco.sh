#!/usr/bin/env bash
set -euo pipefail

# Start backend (if not already running)
python - <<'PY'
import asyncio, json
from contextlib import suppress
import http.client

try:
    conn = http.client.HTTPConnection('localhost', 5055, timeout=0.5)
    conn.request('GET', '/health')
    resp = conn.getresponse()
    print('Backend already running' if resp.status==200 else 'Starting backend...')
except Exception:
    print('Starting backend...')
    import subprocess
    p = subprocess.Popen(['python','-m','uvicorn','backend.app:app','--host','0.0.0.0','--port','5055'])
PY

# Toggle aruco + pose
curl -s -X POST http://localhost:5055/settings \
  -H 'Content-Type: application/json' \
  -d '{"aruco": true, "pose": true}' | jq -r '.aruco,.pose'

# Start a session
curl -s -X POST http://localhost:5055/session/start \
  -H 'Content-Type: application/json' \
  -d '{"routine_id":"brush_teeth"}' | jq -r '.status'

echo 'Move marker 23 near mouth target and observe overlay states.'
