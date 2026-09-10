@echo off
title ATS Chatbot Local Launcher
echo =======================================================
echo   ATS Optimization & Multi-Channel Chatbot Launcher
echo =======================================================
echo.

:: Check if python is available
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [1/2] Installing / checking Python dependencies...
    pip install -r requirements.txt
    echo.
    echo [2/2] Starting FastAPI Server on http://localhost:8000 ...
    start http://localhost:8000
    python main.py
) else (
    echo [INFO] Python not found in system PATH.
    echo [INFO] Opening standalone web console in your default browser...
    start "" "%~dp0static\index.html"
)

pause
