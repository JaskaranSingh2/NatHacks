#!/usr/bin/env bash
set -euo pipefail
BASE_URL=${BASE_URL:-http://localhost:5055}
PAYLOAD_FILE=${1:-test_animation.json}
if [ ! -f "$PAYLOAD_FILE" ]; then
  echo "Payload file $PAYLOAD_FILE not found" >&2
  exit 1
fi
curl -s -X POST "$BASE_URL/overlay" -H 'Content-Type: application/json' --data-binary @"$PAYLOAD_FILE" | jq . || true
