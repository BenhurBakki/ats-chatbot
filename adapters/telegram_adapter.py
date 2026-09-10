"""
Telegram Bot Adapter for ATS Optimization & Tracking Chatbot.
Handles updates from Telegram Bot API (both Webhook and Polling modes),
document parsing (PDF, DOCX, TXT), and rich HTML response dispatches.
"""

import os
import io
import json
import html
import ssl
import re
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

from adapters.channel_manager import channel_manager
from core.courses_db import COURSE_CATALOG

# Bot credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8777822180:AAH5NQouyLXOwYmmJb8ycneVqb_VrI32B9E")
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
TELEGRAM_FILE_BASE = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}"


_ssl_context_cache = None

def _get_ssl_context() -> ssl.SSLContext:
    """Create and cache SSL context that handles Windows / self-signed certificate chains reliably."""
    global _ssl_context_cache
    if _ssl_context_cache is not None:
        return _ssl_context_cache
    try:
        ctx = ssl.create_default_context()
        # Test basic connection; if system certs are missing, fallback to unverified
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        _ssl_context_cache = ctx
        return _ssl_context_cache
    except Exception:
        _ssl_context_cache = ssl._create_unverified_context()
        return _ssl_context_cache


def _telegram_api_call(method: str, payload: Optional[Dict[str, Any]] = None, timeout: int = 15) -> Dict[str, Any]:
    """Execute an HTTP POST or GET request to the Telegram Bot API with automatic SSL fallback."""
    url = f"{TELEGRAM_API_BASE}/{method}"
    headers = {"Content-Type": "application/json"}
    data_bytes = json.dumps(payload).encode("utf-8") if payload is not None else None

    ctx = _get_ssl_context()
    req = urllib.request.Request(url, data=data_bytes, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        try:
            return json.loads(body)
        except Exception:
            return {"ok": False, "description": f"HTTP {e.code}: {body}"}
    except (ssl.SSLError, urllib.error.URLError) as ssl_or_url_err:
        # Fallback to unverified SSL if cert chain or proxy causes verification failure
        try:
            unverified_ctx = ssl._create_unverified_context()
            req_retry = urllib.request.Request(url, data=data_bytes, headers=headers)
            with urllib.request.urlopen(req_retry, context=unverified_ctx, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as err:
            return {"ok": False, "description": str(err)}
    except Exception as err:
        return {"ok": False, "description": str(err)}


class TelegramAdapter:
    """Universal Telegram Bot Adapter for ATS Chatbot (@BennhurBot)."""

    @classmethod
    def send_chat_action(cls, chat_id: int, action: str = "typing") -> bool:
        """Send chat action (e.g. 'typing', 'upload_document')."""
        res = _telegram_api_call("sendChatAction", {"chat_id": chat_id, "action": action})
        return res.get("ok", False)

    @classmethod
    def send_message(
        cls,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML",
        reply_markup: Optional[Dict[str, Any]] = None,
        reply_to_message_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send message with HTML parse mode and fallback to plain text if syntax fails."""
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id

        res = _telegram_api_call("sendMessage", payload)
        if not res.get("ok") and parse_mode:
            # Fallback without parse_mode if formatting had unescaped characters
            payload.pop("parse_mode", None)
            res = _telegram_api_call("sendMessage", payload)
        return res

    @classmethod
    def get_file_info(cls, file_id: str) -> Optional[str]:
        """Retrieve Telegram file path for downloading."""
        res = _telegram_api_call("getFile", {"file_id": file_id})
        if res.get("ok"):
            return res.get("result", {}).get("file_path")
        return None

    @classmethod
    def download_file_bytes(cls, file_path: str) -> Optional[bytes]:
        """Download raw bytes of uploaded file from Telegram with automatic SSL fallback."""
        url = f"{TELEGRAM_FILE_BASE}/{file_path}"
        ctx = _get_ssl_context()
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                return resp.read()
        except (ssl.SSLError, urllib.error.URLError):
            try:
                unverified_ctx = ssl._create_unverified_context()
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, context=unverified_ctx, timeout=30) as resp:
                    return resp.read()
            except Exception:
                return None
        except Exception:
            return None

    @classmethod
    def extract_text_from_document(cls, filename: str, file_bytes: bytes) -> str:
        """Extract text from PDF, DOCX, or TXT file bytes."""
        lower_name = filename.lower()
        if lower_name.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                pages_text = [page.extract_text() or "" for page in reader.pages]
                return "\n".join(pages_text).strip()
            except Exception as e:
                return f"[Error parsing PDF: {e}]"

        elif lower_name.endswith(".docx") or lower_name.endswith(".doc"):
            try:
                import docx
                doc = docx.Document(io.BytesIO(file_bytes))
                paras = [p.text for p in doc.paragraphs if p.text]
                return "\n".join(paras).strip()
            except Exception as e:
                return f"[Error parsing Word Document: {e}]"

        else:
            try:
                return file_bytes.decode("utf-8", errors="ignore").strip()
            except Exception:
                return file_bytes.decode("latin-1", errors="ignore").strip()

    @classmethod
    def format_html_response(cls, analysis: Dict[str, Any]) -> str:
        """Format ATS evaluation results using clean, beautiful Telegram HTML tags."""
        score = analysis.get("ats_score", 0)
        breakdown = analysis.get("breakdown", {})
        skills_match = breakdown.get("skills_match", 0)
        exp_match = breakdown.get("experience_match", 0)
        courses_str = analysis.get("suggested_courses_str", "None")
        overall = analysis.get("overall_analytics", {}).get("full_text", "")
        ta = analysis.get("think_aloud", {})

        # Score badge indicator
        badge = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"

        title_analysis = html.escape(str(ta.get("title_analysis", "")))
        skills_analysis = html.escape(str(ta.get("skills_match", "")))
        exp_analysis = html.escape(str(ta.get("experience_match", "")))
        improvement = html.escape(str(ta.get("areas_for_improvement", "")))
        overall_escaped = html.escape(str(overall))
        courses_escaped = html.escape(str(courses_str))

        msg = (
            f"<b>{badge} ATS Evaluation Report</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 <b>ATS Score:</b> <code>{score}%</code>\n"
            f"📊 <b>Breakdown:</b> [Skills: <code>{skills_match}%</code>, Experience: <code>{exp_match}%</code>]\n\n"
            f"🧠 <b>Think-Aloud Evaluation:</b>\n"
            f"• <b>Role Alignment:</b> {title_analysis}\n"
            f"• <b>Skills Match:</b> {skills_analysis}\n"
            f"• <b>Experience Match:</b> {exp_analysis}\n"
            f"• <b>Strategy & Gaps:</b> {improvement}\n\n"
            f"🎓 <b>Suggested Courses:</b>\n{courses_escaped}\n\n"
            f"📈 <b>Overall Analytics:</b>\n<i>{overall_escaped}</i>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 <i>Type <b>courses</b> for direct links, <b>reset</b> to clear, or <b>helo</b> to start over!</i>"
        )
        return msg

    @classmethod
    def handle_update(cls, update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming Telegram update (Message, Document, or Command).
        Works identically for Webhook POST requests and Polling loop.
        """
        message = update.get("message") or update.get("edited_message")
        if not message:
            return {"ok": True, "status": "no_message"}

        chat = message.get("chat", {})
        chat_id = chat.get("id")
        if not chat_id:
            return {"ok": True, "status": "no_chat_id"}

        user_info = message.get("from", {})
        first_name = user_info.get("first_name", "Candidate")
        session_user_id = f"tg_{chat_id}"

        # 1. Check for Document / Resume Upload (PDF, Word, Text)
        document = message.get("document")
        if document:
            file_id = document.get("file_id")
            filename = document.get("file_name", "Resume.pdf")
            cls.send_chat_action(chat_id, "upload_document")

            file_path = cls.get_file_info(file_id)
            if not file_path:
                cls.send_message(
                    chat_id,
                    "⚠️ <i>Unable to download file from Telegram. Please try sending it again or paste the text directly.</i>"
                )
                return {"ok": True, "status": "file_fetch_error"}

            file_bytes = cls.download_file_bytes(file_path)
            if not file_bytes:
                cls.send_message(
                    chat_id,
                    "⚠️ <i>Could not read uploaded document data. Please ensure it is a valid PDF or DOCX file.</i>"
                )
                return {"ok": True, "status": "file_read_error"}

            # Extract text
            extracted_text = cls.extract_text_from_document(filename, file_bytes)
            if not extracted_text or len(extracted_text) < 20:
                cls.send_message(
                    chat_id,
                    f"⚠️ <i>Could not extract readable text from <b>{html.escape(filename)}</b>. Make sure it is not a scanned image PDF.</i>"
                )
                return {"ok": True, "status": "empty_extracted_text"}

            # Notify user that parsing succeeded
            cls.send_message(
                chat_id,
                f"📄 <b>Received:</b> <code>{html.escape(filename)}</code> ({len(extracted_text)} chars extracted).\n⚙️ <i>Analyzing ATS match against Job Description...</i>"
            )
            cls.send_chat_action(chat_id, "typing")

            # Feed extracted text as resume into session
            response = channel_manager.handle_message(
                user_id=session_user_id,
                channel="telegram",
                text=extracted_text
            )

            # If analysis was performed, format beautifully
            if response.get("structured_data"):
                reply_html = cls.format_html_response(response["structured_data"])
            else:
                reply_html = response.get("reply_text", "")

            cls.send_message(chat_id, reply_html)
            return {"ok": True, "status": "document_processed"}

        # 2. Text Message / Commands
        text = (message.get("text") or "").strip()
        if not text:
            return {"ok": True, "status": "empty_text"}

        text_lower = text.lower()

        # Command: helo, hello, /start, start, hi, hey
        if text_lower in ["helo", "hello", "hi", "hey", "/helo", "/hello", "/start", "start", "/hi"]:
            session = channel_manager.get_or_create_session(session_user_id, "telegram")
            session.reset()
            welcome = (
                f"👋 <b>Welcome {html.escape(first_name)} to BenBot (@BennhurBot)!</b>\n\n"
                f"I am your AI-powered <b>ATS Resume Optimizer & Skill Matcher</b>.\n\n"
                f"<b>How to use:</b>\n"
                f"1️⃣ Send or paste your <b>Job Description (JD)</b> (e.g. <i>'JD for Senior Data Analyst: 3+ years Python, SQL...'</i>)\n"
                f"2️⃣ Send your <b>Resume text</b> OR upload your <b>Resume PDF / DOCX file</b> directly into this chat!\n\n"
                f"I will instantly evaluate ATS match %, highlight gaps, think aloud on improvement strategies, and give direct links to recommended upskilling courses.\n\n"
                f"<b>Basic Commands:</b>\n"
                f"• <b>helo</b> - Show this welcome menu anytime\n"
                f"• <b>example</b> - Load sample Data Analyst JD to test immediately\n"
                f"• <b>courses</b> - Browse top upskilling courses\n"
                f"• <b>reset</b> - Clear session and start over\n"
                f"• <b>help</b> - Instructions & tips"
            )
            keyboard = {
                "keyboard": [
                    [{"text": "helo"}, {"text": "example"}],
                    [{"text": "courses"}, {"text": "reset"}]
                ],
                "resize_keyboard": True,
                "one_time_keyboard": False
            }
            cls.send_message(chat_id, welcome, reply_markup=keyboard)
            return {"ok": True, "status": "helo_sent"}

        # Command: /help or help
        if text_lower in ["/help", "help", "info", "/info"]:
            help_text = (
                "📖 <b>BenBot (@BennhurBot) Help & Basic Commands</b>\n\n"
                "• <b>helo:</b> Show welcome message & quick buttons\n"
                "• <b>example:</b> Load an instant sample JD to test\n"
                "• <b>courses:</b> View direct clickable links to recommended upskilling courses\n"
                "• <b>reset:</b> Reset session to evaluate another job description\n"
                "• <b>Send Job Description:</b> Just paste the text of the JD\n"
                "• <b>Send Resume:</b> Upload a <code>.pdf</code> / <code>.docx</code> document or paste resume text\n\n"
                "<i>Tip: You can also send both at once: 'JD for Data Analyst: ... Resume of Jane: ...'</i>"
            )
            cls.send_message(chat_id, help_text)
            return {"ok": True, "status": "help_sent"}

        # Command: /reset
        if text_lower in ["/reset", "reset", "clear"]:
            session = channel_manager.get_or_create_session(session_user_id, "telegram")
            session.reset()
            cls.send_message(
                chat_id,
                "🔄 <b>Session Reset!</b>\n\nPlease send or paste a new <b>Job Description (JD)</b> to begin."
            )
            return {"ok": True, "status": "session_reset"}

        # Command: /courses
        if text_lower in ["/courses", "courses"]:
            course_items = []
            for code, c in list(COURSE_CATALOG.items())[:8]:
                course_items.append(f"• <a href=\"{c['url']}\">{html.escape(c['title'])}</a> (<i>{html.escape(c['provider'])}</i>)")
            courses_msg = "🎓 <b>Top Recommended Upskilling Courses:</b>\n\n" + "\n".join(course_items)
            cls.send_message(chat_id, courses_msg)
            return {"ok": True, "status": "courses_sent"}

        # Command: /example
        if text_lower in ["/example", "example"]:
            text = "JD for Senior Data Analyst: Requirements: 3+ years experience in Python, SQL, Tableau, Power BI, ETL pipelines, statistical modeling."

        # Send typing action
        cls.send_chat_action(chat_id, "typing")

        # Process message via universal ChannelManager
        response = channel_manager.handle_message(
            user_id=session_user_id,
            channel="telegram",
            text=text
        )

        # Format output
        if response.get("structured_data"):
            reply_text = cls.format_html_response(response["structured_data"])
        else:
            raw_reply = response.get("reply_text", "")
            formatted = html.escape(raw_reply)
            formatted = formatted.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
            formatted = re.sub(r'\*([^*]+)\*', r'<b>\1</b>', formatted)
            formatted = re.sub(r'_([^_]+)_', r'<i>\1</i>', formatted)
            reply_text = formatted

        cls.send_message(chat_id, reply_text)
        return {"ok": True, "status": "message_handled"}

    @classmethod
    def set_webhook(cls, webhook_url: str) -> Dict[str, Any]:
        """Register public HTTPS webhook with Telegram."""
        return _telegram_api_call("setWebhook", {"url": webhook_url, "allowed_updates": ["message", "edited_message"]})

    @classmethod
    def delete_webhook(cls) -> Dict[str, Any]:
        """Remove registered webhook so polling can run."""
        return _telegram_api_call("deleteWebhook", {"drop_pending_updates": False})

    @classmethod
    def get_webhook_info(cls) -> Dict[str, Any]:
        """Inspect current webhook status."""
        return _telegram_api_call("getWebhookInfo")

    @classmethod
    def get_me(cls) -> Dict[str, Any]:
        """Test authentication and fetch bot profile."""
        return _telegram_api_call("getMe")
