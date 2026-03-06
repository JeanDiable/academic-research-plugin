#!/bin/bash
# Sync .claude-plugin/ metadata from root plugin.json, then commit and push.
# Usage: ./publish.sh "commit message"
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

ROOT_JSON="plugin.json"
CP_JSON=".claude-plugin/plugin.json"
MKT_JSON=".claude-plugin/marketplace.json"

if [ ! -f "$ROOT_JSON" ]; then
    echo "Error: $ROOT_JSON not found"
    exit 1
fi

# Extract fields from root plugin.json
VERSION=$(python3 -c "import json; print(json.load(open('$ROOT_JSON'))['version'])")
NAME=$(python3 -c "import json; print(json.load(open('$ROOT_JSON'))['name'])")
DESC=$(python3 -c "import json; print(json.load(open('$ROOT_JSON'))['description'])")

echo "Syncing .claude-plugin/ to v$VERSION..."

# Write .claude-plugin/plugin.json (name, version, description ONLY — no skills!)
python3 -c "
import json
data = {'name': '$NAME', 'version': '$VERSION', 'description': '''$DESC'''}
with open('$CP_JSON', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"

# Update version in marketplace.json
python3 -c "
import json
with open('$MKT_JSON') as f:
    data = json.load(f)
for p in data.get('plugins', []):
    if p['name'] == '$NAME':
        p['version'] = '$VERSION'
with open('$MKT_JSON', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"

echo "  $CP_JSON -> v$VERSION"
echo "  $MKT_JSON -> v$VERSION"

# Stage and commit if there are changes
git add -A
if git diff --cached --quiet; then
    echo "No changes to commit."
else
    MSG="${1:-chore: bump to v$VERSION}"
    git commit -m "$MSG"
fi

# Push
echo "Pushing to origin..."
git push

echo "Done! Run 'claude-plugin-update' to refresh in Claude Code."
