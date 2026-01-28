@echo off
setlocal
title Witchborn Codex Protocol Installer (Windows)

echo [1/3] Verifying Environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b
)

echo [2/3] Installing Codex Client Library...
:: Assumes running from repo root. If distributed, this would be 'pip install codex-ai'
pip install ..\client --upgrade --quiet

:: Find where pip put the executable
for /f "tokens=*" %%i in ('where codex-handle') do set HANDLER_PATH=%%i

if "%HANDLER_PATH%"=="" (
    echo [ERROR] Could not locate 'codex-handle'. Installation failed.
    pause
    exit /b
)

echo [3/3] Registering Protocols (Requires Admin)...

:: Register ai://
reg add "HKEY_CLASSES_ROOT\ai" /ve /t REG_SZ /d "Witchborn AI Protocol" /f
reg add "HKEY_CLASSES_ROOT\ai" /v "URL Protocol" /t REG_SZ /d "" /f
reg add "HKEY_CLASSES_ROOT\ai\shell\open\command" /ve /t REG_SZ /d "\"%HANDLER_PATH%\" \"%%1\"" /f

:: Register mcp://
reg add "HKEY_CLASSES_ROOT\mcp" /ve /t REG_SZ /d "Witchborn MCP Protocol" /f
reg add "HKEY_CLASSES_ROOT\mcp" /v "URL Protocol" /t REG_SZ /d "" /f
reg add "HKEY_CLASSES_ROOT\mcp\shell\open\command" /ve /t REG_SZ /d "\"%HANDLER_PATH%\" \"%%1\"" /f

echo.
echo ========================================================
echo  SUCCESS: Protocols Registered
echo  Handler: %HANDLER_PATH%
echo ========================================================
echo.
pause