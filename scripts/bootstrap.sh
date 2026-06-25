#!/bin/sh
# AKASHA one-shot bootstrap — SaaS akasha-core → private brain на GitHub пользователя.
set -e
SAAS_URL="${1:-https://github.com/sikuykus-lab/akasha-core}"
AGENT="${2:-cursor}"
SCOPE="${3:-project}"
python3 -m pip install --user --upgrade "git+https://github.com/sikuykus-lab/akasha-core.git"
exec python3 -m akash_core.cli onboard "$SAAS_URL" --agent "$AGENT" --scope "$SCOPE"
