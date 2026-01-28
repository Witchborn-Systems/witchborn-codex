#!/bin/bash

echo "=== Witchborn Codex Installer (Linux) ==="

# 1. Install Lib
echo "[*] Installing Python Package..."
pip install ../client --upgrade --quiet

# Locate the binary
HANDLER_BIN=$(which codex-handle)
if [ -z "$HANDLER_BIN" ]; then
    echo "[!] Error: codex-handle not found in PATH."
    exit 1
fi
echo "[*] Found Handler: $HANDLER_BIN"

# 2. Create Desktop Entry
DESKTOP_FILE="$HOME/.local/share/applications/codex-handler.desktop"
mkdir -p "$HOME/.local/share/applications"

cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Type=Application
Name=Witchborn Codex Handler
Exec=$HANDLER_BIN %u
StartupNotify=false
MimeType=x-scheme-handler/ai;x-scheme-handler/mcp;
EOF

# 3. Register MIME Types
echo "[*] Registering x-scheme-handler..."
xdg-mime default codex-handler.desktop x-scheme-handler/ai
xdg-mime default codex-handler.desktop x-scheme-handler/mcp

echo "[SUCCESS] ai:// and mcp:// are now active."