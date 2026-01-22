@echo off
:: Telegram to Obsidian Quick Capture - Startup Script
:: Place a shortcut to this file in your Windows Startup folder
:: (Win + R, then type: shell:startup)

cd /d "%~dp0"
python sync_thoughts.py

:: Keep window open briefly to see results (remove these lines for silent operation)
echo.
echo Press any key to close...
timeout /t 5 /nobreak >nul
