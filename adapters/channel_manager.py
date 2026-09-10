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
        self.evaluated_candidates: list[Dict[str, Any]] = []
        self.pending_resumes: list[Dict[str, Any]] = []
        self.batch_jds: list[str] = []
        self.last_activity = time.time()

    def reset(self):
        self.state = "IDLE"
        self.current_jd = ""
        self.role_hint = ""
        self.current_resume = ""
        self.candidate_hint = ""
        self.last_analysis = None
        self.evaluated_candidates = []
        self.pending_resumes = []
        self.batch_jds = []
        self.last_activity = time.time()


def is_greeting(text: str) -> bool:
    """Detect any conversational greeting or polite query."""
    clean = text.strip().lower()
    clean_no_punc = re.sub(r'[^\w\s]', '', clean)
    words = clean_no_punc.split()
    if not words:
        return False
    if len(words) > 20 or len(clean) > 160:
        return False

    first_word = words[0]
    greeting_words = {
        "hi", "hello", "helo", "hey", "hy", "hola", "howdy", "yo", "sup",
        "greetings", "namaste", "bonjour", "welcome", "gm", "ge"
    }
    if first_word in greeting_words:
        return True

    multi_greetings = [
        "good morning", "good afternoon", "good evening", "good day",
        "hi there", "hello there", "hey there", "hello bot", "hi bot",
        "how are you", "who are you", "what can you do", "can you help"
    ]
    for g in multi_greetings:
        if clean_no_punc.startswith(g):
            return True
    return False


