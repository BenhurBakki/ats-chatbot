# ATS Chatbot Local PowerShell Runner
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  ATS Optimization & Multi-Channel Chatbot Launcher    " -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

if ($pythonCmd) {
    Write-Host "[1/2] Installing requirements..." -ForegroundColor Green
    pip install -r requirements.txt
    Write-Host "[2/2] Launching server on http://localhost:8000..." -ForegroundColor Green
    Start-Process "http://localhost:8000"
    python main.py
} else {
    Write-Host "[INFO] Python CLI not detected in current PATH." -ForegroundColor Yellow
    Write-Host "[INFO] Launching interactive standalone console in browser..." -ForegroundColor Green
    $indexPath = Join-Path $PSScriptRoot "static\index.html"
    Start-Process $indexPath
}
