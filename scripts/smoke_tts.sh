#!/usr/bin/env bash
set -euo pipefail
BASE_URL=${BASE_URL:-http://localhost:5055}
TEXT=${1:-"Magic mirror online"}
JSON=$(printf '{"text":"%s"}' "$TEXT")
curl -s -X POST "$BASE_URL/tts" -H 'Content-Type: application/json' -d "$JSON" | jq . || true
