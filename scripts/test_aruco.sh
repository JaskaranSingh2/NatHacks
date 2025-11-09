#!/usr/bin/env bash
set -euo pipefail

<<<<<<< HEAD
# Start backend (if not already running)
python - <<'PY'
=======
# Determine python interpreter
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN=python
else
  echo "No python interpreter found." >&2
  exit 1
fi

# Start backend (if not already running)
$PYTHON_BIN - <<'PY'
>>>>>>> 3fd54b7223d6d85794d599f6829e5349642b0e6f
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
<<<<<<< HEAD
    import subprocess
    p = subprocess.Popen(['python','-m','uvicorn','backend.app:app','--host','0.0.0.0','--port','5055'])
=======
  import subprocess, os
  py = os.environ.get('PYTHON_BIN','python3')
  p = subprocess.Popen([py,'-m','uvicorn','backend.app:app','--host','0.0.0.0','--port','5055'])
>>>>>>> 3fd54b7223d6d85794d599f6829e5349642b0e6f
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
