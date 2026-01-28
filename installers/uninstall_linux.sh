#!/bin/bash
echo "=== Witchborn Codex Uninstaller (Linux) ==="

# 1. Remove Desktop Entry
DESKTOP_FILE="$HOME/.local/share/applications/codex-handler.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo "[*] Removed desktop entry."
fi

# 2. Update MIME Database
xdg-mime uninstall "$DESKTOP_FILE" 2>/dev/null
update-desktop-database "$HOME/.local/share/applications"

# 3. Uninstall Package
pip uninstall codexai -y
echo "[SUCCESS] Protocols deregistered and package removed."