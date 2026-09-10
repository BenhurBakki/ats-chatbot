# Cloud Deployment & Multi-Channel Integration Guide

This guide walks you through deploying your **ATS Optimization & Tracking Chatbot** to the cloud and connecting it with **WhatsApp**, **Instagram**, and **Slack**.

---

## 1. Cloud Deployment Options

### Option A: 1-Click Deploy on Render (Recommended)
1. Push this repository to GitHub or GitLab.
2. Log into [Render.com](https://render.com) and click **New +** -> **Blueprint**.
3. Select your repository. Render will automatically detect [`render.yaml`](file:///d:/ATS/render.yaml) and configure the Python web service.
4. Set your environment variables in the Render Dashboard (or use defaults for testing).
5. Your service will be live at `https://your-app-name.onrender.com`.

### Option B: Deploy with Docker on Railway
1. Go to [Railway.app](https://railway.app) and create a **New Project** -> **Deploy from GitHub repo**.
2. Railway detects the [`Dockerfile`](file:///d:/ATS/Dockerfile) and automatically builds the container.
3. In **Settings -> Networking**, click **Generate Domain** (e.g., `https://ats-bot.up.railway.app`).

### Option C: Deploy to AWS (App Runner or Elastic Container Service)
```bash
# 1. Build the Docker image
docker build -t ats-multi-channel-chatbot .

# 2. Tag and push to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
docker tag ats-multi-channel-chatbot:latest <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/ats-bot:latest
docker push <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/ats-bot:latest

# 3. Create an AWS App Runner service pointing to your ECR image on port 8000.
```

### Option D: Deploy to Google Cloud Run
```bash
gcloud builds submit --tag gcr.io/<PROJECT_ID>/ats-chatbot
gcloud run deploy ats-chatbot --image gcr.io/<PROJECT_ID>/ats-chatbot --platform managed --port 8000 --allow-unauthenticated
```

---

## 2. WhatsApp Integration (Meta Cloud API)

1. Go to the [Meta for Developers Portal](https://developers.facebook.com/) and create/open your **Business App**.
2. Under **Products**, add **WhatsApp**.
3. Under **WhatsApp -> Configuration**:
   - **Callback URL:** `https://your-app-name.onrender.com/webhook/whatsapp`
   - **Verify Token:** `ats_bot_verify_token_secret` (or whatever you set in `WHATSAPP_VERIFY_TOKEN`).
   - Click **Verify and Save**.
4. In **Webhook fields**, click **Manage** and subscribe to:
   - `messages`
5. In your cloud server's environment variables, configure:
   - `WHATSAPP_TOKEN`: Permanent Meta System User Token or Temporary Token.
   - `WHATSAPP_PHONE_ID`: Your Test or Production WhatsApp Phone Number ID.

---

## 3. Slack Integration (Events API & Slash Commands)

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and click **Create New App** -> **From scratch**.
2. **Bot Permissions (OAuth & Permissions):**
   - Add the following Bot Token Scopes:
     - `chat:write`
     - `commands`
     - `im:history`
     - `app_mentions:read`
3. **Event Subscriptions:**
   - Turn On **Enable Events**.
   - **Request URL:** `https://your-app-name.onrender.com/webhook/slack` (Slack will verify the URL automatically).
   - Under **Subscribe to bot events**, add:
     - `app_mention`
     - `message.im`
4. **Slash Command:**
   - Go to **Slash Commands** -> **Create New Command**:
     - Command: `/ats-check`
     - Request URL: `https://your-app-name.onrender.com/webhook/slack/command`
     - Short Description: `Analyze Resume against Job Description with think-aloud ATS score`
5. Click **Install App to Workspace**, then copy:
   - `Bot User OAuth Token` (starts with `xoxb-`) -> set as `SLACK_BOT_TOKEN` in your environment.

---

## 4. Instagram Messaging Integration (Meta Graph API)

1. In your [Meta App Dashboard](https://developers.facebook.com/), add **Messenger** / **Instagram Graph API**.
2. Under **Instagram Settings**:
   - Connect your Instagram Professional / Creator account to your Facebook Page.
   - Generate an **Instagram Page Access Token** and set `INSTAGRAM_PAGE_ACCESS_TOKEN`.
3. Under **Webhooks -> Instagram**:
   - **Callback URL:** `https://your-app-name.onrender.com/webhook/instagram`
   - **Verify Token:** `ats_bot_verify_token_secret`
   - Subscribe to: `messages`, `messaging_postbacks`.

---

## 5. Direct REST API Usage

### Single Analysis:
```bash
curl -X POST "https://your-app-name.onrender.com/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "JD for Data Analyst: Requirements 3+ yrs SQL, Python, Power BI",
    "resume": "Resume of Jane Smith: 3.5 yrs Python, SQL, Tableau, Pandas"
  }'
```

### Standardized Response:
```json
{
  "target_role": "Data Analyst",
  "candidate_name": "Jane Smith",
  "ats_score": 78,
  "breakdown": {
    "skills_match": 85,
    "experience_match": 70
  },
  "suggested_courses_str": "Python for Data Science & Applied Analytics, SQL Basics",
  "formatted_output": "ATS Score: 78%, Breakdown: [Skills match: 85%, Experience match: 70%]. Suggested Courses: Python for Data Science & Applied Analytics, SQL Basics. Overall Analytics: [Strengths: Solid foundation in Python, SQL. Improvement Areas: Add quantitative ROI metrics]."
}
```
