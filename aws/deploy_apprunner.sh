#!/usr/bin/env bash
# ==============================================================================
# Automated AWS App Runner Deployment Script - ATS Multi-Channel Chatbot
# ==============================================================================
set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
REPO_NAME="ats-multi-channel-chatbot"
SERVICE_NAME="ats-multi-channel-chatbot"

echo "================================================================"
echo "  AWS App Runner Deployment - ATS Multi-Channel Chatbot         "
echo "================================================================"

# 1. Verify AWS Identity
echo -e "\n[1/6] Verifying AWS credentials..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ Authenticated as AWS Account: $ACCOUNT_ID (Region: $REGION)"

# 2. Create ECR Repo
echo -e "\n[2/6] Setting up Amazon ECR Repository..."
ECR_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME"
if ! aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$REGION" >/dev/null 2>&1; then
    aws ecr create-repository --repository-name "$REPO_NAME" --region "$REGION" --image-scanning-configuration scanOnPush=true >/dev/null
    echo "✅ Created ECR repository: $ECR_URI"
else
    echo "✅ ECR repository already exists: $ECR_URI"
fi

# 3. Create IAM Role for App Runner
echo -e "\n[3/6] Configuring IAM Role for App Runner..."
ROLE_NAME="AppRunnerECRAccessRole"
if ! aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
    TRUST_POLICY='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"build.apprunner.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
    aws iam create-role --role-name "$ROLE_NAME" --assume-role-policy-document "$TRUST_POLICY" >/dev/null
    aws iam attach-role-policy --role-name "$ROLE_NAME" --policy-arn "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess" >/dev/null
    echo "✅ Created IAM Role: $ROLE_NAME"
else
    echo "✅ IAM Role already exists: $ROLE_NAME"
fi

# 4. Build & Push Docker Image
echo -e "\n[4/6] Building and pushing Docker container image..."
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
docker build --platform linux/amd64 -t "$REPO_NAME:latest" .
docker tag "$REPO_NAME:latest" "$ECR_URI:latest"
docker push "$ECR_URI:latest"
echo "✅ Image successfully pushed to Amazon ECR."

# 5. Create or Update App Runner Service
echo -e "\n[5/6] Deploying to AWS App Runner..."
CONFIG_FILE=$(mktemp)
sed "s/<AWS_ACCOUNT_ID>/$ACCOUNT_ID/g; s/<AWS_REGION>/$REGION/g" aws/apprunner_service.json > "$CONFIG_FILE"

SERVICE_ARN=$(aws apprunner list-services --region "$REGION" --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn" --output text || true)

if [ -n "$SERVICE_ARN" ]; then
    echo "Existing service found. Triggering redeployment..."
    aws apprunner start-deployment --service-arn "$SERVICE_ARN" --region "$REGION" >/dev/null
else
    echo "Creating new App Runner service..."
    SERVICE_ARN=$(aws apprunner create-service --cli-input-json "file://$CONFIG_FILE" --region "$REGION" --query 'Service.ServiceArn' --output text)
fi
rm -f "$CONFIG_FILE"

# 6. Service URL Output
SERVICE_URL="https://$(aws apprunner describe-service --service-arn "$SERVICE_ARN" --region "$REGION" --query 'Service.ServiceUrl' --output text)"

echo "================================================================"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "================================================================"
echo "🔗 Web App & API URL: $SERVICE_URL"
echo "🔗 Health Endpoint  : $SERVICE_URL/health"
echo "🔗 WhatsApp Webhook : $SERVICE_URL/webhook/whatsapp"
echo "🔗 Slack Webhook    : $SERVICE_URL/webhook/slack"
echo "🔗 Instagram Webhook: $SERVICE_URL/webhook/instagram"
echo "================================================================"
