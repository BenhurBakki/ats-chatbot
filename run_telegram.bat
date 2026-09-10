@echo off
title ATS Telegram Bot Runner - @BennhurBot
echo ========================================================
echo   Starting ATS Telegram Bot (@BennhurBot) in Polling Mode
echo   Chat live at: https://t.me/BennhurBot
echo ========================================================

set PYTHON_EXEC=python
where python >nul 2>nul
if %errorlevel% neq 0 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
        set PYTHON_EXEC="%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    )
)

%PYTHON_EXEC% telegram_bot_runner.py
pause
