<#
.SYNOPSIS
    Automates Git initialization and push to GitHub for AWS Amplify Deployment.
.DESCRIPTION
    This script initializes Git (if not already initialized), adds files,
    commits, and pushes to your GitHub repository.
.EXAMPLE
    .\push_to_github.ps1 -GitHubRepoUrl "https://github.com/your-username/ats-chatbot.git"
#>

param (
    [Parameter(Mandatory=$false)]
    [string]$GitHubRepoUrl = ""
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Push ATS Chatbot Repository to GitHub for AWS Amplify   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Write-Error "❌ Git is not installed or not found in PATH. Please install Git first."
    exit 1
}

# 1. Initialize Git repository if needed
if (-not (Test-Path ".git")) {
    Write-Host "📁 [1/4] Initializing new Git repository..." -ForegroundColor Yellow
    git init
    git branch -M main
} else {
    Write-Host "📁 [1/4] Git repository already initialized." -ForegroundColor Green
}

# 2. Stage and commit files
Write-Host "`n📝 [2/4] Staging and committing files..." -ForegroundColor Yellow
git add .
git commit -m "Deploy ATS Optimization & Multi-Channel Portal with AWS Amplify" --allow-empty

# 3. Handle remote origin
if (-not $GitHubRepoUrl) {
    Write-Host "`n🔗 [3/4] Enter your GitHub Repository URL" -ForegroundColor Yellow
    Write-Host "Example: https://github.com/your-username/ats-chatbot.git" -ForegroundColor Gray
    $GitHubRepoUrl = Read-Host "GitHub Repo URL"
}

if ($GitHubRepoUrl) {
    # Check if origin already exists
    $existingRemote = git remote get-url origin 2>$null
    if ($existingRemote) {
        git remote set-url origin $GitHubRepoUrl
    } else {
        git remote add origin $GitHubRepoUrl
    }
    Write-Host "✅ Remote origin configured: $GitHubRepoUrl" -ForegroundColor Green

    # 4. Push to GitHub
    Write-Host "`n🚀 [4/4] Pushing code to GitHub (main branch)..." -ForegroundColor Yellow
    git push -u origin main

    Write-Host "`n==========================================================" -ForegroundColor Green
    Write-Host "🎉 Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "Next step: Open AWS Amplify Console and select this repo." -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Green
} else {
    Write-Host "`n⚠️ No GitHub URL provided. You can push manually using:" -ForegroundColor Yellow
    Write-Host "  git remote add origin <YOUR_GITHUB_REPO_URL>"
    Write-Host "  git push -u origin main"
}
