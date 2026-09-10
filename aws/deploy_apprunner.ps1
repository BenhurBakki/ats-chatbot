<#
.SYNOPSIS
    Automated AWS Deployment Script for ATS Multi-Channel Chatbot.
.DESCRIPTION
    This PowerShell script automates:
    1. AWS Account & Region discovery
    2. ECR Repository Creation
    3. IAM Role configuration for App Runner
    4. Building and pushing Docker container image
    5. Creating or updating AWS App Runner service
    6. Returning the live public HTTPS service URL
.EXAMPLE
    .\aws\deploy_apprunner.ps1 -Region "us-east-1"
#>

param (
    [string]$Region = "us-east-1",
    [string]$RepoName = "ats-multi-channel-chatbot",
    [string]$ServiceName = "ats-multi-channel-chatbot"
)

$ErrorActionPreference = "Stop"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  AWS App Runner Deployment - ATS Multi-Channel Chatbot         " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check AWS CLI prerequisites
Write-Host "🔍 [1/6] Verifying AWS CLI and Docker..." -ForegroundColor Yellow
try {
    $callerIdentity = aws sts get-caller-identity --output json | ConvertFrom-Json
    $accountId = $callerIdentity.Account
    Write-Host "✅ AWS Authentication verified. Account ID: $accountId | Region: $Region" -ForegroundColor Green
} catch {
    Write-Error "❌ AWS CLI is not configured or authenticated. Please run 'aws configure' first."
    exit 1
}

# 2. Create ECR Repository if it doesn't already exist
Write-Host "`n📦 [2/6] Setting up Amazon ECR Repository ($RepoName)..." -ForegroundColor Yellow
$ecrRepoUri = "$accountId.dkr.ecr.$Region.amazonaws.com/$RepoName"
try {
    aws ecr describe-repositories --repository-names $RepoName --region $Region 2>&1 | Out-Null
    Write-Host "✅ ECR Repository already exists: $ecrRepoUri" -ForegroundColor Green
} catch {
    Write-Host "Creating new ECR repository..." -ForegroundColor Gray
    aws ecr create-repository --repository-name $RepoName --region $Region --image-scanning-configuration scanOnPush=true | Out-Null
    Write-Host "✅ Created ECR repository: $ecrRepoUri" -ForegroundColor Green
}

# 3. Create IAM Role for App Runner to pull from private ECR
Write-Host "`n🔑 [3/6] Configuring IAM Role for App Runner..." -ForegroundColor Yellow
$roleName = "AppRunnerECRAccessRole"
$trustPolicy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "build.apprunner.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
"@

try {
    aws iam get-role --role-name $roleName 2>&1 | Out-Null
    Write-Host "✅ IAM Role already exists: $roleName" -ForegroundColor Green
} catch {
    $tempTrustFile = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $tempTrustFile -Value $trustPolicy
    aws iam create-role --role-name $roleName --assume-role-policy-document "file://$tempTrustFile" | Out-Null
    aws iam attach-role-policy --role-name $roleName --policy-arn "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess" | Out-Null
    Remove-Item $tempTrustFile
    Write-Host "✅ Created and attached IAM Role: $roleName" -ForegroundColor Green
}
$roleArn = "arn:aws:iam::$accountId:role/$roleName"

# 4. Authenticate Docker and Push Image to ECR
Write-Host "`n🐳 [4/6] Building and Pushing Docker Image to Amazon ECR..." -ForegroundColor Yellow
Write-Host "Logging into Amazon ECR..." -ForegroundColor Gray
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$accountId.dkr.ecr.$Region.amazonaws.com"

Write-Host "Building Docker image (target platform: linux/amd64)..." -ForegroundColor Gray
docker build --platform linux/amd64 -t "$RepoName`:latest" .
docker tag "$RepoName`:latest" "$ecrRepoUri`:latest"

Write-Host "Pushing Docker image to ECR..." -ForegroundColor Gray
docker push "$ecrRepoUri`:latest"
Write-Host "✅ Container image successfully pushed to ECR." -ForegroundColor Green

# 5. Deploy / Update AWS App Runner Service
Write-Host "`n🚀 [5/6] Deploying to AWS App Runner ($ServiceName)..." -ForegroundColor Yellow

# Read JSON template and replace tokens
$configTemplate = Get-Content -Path "aws/apprunner_service.json" -Raw
$configJson = $configTemplate -replace "<AWS_ACCOUNT_ID>", $accountId -replace "<AWS_REGION>", $Region

$tempConfigFile = [System.IO.Path]::GetTempFileName()
Set-Content -Path $tempConfigFile -Value $configJson

# Check if service already exists
$existingService = aws apprunner list-services --region $Region --output json | ConvertFrom-Json
$targetService = $existingService.ServiceSummaryList | Where-Object { $_.ServiceName -eq $ServiceName }

if ($targetService) {
    Write-Host "Service exists. Triggering new deployment..." -ForegroundColor Gray
    aws apprunner start-deployment --service-arn $targetService.ServiceArn --region $Region | Out-Null
    $serviceArn = $targetService.ServiceArn
} else {
    Write-Host "Creating new App Runner Service..." -ForegroundColor Gray
    $createResult = aws apprunner create-service --cli-input-json "file://$tempConfigFile" --region $Region --output json | ConvertFrom-Json
    $serviceArn = $createResult.Service.ServiceArn
}
Remove-Item $tempConfigFile

# 6. Retrieve Live Service URL
Write-Host "`n🌐 [6/6] Fetching Live Service Information..." -ForegroundColor Yellow
$serviceDetails = aws apprunner describe-service --service-arn $serviceArn --region $Region --output json | ConvertFrom-Json
$serviceUrl = "https://" + $serviceDetails.Service.ServiceUrl

Write-Host "`n================================================================" -ForegroundColor Green
Write-Host "🎉 DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host "🔗 Live Web App & API URL : $serviceUrl" -ForegroundColor Cyan
Write-Host "🔗 Health Check URL       : $serviceUrl/health" -ForegroundColor Cyan
Write-Host "🔗 WhatsApp Webhook       : $serviceUrl/webhook/whatsapp" -ForegroundColor Cyan
Write-Host "🔗 Slack Events Webhook   : $serviceUrl/webhook/slack" -ForegroundColor Cyan
Write-Host "🔗 Instagram Webhook      : $serviceUrl/webhook/instagram" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Green
