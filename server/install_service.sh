#!/bin/bash

# Witchborn Codex Server Installer (Systemd)
# Usage: sudo ./install_service.sh

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./install_service.sh)"
  exit 1
fi

echo "=== Witchborn Codex Server Installer ==="

# 1. Determine Paths
# We assume this script is inside server/ directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"
USER_NAME=$(logname)
GROUP_NAME=$(id -gn $USER_NAME)

# 2. Check for Virtual Environment
if [ ! -f "$VENV_PYTHON" ]; then
    echo "[!] Error: .venv not found at $VENV_PYTHON"
    echo "    Please run 'python3 -m venv .venv' and 'pip install -r requirements.txt' in the project root first."
    exit 1
fi

echo "[*] Installing service for user: $USER_NAME"
echo "[*] Server Root: $SCRIPT_DIR"

# 3. Create Systemd Service File
SERVICE_FILE="/etc/systemd/system/witchborn-codex.service"

cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=Witchborn Codex Authority Server
After=network.target

[Service]
Type=simple
User=$USER_NAME
Group=$GROUP_NAME
WorkingDirectory=$SCRIPT_DIR
# Run uvicorn directly via the venv python to ensure deps are loaded
ExecStart=$VENV_PYTHON $MAIN_SCRIPT
Restart=always
RestartSec=5
Environment=CODEX_PORT=8000
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# 4. Enable and Start
echo "[*] Reloading systemd daemon..."
systemctl daemon-reload

echo "[*] Enabling witchborn-codex service..."
systemctl enable witchborn-codex

echo "[*] Starting service..."
systemctl restart witchborn-codex

echo "========================================================"
echo "SUCCESS: Server is running."
echo "View logs:  journalctl -u witchborn-codex -f"
echo "Stop server: sudo systemctl stop witchborn-codex"
echo "========================================================"