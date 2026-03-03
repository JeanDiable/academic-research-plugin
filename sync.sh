#!/bin/bash
# sync.sh — Copies shared scripts from lib/ to each skill's scripts/ directory.
# Run this after editing any file in lib/.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Skills that need paper_search.py + bibtex_utils.py
SEARCH_SKILLS=(
    literature-survey
    paper-triggered-survey
    survey-writing
    paper-reviewing
    paper-polishing
    citation-assistant
    homework-machine
)

for skill in "${SEARCH_SKILLS[@]}"; do
    mkdir -p "skills/$skill/scripts"
    cp lib/paper_search.py "skills/$skill/scripts/"
    cp lib/bibtex_utils.py "skills/$skill/scripts/"
    cp lib/requirements.txt "skills/$skill/scripts/"
    echo "  Synced → skills/$skill/scripts/"
done

# homework-machine also needs translate_roundtrip.py
cp lib/translate_roundtrip.py skills/homework-machine/scripts/
echo "  Synced translate_roundtrip.py → skills/homework-machine/scripts/"

echo "Done. All skills synced."
