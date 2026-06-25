#!/bin/sh
# AKASHA one-shot bootstrap — агент запускает сам, пользователь только даёт URL brain.
set -e
BRAIN_URL="$1"
AGENT="${2:-cursor}"
SCOPE="${3:-project}"
python3 -m pip install --user --upgrade "git+https://github.com/sikuykus-lab/akasha-core.git"
exec python3 -m akash_core.cli onboard "$BRAIN_URL" --agent "$AGENT" --scope "$SCOPE"
