#!/usr/bin/env bash
# Reload MagicMirror without restarting backend

echo "🔄 Reloading MagicMirror..."

# Kill MagicMirror
pkill -f "electron.*MagicMirror" || true
pkill -f "npm.*start.*MagicMirror" || true
sleep 2

# Restart MagicMirror
cd ~/MagicMirror
npm start > /tmp/magicmirror.log 2>&1 &

echo "✅ MagicMirror restarted"
echo "📝 Logs: tail -f /tmp/magicmirror.log"
