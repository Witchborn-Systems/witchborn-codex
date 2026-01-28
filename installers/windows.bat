@echo off
setlocal
title Witchborn Codex Master Installer

:: 1. Check Admin Rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] ERROR: Please right-click and 'Run as Administrator'.
    pause
    exit /b
)

:: 2. Setup Paths
set "SOURCE_DIR=%~dp0..\client\dist"
set "INSTALL_DIR=C:\Program Files\WitchbornCodex"
set "HANDLER_EXE=%INSTALL_DIR%\codex-handle.exe"

echo [*] Installing Witchborn Codex...
echo     Source: %SOURCE_DIR%
echo     Dest:   %INSTALL_DIR%

:: 3. Create Directory & Copy Files
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copy Handler (Silent Version)
copy /Y "%SOURCE_DIR%\codex-handle.exe" "%INSTALL_DIR%\" >nul
if %errorlevel% neq 0 (
    echo [!] ERROR: Could not find codex-handle.exe in dist folder!
    echo     Did you run 'pyinstaller' yet?
    pause
    exit /b
)

:: Copy CLI Tool
if exist "%SOURCE_DIR%\ailookup.exe" (
    copy /Y "%SOURCE_DIR%\ailookup.exe" "%INSTALL_DIR%\" >nul
) else (
    echo [!] Warning: ailookup.exe not found. Skipping CLI tool.
)

:: 4. Register Protocols (The Magic Part)
echo [*] Registering Protocols in Windows Registry...

:: Register ai://
reg add "HKCR\ai" /ve /t REG_SZ /d "URL:Witchborn AI Identity" /f >nul
reg add "HKCR\ai" /v "URL Protocol" /t REG_SZ /d "" /f >nul
reg add "HKCR\ai\DefaultIcon" /ve /t REG_SZ /d "\"%HANDLER_EXE%\",0" /f >nul
reg add "HKCR\ai\shell\open\command" /ve /t REG_SZ /d "\"%HANDLER_EXE%\" \"%%1\"" /f >nul

:: Register mcp://
reg add "HKCR\mcp" /ve /t REG_SZ /d "URL:Witchborn MCP Agent" /f >nul
reg add "HKCR\mcp" /v "URL Protocol" /t REG_SZ /d "" /f >nul
reg add "HKCR\mcp\DefaultIcon" /ve /t REG_SZ /d "\"%HANDLER_EXE%\",0" /f >nul
reg add "HKCR\mcp\shell\open\command" /ve /t REG_SZ /d "\"%HANDLER_EXE%\" \"%%1\"" /f >nul

:: 5. Add to System PATH
echo [*] Adding to System PATH...
setx /M PATH "%PATH%;%INSTALL_DIR%" >nul

echo.
echo ========================================================
echo  [SUCCESS] Witchborn Codex Installed!
echo ========================================================
echo.
echo  1. Open Chrome or Edge.
echo  2. Type: ai://acme@webai
echo  3. Hit Enter.
echo.
pause