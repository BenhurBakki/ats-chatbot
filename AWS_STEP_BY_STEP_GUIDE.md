# 🚀 Step-by-Step AWS Deployment Guide

This guide explains how to deploy the **ATS Multi-Channel Chatbot** to Amazon Web Services (AWS) using either the **Automated Script** or the **AWS Management Console (GUI)**.

---

## Method 1: Automated 1-Click Deployment (Recommended)

### Prerequisites:
1. **AWS CLI** installed and configured (`aws configure`).
2. **Docker Desktop** running.

### Execution:
Open PowerShell in `d:\ATS` and run:

```powershell
# 1. Run the automated deployment script
.\aws\deploy_apprunner.ps1 -Region "us-east-1"
```

The script will automatically:
1. Authenticate with your AWS account.
2. Create the private **Amazon ECR** repository.
3. Configure the **AppRunnerECRAccessRole** IAM role.
4. Build the multi-stage Docker container for Linux/AMD64.
5. Push the container image to Amazon ECR.
6. Deploy the service to **AWS App Runner** with automatic HTTPS and auto-scaling.
7. Print your live webhook endpoints.

---

## Method 2: AWS Management Console (Step-by-Step GUI)

If you prefer deploying via the AWS Web Console:

### Step 1: Create an Amazon ECR Repository
1. Log in to the [AWS Management Console](https://console.aws.amazon.com/).
2. Search for **Elastic Container Registry (ECR)**.
3. Click **Create repository**:
   - Visibility: **Private**
   - Repository name: `ats-multi-channel-chatbot`
   - Tag immutability: **Mutable**
   - Click **Create repository**.
4. Click on your newly created repository and click **View push commands** in the top right. Run those 4 commands in your terminal to push your Docker image to ECR.

---

### Step 2: Create an AWS App Runner Service
1. In the AWS Console, search for **App Runner**.
2. Click **Create service**.
3. **Source and deployment:**
   - Source: **Container registry**
   - Provider: **Amazon ECR**
   - Container image URI: Click **Browse** and select `ats-multi-channel-chatbot:latest`.
   - Deployment settings: Select **Automatic** (App Runner will redeploy automatically whenever you push a new image).
   - ECR access role: Choose **Create new service role** (or select `AppRunnerECRAccessRole`).
   - Click **Next**.

4. **Configure service:**
   - Service name: `ats-multi-channel-chatbot`
   - Virtual CPU (vCPU): **1 vCPU**
   - Memory: **2 GB**
   - **Environment variables:** (Add the following key-value pairs):
     - `PORT` = `8000`
     - `WHATSAPP_VERIFY_TOKEN` = `ats_bot_verify_token_secret`
     - `INSTAGRAM_VERIFY_TOKEN` = `ats_bot_verify_token_secret`
     - `WHATSAPP_TOKEN` = `<YOUR_META_TOKEN>` (optional for testing)
     - `SLACK_BOT_TOKEN` = `<YOUR_SLACK_TOKEN>` (optional for testing)

5. **Health check:**
   - Protocol: **HTTP**
   - Path: `/health`
   - Interval: `10` seconds
   - Timeout: `5` seconds
   - Healthy threshold: `1`
   - Unhealthy threshold: `5`

6. Click **Next** -> **Create & deploy**.
7. App Runner will take 2-3 minutes to provision the container, allocate a managed load balancer, and issue an SSL/TLS certificate.
8. Once status changes to **Running**, copy your **Default domain** (e.g. `https://abc123xyz.us-east-1.awsapprunner.com`).

---

## 🔗 Connecting Your Live AWS URL to Messaging Channels

Once you have your AWS App Runner URL (e.g. `https://abc123xyz.us-east-1.awsapprunner.com`), configure your webhooks:

### 1. WhatsApp (Meta Cloud API)
* Go to [Meta for Developers](https://developers.facebook.com/) -> Your App -> **WhatsApp** -> **Configuration**.
* **Callback URL:** `https://<YOUR_APP_RUNNER_URL>/webhook/whatsapp`
* **Verify Token:** `ats_bot_verify_token_secret`
* Subscribe to the `messages` webhook field.

### 2. Slack App (Events & Slash Commands)
* Go to [Slack API Dashboard](https://api.slack.com/apps) -> Your App -> **Event Subscriptions**.
* Turn ON Events and enter **Request URL:** `https://<YOUR_APP_RUNNER_URL>/webhook/slack`
* Go to **Slash Commands** -> Create `/ats-check` pointing to `https://<YOUR_APP_RUNNER_URL>/webhook/slack/command`.

### 3. Instagram Direct Messaging
* Go to Meta App Dashboard -> **Instagram** -> **Webhooks**.
* **Callback URL:** `https://<YOUR_APP_RUNNER_URL>/webhook/instagram`
* **Verify Token:** `ats_bot_verify_token_secret`
* Subscribe to `messages`.

---

## 🔍 Verifying the AWS Deployment

Run this command in terminal:
```bash
# Health check
curl -i https://<YOUR_APP_RUNNER_URL>/health

# Sample ATS Evaluation
curl -X POST https://<YOUR_APP_RUNNER_URL>/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"job_description": "JD for Data Analyst: SQL, Python", "resume": "Resume of Jane Smith: 3 yrs Python, SQL"}'
```
