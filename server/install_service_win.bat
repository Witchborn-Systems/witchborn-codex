@echo off
setlocal
title Witchborn Codex Server Installer (Windows)

:: 1. Check Admin Privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] ERROR: This script requires Administrator privileges.
    echo     Right-click and select "Run as administrator".
    pause
    exit /b
)

echo === Witchborn Codex Server Installer ===

:: 2. Determine Paths
set "SCRIPT_DIR=%~dp0"
:: Remove trailing backslash if present
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Assume standard structure: server/ is one level deep, so root is up one
set "PROJECT_ROOT=%SCRIPT_DIR%\.."
set "VENV_PYTHON=%PROJECT_ROOT%\.venv\Scripts\python.exe"
set "MAIN_SCRIPT=%SCRIPT_DIR%\main.py"

:: 3. Verify Environment
if not exist "%VENV_PYTHON%" (
    echo [!] Error: Python Virtual Environment not found.
    echo     Expected at: %VENV_PYTHON%
    echo     Please run 'python -m venv .venv' and 'pip install -r requirements.txt' first.
    pause
    exit /b
)

echo [*] Server Script: %MAIN_SCRIPT%
echo [*] Python Path:   %VENV_PYTHON%

:: 4. Create Scheduled Task
:: /tn : Task Name
:: /tr : Task Run (The command)
:: /sc : Schedule (ONSTART runs at boot)
:: /ru : Run User (SYSTEM account runs in background, no window)
:: /f  : Force overwrite if exists

echo [*] Registering 'WitchbornCodexServer' to run at system startup...

schtasks /create /tn "WitchbornCodexServer" ^
    /tr "\"%VENV_PYTHON%\" \"%MAIN_SCRIPT%\"" ^
    /sc onstart ^
    /ru SYSTEM ^
    /f

if %errorlevel% neq 0 (
    echo [!] Failed to create task.
    pause
    exit /b
)

echo.
echo ========================================================
echo  SUCCESS: Server Service Installed.
echo.
echo  To Start Now:   schtasks /run /tn "WitchbornCodexServer"
echo  To Stop:        schtasks /end /tn "WitchbornCodexServer"
echo  To Uninstall:   schtasks /delete /tn "WitchbornCodexServer" /f
echo ========================================================
echo.
pause