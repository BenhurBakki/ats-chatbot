# PowerShell runner for ATS Telegram Bot (@BennhurBot)
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting ATS Telegram Bot (@BennhurBot) in Polling Mode" -ForegroundColor Green
Write-Host "  Chat live at: https://t.me/BennhurBot" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan

$python = "python"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    if (Test-Path "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe") {
        $python = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
    }
}

& $python telegram_bot_runner.py
