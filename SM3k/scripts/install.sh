#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/opt/SM3k"
ENV_DIR="$REPO_DIR/.venv"
CONF_DIR="/etc/SM3k"
DATA_DIR="/var/lib/SM3k"
UNIT="/etc/systemd/system/smoker.service"

sudo mkdir -p "$REPO_DIR" "$CONF_DIR" "$DATA_DIR"
sudo chown -R "$USER":"$USER" "$REPO_DIR" "$CONF_DIR" "$DATA_DIR"

# Copy (or git clone beforehand) your project into /opt/smoker
# If you're running this from your repo root:
sudo rsync -a --delete ./ "$REPO_DIR/"

# venv
python3 -m venv "$ENV_DIR"
"$ENV_DIR/bin/pip" install --upgrade pip
"$ENV_DIR/bin/pip" install -r "$REPO_DIR/requirements.txt"

# default config if missing
[ -f "$CONF_DIR/smoker.yaml" ] || sudo cp "$REPO_DIR/smoker.yaml" "$CONF_DIR/smoker.yaml"
[ -f "$CONF_DIR/.env" ] || sudo cp "$REPO_DIR/.env.example" "$CONF_DIR/.env"

# systemd unit
sudo tee "$UNIT" >/dev/null <<'UNIT'
[Unit]
Description=Smoker Controller
After=network-online.target
Wants=network-online.target

[Service]
User=%i
WorkingDirectory=/opt/SM3k
EnvironmentFile=/etc/SM3k/.env
Environment="PYTHONPATH=/opt/SM3k"
ExecStart=/opt/SM3k/.venv/bin/python -m smoker.main --config /etc/SM3k/smoker.yaml --data /var/lib/SM3k
Restart=always
RestartSec=2
Nice=-10
CPUSchedulingPolicy=rr
CPUSchedulingPriority=50
# Hard watchdog optional:
# RuntimeWatchdogSec=10s

[Install]
WantedBy=multi-user.target
UNIT

# Enable for current user (replace %i in unit with your user)
sudo systemctl enable --now smoker.service
sudo systemctl restart smoker.service
sudo systemctl status --no-pager smoker.service
