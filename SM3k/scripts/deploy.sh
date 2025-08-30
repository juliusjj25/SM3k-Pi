#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="/opt/SM3k"
ENV_DIR="$REPO_DIR/.venv"

sudo systemctl stop smoker.service || true

# If the Pi has the repo as a git clone in /opt/smoker:
if [ -d "$REPO_DIR/.git" ]; then
  git -C "$REPO_DIR" fetch --all
  git -C "$REPO_DIR" reset --hard origin/main
else
  # Otherwise, sync from your working copy (run this script from your repo root)
  sudo rsync -a --delete ./ "$REPO_DIR/"
fi

"$ENV_DIR/bin/pip" install -r "$REPO_DIR/requirements.txt"

sudo systemctl start smoker.service
sudo systemctl --no-pager status smoker.service
