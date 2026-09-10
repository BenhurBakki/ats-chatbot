"""
Universal Multi-Channel Session and State Manager for ATS Chatbot.
Handles conversational state across WhatsApp, Instagram, Slack, and Web interfaces.
"""

import time
import re
from typing import Dict, Any, Optional
from core.ats_analyzer import ATSAnalyzer, BatchATSQueue

class UserSession:
    def __init__(self, user_id: str, channel: str):
        self.user_id = user_id
        self.channel = channel  # 'telegram', 'whatsapp', 'slack', 'instagram', 'web'
        self.state = "IDLE"     # IDLE, WAITING_FOR_JD, WAITING_FOR_RESUME, ANALYZED
        self.current_jd = ""
        self.role_hint = ""
        self.current_resume = ""
        self.candidate_hint = ""
        self.last_analysis: Optional[Dict[str, Any]] = None
        self.batch_jds: list[str] = []
        self.last_activity = time.time()

    def reset(self):
        self.state = "IDLE"
        self.current_jd = ""
        self.role_hint = ""
        self.current_resume = ""
        self.candidate_hint = ""
        self.last_analysis = None
        self.batch_jds = []
        self.last_activity = time.time()


class ChannelManager:
    """Manages conversations across all platforms with uniform messaging logic."""

    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}
        self.analyzer = ATSAnalyzer()
        self.batch_queue = BatchATSQueue()

    def get_or_create_session(self, user_id: str, channel: str) -> UserSession:
        session_key = f"{channel}:{user_id}"
        if session_key not in self.sessions:
            self.sessions[session_key] = UserSession(user_id, channel)
        self.sessions[session_key].last_activity = time.time()
        return self.sessions[session_key]

    def handle_message(self, user_id: str, channel: str, text: str, attachments: list = None) -> Dict[str, Any]:
        """
        Process incoming text or document attachment from any channel.
        Returns a dict with 'reply_text', 'structured_data', and 'channel_payload'.
        """
        session = self.get_or_create_session(user_id, channel)
        text_clean = text.strip()
        text_lower = text_clean.lower()

        # Handle Commands
        if text_lower in ["/reset", "reset", "start over", "clear", "hello", "hi", "hey"] and session.state == "IDLE":
            session.reset()
            return {
                "reply_text": (
                    "👋 *Welcome to ATS Optimization & Tracking Assistant!*\n\n"
                    "I evaluate your resume against Job Descriptions, calculate precise ATS match scores, "
                    "think aloud through skills & experience alignment, and provide targeted upskilling course links.\n\n"
                    "📄 *Step 1:* Please send or paste the *Job Description (JD)* (e.g. `JD for Data Analyst...` or raw JD text)."
                ),
                "state": session.state,
                "quick_replies": ["Try Example: Data Analyst", "Try Example: Software Dev", "Batch Mode"]
            }

        if text_lower in ["/reset", "reset", "start over", "clear"]:
            session.reset()
            return {
                "reply_text": "🔄 Session reset. Please send or paste a *Job Description (JD)* to begin a new ATS evaluation.",
                "state": "IDLE"
            }

        # Quick Example Triggers
        if "data analyst" in text_lower and ("example" in text_lower or len(text_clean) < 40):
            session.current_jd = "JD for Senior Data Analyst: Requirements: 3+ years experience in Python for data analysis, SQL, Power BI, Tableau, ETL pipelines, and statistical modeling."
            session.role_hint = "Data Analyst"
            session.state = "WAITING_FOR_RESUME"
            return {
                "reply_text": (
                    "✅ Loaded *JD for Data Analyst*.\n\n"
                    "📄 *Step 2:* Now send or paste the *Candidate's Resume* (e.g., Jane Smith's resume)."
                ),
                "state": session.state
            }

        if "software" in text_lower and ("example" in text_lower or len(text_clean) < 40):
            session.current_jd = "JD for Software Developer: Requirements: 4+ years experience in Python, FastAPI, React, Advanced Algorithms, Full Stack Development, Docker, CI/CD."
            session.role_hint = "Software Developer"
            session.state = "WAITING_FOR_RESUME"
            return {
                "reply_text": (
                    "✅ Loaded *JD for Software Developer*.\n\n"
                    "📄 *Step 2:* Now send or paste the *Candidate's Resume* (e.g., John Doe's resume)."
                ),
                "state": session.state
            }

        # Direct one-shot input check (e.g., "JD for ..., Resume of ...")
        if re.search(r'jd\s+(?:for|:)', text_clean, re.IGNORECASE) and re.search(r'resume\s+(?:of|for|:)', text_clean, re.IGNORECASE):
            parts = re.split(r'resume\s+(?:of|for|:)', text_clean, flags=re.IGNORECASE)
            jd_part = parts[0]
            resume_part = parts[1] if len(parts) > 1 else ""
            analysis = self.analyzer.analyze(jd_text=jd_part, resume_text=resume_part)
            session.last_analysis = analysis
            session.state = "ANALYZED"
            return {
                "reply_text": self._format_chat_response(analysis),
                "structured_data": analysis,
                "state": session.state
            }

        # Conversational Flow
        if session.state in ["IDLE", "WAITING_FOR_JD"]:
            session.current_jd = text_clean
            session.role_hint = self.analyzer._extract_role_title(text_clean)
            session.state = "WAITING_FOR_RESUME"
            return {
                "reply_text": (
                    f"✅ *Job Description Received* (Detected Role: _{session.role_hint}_)\n\n"
                    f"📄 *Step 2:* Please upload or paste the *Candidate's Resume* to analyze against this JD."
                ),
                "state": session.state
            }

        elif session.state == "WAITING_FOR_RESUME":
            session.current_resume = text_clean
            session.candidate_hint = self.analyzer._extract_candidate_name(text_clean)
            analysis = self.analyzer.analyze(
                jd_text=session.current_jd,
                resume_text=session.current_resume,
                role_hint=session.role_hint,
                candidate_hint=session.candidate_hint
            )
            session.last_analysis = analysis
            session.state = "ANALYZED"
            return {
                "reply_text": self._format_chat_response(analysis),
                "structured_data": analysis,
                "state": session.state
            }

        elif session.state == "ANALYZED":
            if "another" in text_lower or "new" in text_lower or "next" in text_lower:
                session.reset()
                return {
                    "reply_text": "📄 Please send the next *Job Description* to begin another analysis.",
                    "state": "IDLE"
                }
            elif "course" in text_lower or "link" in text_lower:
                courses = session.last_analysis.get("suggested_courses", [])
                course_lines = [f"• *{c['title']}* ({c['provider']}) - {c['url']}" for c in courses]
                return {
                    "reply_text": "🎓 *Recommended Upskilling Course Direct Links:*\n\n" + "\n\n".join(course_lines),
                    "state": session.state
                }
            else:
                return {
                    "reply_text": (
                        "💡 You can type:\n"
                        "• *'new'* to test another Job Description / Resume\n"
                        "• *'courses'* to get direct clickable links to recommended courses\n"
                        "• Send a new JD directly to start again!"
                    ),
                    "state": session.state
                }

        return {
            "reply_text": "Please provide a Job Description to get started.",
            "state": "IDLE"
        }

    def _format_chat_response(self, analysis: Dict[str, Any]) -> str:
        """Format the analysis into the exact specified format with clean chat readability."""
        ta = analysis["think_aloud"]
        courses_str = analysis["suggested_courses_str"]
        overall = analysis["overall_analytics"]["full_text"]
        score = analysis["ats_score"]
        skills_match = analysis["breakdown"]["skills_match"]
        exp_match = analysis["breakdown"]["experience_match"]

        # Exact required output format integrated with think-aloud
        think_aloud_section = (
            f"🧠 *Think-Aloud Evaluation:*\n"
            f"• *Role Analysis:* {ta['title_analysis']}\n"
            f"• *Skills Match:* {ta['skills_match']}\n"
            f"• *Experience Match:* {ta['experience_match']}\n"
            f"• *Improvement Strategy:* {ta['areas_for_improvement']}\n\n"
        )

        standard_output = (
            f"📊 *ATS Score:* {score}%, "
            f"Breakdown: [Skills match: {skills_match}%, Experience match: {exp_match}%]. "
            f"Suggested Courses: {courses_str}. "
            f"Overall Analytics: [{overall}]"
        )

        return think_aloud_section + standard_output


# Global singleton instance
channel_manager = ChannelManager()
