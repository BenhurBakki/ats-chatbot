# ✈️ Telegram Bot Integration Guide — @BennhurBot

Your bot is registered on Telegram at: **[t.me/BennhurBot](https://t.me/BennhurBot)**

Token: `8777822180:AAH5NQouyLXOwYmmJb8ycneVqb_VrI32B9E`

---

## ⚡ 1. Instant Local Testing (Zero Cloud Setup Needed)

You can run your bot **right now** from your computer using long-polling. No public domain, no ngrok, and no port forwarding needed!

### Option A: 1-Click Windows Batch Script
Double-click `run_telegram.bat` or run in terminal:
```bat
run_telegram.bat
```

### Option B: PowerShell
```powershell
.\run_telegram.ps1
```

### Option C: Python Command
```bash
python telegram_bot_runner.py
```

You will see:
```text
🤖 ATS TELEGRAM BOT IS ONLINE: @BennhurBot
👉 Direct Link: https://t.me/BennhurBot
✨ Features: Text Chat, PDF/DOCX Resume Uploads, /courses, /example
```

Now open Telegram, open **`@BennhurBot`**, and type `/start`!

---

## 📱 How Users Interact with @BennhurBot

### 1. Welcome & Help
- Send `/start` — Welcomes the user, explains the 2-step evaluation flow, and provides quick action buttons.
- Send `/help` — Full list of commands and tips.
- Send `/reset` — Clears conversation and starts a fresh evaluation.
- Send `/courses` — Direct clickable links to top upskilling courses.
- Send `/example` — Automatically loads a sample Data Analyst JD to test instantly.

### 2. Full Two-Step ATS Evaluation
1. **Step 1 (Send Job Description):**
   Paste the JD text, for example:
   > `JD for Senior Data Analyst: Requirements: 3+ years experience in Python, SQL, Tableau, Power BI, statistical modeling.`
   
   The bot detects the role and replies:
   > `✅ Job Description Received (Detected Role: Senior Data Analyst)`
   > `📄 Step 2: Please upload or paste the Candidate's Resume to analyze against this JD.`

2. **Step 2 (Upload Resume PDF or Paste Text):**
   - **Upload a PDF / DOCX file:** You can drag and drop or attach your actual `Resume.pdf` file directly into the Telegram chat! The bot automatically downloads it, extracts text using `pypdf`, and parses it.
   - **OR paste resume text:** Paste plain text or summary.

3. **Instant AI Evaluation Response:**
   The bot replies with rich formatted output:
   - 🎯 **ATS Score:** composite 0-100% score
   - 📊 **Breakdown:** Skills match % and Experience match %
   - 🧠 **Think-Aloud Evaluation:**
     - Role Alignment
     - Skills Match analysis
     - Experience Match analysis
     - Strategy & Gaps
   - 🎓 **Suggested Courses:** Targeted courses for any missing skills
   - 📈 **Overall Analytics:** Summary strengths and improvement recommendations

---

## ☁️ 2. Cloud Webhook Setup (For AWS App Runner, Render, Railway)

When your backend is deployed to a cloud server with a public HTTPS URL (e.g. AWS App Runner or Render):

### Set the Webhook:
Run this curl command (or open in browser):
```bash
curl -F "url=https://<YOUR_APP_RUNNER_URL>/webhook/telegram" \
     https://api.telegram.org/bot8777822180:AAH5NQouyLXOwYmmJb8ycneVqb_VrI32B9E/setWebhook
```

Or use the built-in API endpoint on your deployed backend:
```bash
POST https://<YOUR_APP_RUNNER_URL>/api/telegram/set-webhook
Body (form): webhook_url=https://<YOUR_APP_RUNNER_URL>/webhook/telegram
```

### Check Webhook Status:
```bash
curl https://api.telegram.org/bot8777822180:AAH5NQouyLXOwYmmJb8ycneVqb_VrI32B9E/getWebhookInfo
```

### Switch back to Local Polling:
If you want to switch back to local polling, just delete the webhook:
```bash
curl https://api.telegram.org/bot8777822180:AAH5NQouyLXOwYmmJb8ycneVqb_VrI32B9E/deleteWebhook
```
*(Note: `telegram_bot_runner.py` automatically deletes the webhook on startup so polling works seamlessly!)*

---

## 🛠️ Bot Customization in BotFather

You can customize your bot's appearance anytime by chatting with [@BotFather](https://t.me/BotFather):

1. **Set Bot Description** (what users see before clicking Start):
   - Send `/setdescription` to @BotFather
   - Select `@BennhurBot`
   - Paste:
     > `AI-powered ATS Resume Optimizer. Send a Job Description and your Resume PDF to get instant ATS scores, gap analysis, think-aloud evaluation, and targeted upskilling course links.`

2. **Set About Section** (shown on profile):
   - Send `/setabouttext` to @BotFather
   - Select `@BennhurBot`
   - Paste:
     > `Instant ATS evaluation and skill matching powered by AI.`

3. **Set Profile Picture:**
   - Send `/setuserpic` to @BotFather
   - Select `@BennhurBot`
   - Upload your custom bot logo or avatar.

4. **Set Command Menu:**
   - Send `/setcommands` to @BotFather
   - Select `@BennhurBot`
   - Paste:
     ```text
     start - Start evaluation & see instructions
     example - Load sample Data Analyst JD
     courses - Recommended upskilling courses
     reset - Start a new evaluation session
     help - How to use the bot
     ```
