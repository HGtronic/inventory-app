#!/usr/bin/env bash
# Copies the inventory app (client, server, CLAUDE.md) as of a pinned commit, so the
# graders' line references stay valid while the live working tree keeps changing.
set -eu
REPO="$(cd "$(dirname "$0")/../../../../.." && pwd)"
COMMIT=a60d7da
if git -C "$REPO" cat-file -e "$COMMIT^{commit}" 2>/dev/null; then
  git -C "$REPO" archive "$COMMIT" client server CLAUDE.md | tar -x
else
  rsync -a --exclude node_modules --exclude dist --exclude .venv --exclude __pycache__ \
    "$REPO/client" "$REPO/server" "$REPO/CLAUDE.md" .
fi