def classify_document_or_text(text: str, filename: str = "") -> str:
    """
    Classify whether input is a 'JD' (Job Description) or 'RESUME'.
    Returns 'JD', 'RESUME', or 'UNKNOWN'.
    """
    fn_lower = filename.lower() if filename else ""
    text_lower = text.lower()

    # 1. Strong Filename Signals
    jd_filename_words = ["jd", "job_description", "job-description", "jobdescription", "job", "role", "vacancy", "position", "posting", "spec"]
    resume_filename_words = ["resume", "cv", "curriculum", "vitae", "profile", "candidate", "applicant", "bio"]

    base_name = re.sub(r'[\W_]+', ' ', fn_lower).split()
    for word in base_name:
        if word in jd_filename_words:
            return "JD"
        if word in resume_filename_words:
            return "RESUME"

    if re.search(r'(?:^|[\W_])jd(?:[\W_]|$)', fn_lower):
        return "JD"
    if re.search(r'(?:^|[\W_])(?:cv|resume)(?:[\W_]|$)', fn_lower):
        return "RESUME"

    # 2. Strong Text Header Signals
    if re.search(r'^(?:#+\s*)?(?:jd\b|job\s+description|about\s+the\s+job|role\s+overview|job\s+title|position\s+summary)\b', text_lower, re.M):
        return "JD"
    if re.search(r'^(?:#+\s*)?(?:curriculum\s+vitae|resume\b|profile\b)', text_lower, re.M):
        return "RESUME"

    # 3. Keyword scoring
    jd_score = 0
    resume_score = 0

    jd_keywords = [
        "responsibilities", "requirements", "we are looking for", "what you'll do",
        "what you will do", "qualifications", "preferred qualifications", "minimum qualifications",
        "job summary", "about the role", "job description", "hiring", "job requirements",
        "who you are", "equal opportunity employer", "competitive salary"
    ]
    resume_keywords = [
        "education", "work experience", "employment history", "professional experience",
        "bachelor", "master", "university", "college", "gpa", "cgpa",
        "curriculum vitae", "contact information", "projects",
        "technical skills", "certifications", "achievements", "summary of qualifications"
    ]

    for kw in jd_keywords:
        if kw in text_lower:
            jd_score += 1
    for kw in resume_keywords:
        if kw in text_lower:
            resume_score += 1

    if jd_score > resume_score and jd_score >= 1:
        return "JD"
    elif resume_score > jd_score and resume_score >= 1:
        return "RESUME"

    return "UNKNOWN"


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

        filename = ""
        candidate_fallback = ""
        if attachments and len(attachments) > 0:
            att = attachments[0]
            if isinstance(att, dict):
                filename = att.get("filename", "")
                candidate_fallback = att.get("candidate_name", "")

        # Handle Commands & Greetings
        if is_greeting(text_clean) or text_lower in ["/start", "start", "/helo", "/hello"]:
            if session.current_jd and not session.current_resume:
                return {
                    "reply_text": (
                        f"👋 Hello! I have recognized the Job Description for <b>{session.role_hint}</b>.\n\n"
                        "📄 <b>Next Step:</b> Please upload or send the <b>Candidate's Resume</b> (.pdf / .docx or text) to evaluate ATS match!\n\n"
                        "💡 <i>Type <b>reset</b> anytime to start fresh.</i>"
                    ),
                    "state": session.state
                }
            elif session.current_resume and not session.current_jd:
                return {
                    "reply_text": (
                        f"👋 Hello! I have recognized the Resume for <b>{session.candidate_hint or 'Candidate'}</b>.\n\n"
                        "📋 <b>Next Step:</b> Please upload or send the <b>Job Description (JD)</b> (.pdf / .docx or text) to evaluate ATS match!\n\n"
                        "💡 <i>Type <b>reset</b> anytime to start fresh.</i>"
                    ),
                    "state": session.state
                }
            else:
                session.reset()
                return {
                    "reply_text": (
                        "👋 <b>Welcome to ATS Optimization & Tracking Assistant!</b>\n\n"
                        "I evaluate your resume against Job Descriptions, calculate precise ATS match scores, "
                        "think aloud through skills & experience alignment, and provide targeted upskilling course links.\n\n"
                        "<b>How to use:</b>\n"
                        "1️⃣ Upload or send your <b>Job Description (JD)</b> (.docx, .pdf, or text)\n"
                        "2️⃣ Upload or send your <b>Resume</b> (.docx, .pdf, or text)\n\n"
                        "<i>(You can upload them in either order — I will automatically recognize each!)</i>\n\n"
                        "💡 <b>Basic Commands:</b>\n"
                        "• <b>helo</b> - Show this welcome guide\n"
                        "• <b>example</b> - Load sample Data Analyst JD\n"
                        "• <b>courses</b> - Recommended upskilling courses\n"
                        "• <b>reset</b> - Clear session & start fresh"
                    ),
                    "state": session.state,
                    "quick_replies": ["Try Example: Data Analyst", "Try Example: Software Dev", "Courses"]
                }

        if text_lower in ["/reset", "reset", "start over", "clear", "/clear"]:
            session.reset()
            return {
                "reply_text": "🔄 <b>Session reset!</b> Please upload or paste a <b>Job Description (JD)</b> or <b>Resume</b> to begin a new ATS evaluation.",
                "state": "IDLE"
            }

        # Quick Example Triggers
        if "data analyst" in text_lower and ("example" in text_lower or len(text_clean) < 40):
            session.current_jd = "JD for Senior Data Analyst: Requirements: 3+ years experience in Python for data analysis, SQL, Power BI, Tableau, ETL pipelines, and statistical modeling."
            session.role_hint = "Senior Data Analyst"
            if session.current_resume:
                analysis = self.analyzer.analyze(
                    jd_text=session.current_jd,
                    resume_text=session.current_resume,
                    role_hint=session.role_hint,
                    candidate_hint=session.candidate_hint,
                    filename=filename
                )
                session.last_analysis = analysis
                session.state = "ANALYZED"
                return {
                    "reply_text": self._format_chat_response(analysis),
                    "structured_data": analysis,
                    "state": session.state
                }
            session.state = "WAITING_FOR_RESUME"
            return {
                "reply_text": (
                    "✅ Loaded <b>JD for Senior Data Analyst</b>.\n\n"
                    "📄 <b>Step 2:</b> Now upload your <b>Resume PDF / Word file</b> or paste resume text."
                ),
                "state": session.state
            }

        if "software" in text_lower and ("example" in text_lower or len(text_clean) < 40):
            session.current_jd = "JD for Software Developer: Requirements: 4+ years experience in Python, FastAPI, React, Advanced Algorithms, Full Stack Development, Docker, CI/CD."
            session.role_hint = "Software Developer"
            if session.current_resume:
                analysis = self.analyzer.analyze(
                    jd_text=session.current_jd,
                    resume_text=session.current_resume,
                    role_hint=session.role_hint,
                    candidate_hint=session.candidate_hint,
                    filename=filename
                )
                session.last_analysis = analysis
                session.state = "ANALYZED"
                return {
                    "reply_text": self._format_chat_response(analysis),
                    "structured_data": analysis,
                    "state": session.state
                }
            session.state = "WAITING_FOR_RESUME"
            return {
                "reply_text": (
                    "✅ Loaded <b>JD for Software Developer</b>.\n\n"
                    "📄 <b>Step 2:</b> Now upload your <b>Resume PDF / Word file</b> or paste resume text."
                ),
                "state": session.state
            }

        # Direct one-shot input check (e.g., "JD for ..., Resume of ...")
        if re.search(r'jd\s+(?:for|:)', text_clean, re.IGNORECASE) and re.search(r'resume\s+(?:of|for|:)', text_clean, re.IGNORECASE):
            parts = re.split(r'resume\s+(?:of|for|:)', text_clean, flags=re.IGNORECASE)
            jd_part = parts[0]
            resume_part = parts[1] if len(parts) > 1 else ""
            analysis = self.analyzer.analyze(
                jd_text=jd_part,
                resume_text=resume_part,
                candidate_hint=candidate_fallback,
                filename=filename
            )
            session.current_jd = jd_part
            session.current_resume = resume_part
            session.role_hint = analysis.get("target_role", "")
            session.candidate_hint = analysis.get("candidate_name", "")
            session.last_analysis = analysis
            session.state = "ANALYZED"
            return {
                "reply_text": self._format_chat_response(analysis),
                "structured_data": analysis,
                "state": session.state
            }

        # Classify the document or text individually
        doc_type = classify_document_or_text(text_clean, filename)

        # 1. Input is a JOB DESCRIPTION
        if doc_type == "JD" or (doc_type == "UNKNOWN" and session.state == "WAITING_FOR_JD"):
            session.current_jd = text_clean
            session.role_hint = self.analyzer._extract_role_title(text_clean, filename=filename)

            # If user sent resumes first before this JD (single or batch)
            if getattr(session, "pending_resumes", None) and len(session.pending_resumes) > 0:
                pending = list(session.pending_resumes)
                session.pending_resumes = []
                session.evaluated_candidates = []
                batch_results = []
                for p in pending:
                    c_name = self.analyzer._extract_candidate_name(p["text"], filename=p.get("filename", ""))
                    if c_name == "Candidate" and p.get("candidate_fallback"):
                        c_name = p["candidate_fallback"]
                    analysis = self.analyzer.analyze(
                        jd_text=session.current_jd,
                        resume_text=p["text"],
                        role_hint=session.role_hint,
                        candidate_hint=c_name,
                        filename=p.get("filename", "")
                    )
                    session.evaluated_candidates.append(analysis)
                    batch_results.append(analysis)
                session.last_analysis = batch_results[-1]
                session.state = "ANALYZED"
                return {
                    "reply_text": self._format_batch_chat_response(session.role_hint, batch_results, session.evaluated_candidates),
                    "structured_batch": {
                        "target_role": session.role_hint,
                        "results": batch_results,
                        "leaderboard": session.evaluated_candidates
                    },
                    "state": session.state
                }
            elif session.current_resume and not session.evaluated_candidates:
                analysis = self.analyzer.analyze(
                    jd_text=session.current_jd,
                    resume_text=session.current_resume,
                    role_hint=session.role_hint,
                    candidate_hint=session.candidate_hint,
                    filename=filename
                )
                session.last_analysis = analysis
                session.evaluated_candidates.append(analysis)
                analysis["leaderboard"] = session.evaluated_candidates
                session.state = "ANALYZED"
                return {
                    "reply_text": self._format_chat_response(analysis),
                    "structured_data": analysis,
                    "state": session.state
                }
            else:
                # Setting a new JD clears previous candidate leaderboard
                session.current_resume = ""
                session.evaluated_candidates = []
                session.state = "WAITING_FOR_RESUME"
                fn_str = f" (<code>{filename}</code>)" if filename else ""
                return {
                    "reply_text": (
                        f"📋 <b>Job Description Received & Recognized!</b>{fn_str}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💼 <b>Target Role:</b> {session.role_hint}\n\n"
                        f"👉 <b>Step 2:</b> Now upload or send <b>Candidate Resumes</b> (.pdf / .docx or text) to evaluate against this JD!\n\n"
                        f"💡 <i>Tip: You can select and send multiple resumes at once, or upload a .zip archive!</i>"
                    ),
                    "state": session.state
                }

        # 2. Input is a RESUME (or any subsequent document for active JD)
        elif doc_type == "RESUME" or (session.current_jd and session.state in ["WAITING_FOR_RESUME", "ANALYZED"]):
            session.current_resume = text_clean
            cand_name = self.analyzer._extract_candidate_name(text_clean, filename=filename)
            if cand_name == "Candidate" and candidate_fallback:
                cand_name = candidate_fallback
            session.candidate_hint = cand_name

            # Evaluate against current active JD
            if session.current_jd:
                analysis = self.analyzer.analyze(
                    jd_text=session.current_jd,
                    resume_text=session.current_resume,
                    role_hint=session.role_hint,
                    candidate_hint=session.candidate_hint,
                    filename=filename
                )
                session.last_analysis = analysis
                session.evaluated_candidates.append(analysis)
                analysis["leaderboard"] = session.evaluated_candidates
                session.state = "ANALYZED"
                return {
                    "reply_text": self._format_chat_response(analysis),
                    "structured_data": analysis,
                    "state": session.state
                }
            else:
                session.state = "WAITING_FOR_JD"
                if not hasattr(session, "pending_resumes"):
                    session.pending_resumes = []
                session.pending_resumes.append({
                    "filename": filename,
                    "text": text_clean,
                    "candidate_fallback": candidate_fallback
                })
                fn_str = f" (<code>{filename}</code>)" if filename else ""
                count_str = f" ({len(session.pending_resumes)} pending)" if len(session.pending_resumes) > 1 else ""
                return {
                    "reply_text": (
                        f"📄 <b>Resume Received & Recognized!</b>{fn_str}{count_str}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 <b>Candidate:</b> {session.candidate_hint}\n\n"
                        f"👉 <b>Step 2:</b> Now upload or send the <b>Job Description (JD)</b> (.pdf / .docx or text) to evaluate ATS match!"
                    ),
                    "state": session.state
                }

        # 3. Handle post-analysis shortcuts if in ANALYZED state and not sending new document/text
        if session.state == "ANALYZED" and len(text_clean) < 30 and not filename:
            if "another" in text_lower or "new" in text_lower or "next" in text_lower:
                session.reset()
                return {
                    "reply_text": "📄 Please send the next <b>Job Description</b> or upload a <b>Resume</b> to begin another analysis.",
                    "state": "IDLE"
                }
            elif "course" in text_lower or "link" in text_lower:
                courses = session.last_analysis.get("suggested_courses", [])
                course_lines = [f"• <b>{c['title']}</b> ({c['provider']}) - {c['url']}" for c in courses]
                return {
                    "reply_text": "🎓 <b>Recommended Upskilling Course Direct Links:</b>\n\n" + "\n\n".join(course_lines),
                    "state": session.state
                }

        # 4. Default fallback: treat as Job Description
        session.current_jd = text_clean
        session.role_hint = self.analyzer._extract_role_title(text_clean, filename=filename)
        session.state = "WAITING_FOR_RESUME"
        return {
            "reply_text": (
                f"✅ <b>Job Description Received</b> (Detected Role: <i>{session.role_hint}</i>)\n\n"
                f"📄 <b>Step 2:</b> Please upload the <b>Candidate's Resume</b> (.pdf / .docx) or paste the resume text to analyze against this JD."
            ),
            "state": session.state
        }

    def _format_chat_response(self, analysis: Dict[str, Any]) -> str:
        """Format the analysis into the exact specified format with clean chat readability."""
        ta = analysis["think_aloud"]
        courses_str = analysis["suggested_courses_str"]
        overall = analysis["overall_analytics"]["full_text"]
        score = analysis["ats_score"]
        skills_match = analysis["breakdown"]["skills_match"]
        exp_match = analysis["breakdown"]["experience_match"]
        target_role = analysis.get("target_role", "Target Role")
        candidate_name = analysis.get("candidate_name", "Candidate")

        # Visual gauge
        filled = int(round((score / 100) * 10))
        bar = "█" * filled + "░" * (10 - filled)

        header_section = (
            f"👤 *Candidate:* {candidate_name}\n"
            f"💼 *Role:* {target_role}\n"
            f"🎯 *ATS Score:* {score}% `[{bar}]`\n\n"
        )

        think_aloud_section = (
            f"🧠 *Think-Aloud Evaluation:*\n"
            f"• *Role Analysis:* {ta['title_analysis']}\n"
            f"• *Skills Match:* {ta['skills_match']}\n"
            f"• *Experience Match:* {ta['experience_match']}\n"
            f"• *Improvement Strategy:* {ta['areas_for_improvement']}\n\n"
        )

        standard_output = (
            f"📊 *Breakdown:* [Skills match: {skills_match}%, Experience match: {exp_match}%]\n"
            f"🎓 *Suggested Courses:* {courses_str}\n"
            f"📈 *Overall Analytics:* [{overall}]"
        )

        # Leaderboard if multiple resumes analyzed for this JD
        leaderboard_section = ""
        candidates = analysis.get("leaderboard", [])
        if len(candidates) > 1:
            lb_lines = []
            for idx, c in enumerate(sorted(candidates, key=lambda x: x.get("ats_score", 0), reverse=True), start=1):
                c_name = c.get("candidate_name", f"Candidate {idx}")
                c_score = c.get("ats_score", 0)
                badge = "🟢" if c_score >= 80 else "🟡" if c_score >= 60 else "🔴"
                lb_lines.append(f"{idx}. {badge} *{c_name}*: `{c_score}%`")
            leaderboard_section = f"\n\n🏆 *Candidates Ranked for {target_role} ({len(candidates)} total):*\n" + "\n".join(lb_lines)

        return header_section + think_aloud_section + standard_output + leaderboard_section

    def handle_batch_documents(self, user_id: str, channel: str, documents: list[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process multiple documents uploaded simultaneously (e.g. multi-file select or unpacked .zip).
        Each dict in documents: {"filename": str, "text": str, "candidate_fallback": str}
        """
        session = self.get_or_create_session(user_id, channel)
        valid_docs = [
            d for d in documents
            if d.get("text") and len(d["text"].strip()) > 15 and not d["text"].startswith("[Error")
        ]

        if not valid_docs:
            return {
                "reply_text": "⚠️ None of the uploaded files contained readable resume or job description text.",
                "state": session.state
            }

        # If only 1 document was uploaded in the batch, route to standard single handle_message
        if len(valid_docs) == 1:
            d = valid_docs[0]
            return self.handle_message(
                user_id=user_id,
                channel=channel,
                text=d["text"],
                attachments=[{"filename": d.get("filename", ""), "candidate_name": d.get("candidate_fallback", "")}]
            )

        # 1. Separate JDs and Resumes
        jds = []
        resumes = []
        for d in valid_docs:
            dtype = classify_document_or_text(d["text"], d.get("filename", ""))
            if dtype == "JD":
                jds.append(d)
            else:
                resumes.append(d)

        # 2. Determine target JD
        if jds:
            primary_jd = jds[0]
            session.current_jd = primary_jd["text"]
            session.role_hint = self.analyzer._extract_role_title(primary_jd["text"], filename=primary_jd.get("filename", ""))
            session.evaluated_candidates = []  # Start fresh ranking for this new JD

        elif not session.current_jd:
            # Resumes received, but no JD yet! Queue them up
            session.pending_resumes.extend(resumes)
            session.state = "WAITING_FOR_JD"
            count = len(session.pending_resumes)
            return {
                "reply_text": (
                    f"📥 <b>Received {count} Candidate Resumes!</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"I have successfully extracted all {count} resumes.\n\n"
                    f"👉 <b>Next Step:</b> Please upload or send the <b>Job Description (JD)</b> (.pdf / .docx or text) to evaluate all {count} candidates at once!"
                ),
                "state": session.state
            }

        # 3. Evaluate all candidate resumes against session.current_jd
        all_resumes = resumes + list(getattr(session, "pending_resumes", []))
        session.pending_resumes = []

        batch_results = []
        for r in all_resumes:
            c_name = self.analyzer._extract_candidate_name(r["text"], filename=r.get("filename", ""))
            if c_name == "Candidate" and r.get("candidate_fallback"):
                c_name = r["candidate_fallback"]

            analysis = self.analyzer.analyze(
                jd_text=session.current_jd,
                resume_text=r["text"],
                role_hint=session.role_hint,
                candidate_hint=c_name,
                filename=r.get("filename", "")
            )
            session.evaluated_candidates.append(analysis)
            batch_results.append(analysis)

        session.last_analysis = batch_results[-1] if batch_results else None
        session.state = "ANALYZED"

        return {
            "reply_text": self._format_batch_chat_response(session.role_hint, batch_results, session.evaluated_candidates),
            "structured_batch": {
                "target_role": session.role_hint,
                "results": batch_results,
                "leaderboard": session.evaluated_candidates
            },
            "state": session.state
        }

    def _format_batch_chat_response(self, role: str, batch_results: list[Dict[str, Any]], leaderboard: list[Dict[str, Any]]) -> str:
        """Format batch candidate ATS evaluation report for standard text/markdown chat."""
        sorted_lb = sorted(leaderboard, key=lambda x: x.get("ats_score", 0), reverse=True)
        total = len(sorted_lb)

        lines = [
            f"🏆 *Batch ATS Evaluation Report: {role}*",
            "━━━━━━━━━━━━━━━━━━━━",
            f"📊 Evaluated *{total} candidates* for this role.\n",
            "🏅 *Ranked Candidate Leaderboard:*"
        ]

        for rank, c in enumerate(sorted_lb, start=1):
            name = c.get("candidate_name") or f"Candidate {rank}"
            score = c.get("ats_score", 0)
            breakdown = c.get("breakdown", {})
            sm = breakdown.get("skills_match", score)
            em = breakdown.get("experience_match", score)
            badge = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
            lines.append(f"{rank}. {badge} *{name}*: `{score}%` (Skills: {sm}%, Exp: {em}%)")

        if sorted_lb:
            top = sorted_lb[0]
            lines.append(f"\n🌟 *Top Match:* *{top.get('candidate_name')}* ({top.get('ats_score')}% compatibility)")

        lines.append("\n💡 _Send another resume or archive to add candidates, or type *reset* to start over._")
        return "\n".join(lines)


# Global singleton instance
channel_manager = ChannelManager()
