#!/bin/bash
APP_NAME="WitchbornCodex"
APP_DIR="/Applications/$APP_NAME.app"

echo "=== Witchborn Codex Uninstaller (macOS) ==="

# 1. Unregister with LaunchServices
if [ -d "$APP_DIR" ]; then
    /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -u "$APP_DIR"
    rm -rf "$APP_DIR"
    echo "[*] Removed App Bundle and unregistered protocols."
fi

# 2. Uninstall Package
pip3 uninstall codexai -y
echo "[SUCCESS] Uninstallation complete."