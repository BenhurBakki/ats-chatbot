# 🚀 ATS Optimization & Multi-Channel Tracking Chatbot

An AI-powered ATS tracking and evaluation chatbot designed for hiring platforms and multi-channel messaging integrations (**WhatsApp**, **Instagram**, **Slack**, and **REST API**).

## ✨ Key Capabilities

1. **Precision ATS Scoring:** Calculates composite ATS match score (0-100%) with weighted breakdown (`[Skills match: X%, Experience match: Y%]`).
2. **Step-by-Step Think-Aloud Engine:** Explains role analysis, skill alignment, seniority fit, and tactical areas for improvement before outputting scorecards.
3. **Skill-Gap Course Recommendations:** Directly suggests targeted, certified upskilling courses with provider details (Coursera, edX, LinkedIn Learning, Microsoft, AWS).
4. **Batch Queue Processing:** Accepts and prioritizes multiple Job Descriptions and Resumes in the exact order received.
5. **Multi-Channel Webhook & Bot Adapters:**
   - ✈️ **Telegram:** Live bot at [t.me/BennhurBot](https://t.me/BennhurBot) with text chat, PDF/DOCX resume file uploads, and commands (`/start`, `/courses`, `/example`).
   - 🟢 **WhatsApp:** Meta Cloud API & Twilio with document upload support.
   - 🟣 **Slack:** Events API, Slash Command (`/ats-check`), and rich Block Kit UI scorecards.
   - 🟠 **Instagram:** Meta Graph API direct message handling with quick replies.
6. **Built-in Live Testing Console:** Modern responsive Web UI with PDF upload parser, ranked comparison table, batch queue, and interactive Channel Simulator.

---

## 🏃 Quick Start (Local Run)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the Web Application & API
python main.py

# 3. Run the Telegram Bot (@BennhurBot) in Live Polling Mode
python telegram_bot_runner.py
# Or on Windows, double click: run_telegram.bat
```
Open **`http://localhost:8000`** in your browser to access the Interactive Analyzer and Channel Simulator.
Or open **[t.me/BennhurBot](https://t.me/BennhurBot)** in Telegram to test live!

---

## 📦 Container Run (Docker)

```bash
docker-compose up --build
```

---

## ☁️ Cloud Deployment

Refer to [`DEPLOYMENT_GUIDE.md`](file:///d:/ATS/DEPLOYMENT_GUIDE.md) for 1-click deploy templates on **Render**, **Railway**, **AWS App Runner**, and **Google Cloud Run**.
