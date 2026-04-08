#!/bin/bash
set -euo pipefail

# Only run in remote (Claude Code web) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Configure git remote with push access
git -C "$CLAUDE_PROJECT_DIR" remote set-url origin https://pulkitkd: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@github.com/pulkitkd/feed_generator.git

# Install Python dependencies
pip install -r "$CLAUDE_PROJECT_DIR/requirements.txt" --quiet
