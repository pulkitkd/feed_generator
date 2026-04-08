#!/bin/bash
set -euo pipefail

# Only run in remote (Claude Code web) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Configure git remote with push access (token stored outside repo)
TOKEN_FILE="$HOME/.github_pat"
if [ -f "$TOKEN_FILE" ]; then
  TOKEN=$(cat "$TOKEN_FILE")
  git -C "$CLAUDE_PROJECT_DIR" remote set-url origin "https://pulkitkd:${TOKEN}@github.com/pulkitkd/feed_generator.git"
else
  echo "Warning: $TOKEN_FILE not found. Git push access not configured."
fi

# Install Python dependencies
pip install -r "$CLAUDE_PROJECT_DIR/requirements.txt" --quiet
