#!/bin/bash

APP_NAME="WitchbornCodex"
APP_DIR="/Applications/$APP_NAME.app"

echo "=== Witchborn Codex Installer (macOS) ==="

# 1. Install Lib
pip3 install ../client --upgrade --quiet

# Find the python script path
HANDLER_BIN=$(which codex-handle)
if [ -z "$HANDLER_BIN" ]; then
    echo "[!] Error: codex-handle not found. Ensure pip install succeeded."
    exit 1
fi

echo "[*] Creating App Bundle at $APP_DIR..."

# 2. Create Directory Structure
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# 3. Create Info.plist (The Magic Part)
# This tells macOS: "I handle ai:// and mcp://"
cat <<EOF > "$APP_DIR/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>org.witchbornsystems.codex</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleURLTypes</key>
    <array>
        <dict>
            <key>CFBundleURLName</key>
            <string>Witchborn AI Protocol</string>
            <key>CFBundleURLSchemes</key>
            <array>
                <string>ai</string>
            </array>
        </dict>
        <dict>
            <key>CFBundleURLName</key>
            <string>Witchborn MCP Protocol</string>
            <key>CFBundleURLSchemes</key>
            <array>
                <string>mcp</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
EOF

# 4. Create the Launcher Script
# This is the shim that runs when the App "opens" a URL
cat <<EOF > "$APP_DIR/Contents/MacOS/launcher"
#!/bin/bash
# Pass the arguments (the URL) to the Python handler
"$HANDLER_BIN" "\$@"
EOF

chmod +x "$APP_DIR/Contents/MacOS/launcher"

# 5. Register with LaunchServices
echo "[*] Registering with macOS..."
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP_DIR"

echo "[SUCCESS] Installation complete."
echo "You can now type 'open ai://root' in your terminal to test."