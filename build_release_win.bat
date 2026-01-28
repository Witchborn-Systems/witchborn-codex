@echo off
setlocal
title Witchborn Codex - Build Release v1.0

set "REL_NAME=WitchbornCodex_Win_v1.0"
set "DIST_DIR=client\dist"
set "REL_DIR=release\%REL_NAME%"

echo [*] Cleaning old builds...
if exist "release" rmdir /s /q "release"
mkdir "%REL_DIR%"

echo [*] Copying Binaries...
copy /Y "%DIST_DIR%\ailookup.exe" "%REL_DIR%\"
copy /Y "%DIST_DIR%\codex-handle.exe" "%REL_DIR%\"

echo [*] Copying Installer...
copy /Y "installers\install_witchborn.bat" "%REL_DIR%\"
copy /Y "README.md" "%REL_DIR%\"
copy /Y "LICENSE" "%REL_DIR%\"

echo.
echo ========================================================
echo [SUCCESS] Release Ready!
echo Location: %REL_DIR%
echo.
echo Action: Right-click the '%REL_NAME%' folder and "Compress to ZIP"
echo ========================================================
pause