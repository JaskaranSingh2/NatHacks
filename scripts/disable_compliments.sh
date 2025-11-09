#!/usr/bin/env bash
# Disable the compliments module in MagicMirror config
set -e

CONFIG_FILE=~/MagicMirror/config/config.js

echo "🔧 Disabling compliments module..."

# Backup original
cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%s)"

# Comment out the compliments module
sed -i '' '/module: "compliments"/,/^[[:space:]]*},/s/^[[:space:]]*module:/\/\/ module:/' "$CONFIG_FILE"
sed -i '' '/module: "compliments"/,/^[[:space:]]*},/s/^[[:space:]]*position:/\/\/ position:/' "$CONFIG_FILE"

echo "✅ Compliments module disabled!"
echo "📝 Backup saved to: $CONFIG_FILE.backup.*"
echo ""
echo "🔄 Reload MagicMirror to see changes:"
echo "   cd ~/Documents/Engineering/Coding/NatHacks"
echo "   ./scripts/reload_mm.sh"
