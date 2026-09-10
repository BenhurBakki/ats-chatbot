# 🚀 Step-by-Step Guide: Deploying to AWS Amplify

This guide walks you through deploying your **ATS Optimization & Multi-Channel Chatbot Portal** to **AWS Amplify Hosting** in 5 minutes.

---

## Step 1: Push Your Code to GitHub

### Option A: Using the Automated Script (PowerShell)
Open PowerShell in `d:\ATS` and run:
```powershell
.\push_to_github.ps1
```
Enter your GitHub repository URL (e.g. `https://github.com/your-username/ats-chatbot.git`) when prompted.

### Option B: Using Git CLI manually
```bash
# 1. Initialize git
git init
git branch -M main

# 2. Stage and commit
git add .
git commit -m "Deploy ATS Multi-Channel Portal to AWS Amplify"

# 3. Add your remote and push
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO_NAME>.git
git push -u origin main
```

---

## Step 2: Open AWS Amplify Console

1. Navigate to the [AWS Amplify Console](https://console.aws.amazon.com/amplify/).
2. In the top right, make sure your desired AWS region is selected (e.g., `us-east-1`, `ap-south-1`, `eu-west-1`).
3. Click **Create new app** (or **Deploy an app** -> **Host web app**).

---

## Step 3: Connect Your GitHub Repository

1. Choose **GitHub** as your Git provider and click **Next**.
2. If this is your first time, click **Authorize AWS Amplify** to grant AWS read access to your repositories.
3. In the repository dropdown, select your repository: `<YOUR_USERNAME>/ats-chatbot`.
4. In the branch dropdown, select `main`.
5. Click **Next**.

---

## Step 4: Confirm Build Settings (`amplify.yml`)

1. AWS Amplify will automatically detect [`amplify.yml`](file:///d:/ATS/amplify.yml) located in your repository root:
   ```yaml
   version: 1
   frontend:
     phases:
       build:
         commands:
           - echo "Preparing ATS Optimization & Multi-Channel Portal for AWS Amplify..."
     artifacts:
       baseDirectory: static
       files:
         - '**/*'
     cache:
       paths: []
   ```
2. **App Name:** You can keep the default or rename it to `ats-copilot-portal`.
3. Click **Next**.

---

## Step 5: Save and Deploy

1. Review the summary page and click **Save and deploy**.
2. AWS Amplify will start the automated CI/CD pipeline with 4 visual status stages:
   * 🟡 **Provision:** Allocates the AWS build environment.
   * 🟡 **Build:** Packages the `static/` directory assets.
   * 🟡 **Deploy:** Deploys assets across Amazon CloudFront global edge nodes with automatic HTTPS.
   * 🟢 **Verify:** Runs automated visual rendering tests on mobile and desktop viewports.

---

## Step 6: Access Your Live Application

1. When all stages turn **Green (✔)**, click on the live domain link under your branch name:
   * **`https://main.<app-id>.amplifyapp.com`**
2. Your **ATS Optimization & Multi-Channel Chatbot Portal** is now globally live with free managed SSL/TLS certificates!

---

## 🔄 Automatic Continuous Deployment (CI/CD)

Whenever you make any changes to your code in `d:\ATS`:
```bash
git add .
git commit -m "Update ATS features"
git push origin main
```
AWS Amplify will automatically detect the push, rebuild, and redeploy the live site within 60 seconds with zero downtime.
