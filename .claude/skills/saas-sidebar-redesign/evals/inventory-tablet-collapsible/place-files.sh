#!/usr/bin/env bash
# Copies this repo's own client/ and CLAUDE.md as the input, so the test
# always runs against the current app instead of a duplicated snapshot.
set -eu
REPO="$(cd "$(dirname "$0")/../../../../.." && pwd)"
cp "$REPO/CLAUDE.md" .
rsync -a --exclude node_modules --exclude dist "$REPO/client" .
