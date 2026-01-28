@echo off
setlocal
title Witchborn Codex Uninstaller

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Run as Administrator.
    pause
    exit /b
)

echo [*] Removing Registry Keys...
reg delete "HKCR\ai" /f
reg delete "HKCR\mcp" /f

echo [*] Keys deleted. Windows will no longer recognize ai:// links.
pause