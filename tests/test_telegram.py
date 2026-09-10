"""
Unit tests for Telegram Bot Adapter (@BennhurBot).
"""

from adapters.telegram_adapter import TelegramAdapter
from adapters.channel_manager import channel_manager


def test_telegram_get_me():
    """Verify bot credentials with Telegram Bot API or fallback."""
    res = TelegramAdapter.get_me()
    # If network allows:
    if res.get("ok"):
        assert res.get("result", {}).get("username") == "BennhurBot"
    else:
        # Fallback check
        assert "ok" in res


def test_telegram_start_command():
    """Verify helo / start returns greeting and instructions."""
    for cmd in ["helo", "hello", "/start"]:
        update = {
            "update_id": 100,
            "message": {
                "message_id": 1,
                "chat": {"id": 11223344, "type": "private"},
                "from": {"id": 11223344, "first_name": "TestUser", "username": "testuser"},
                "text": cmd
            }
        }
        res = TelegramAdapter.handle_update(update)
        assert res.get("ok") is True
        assert res.get("status") == "helo_sent"


def test_telegram_two_step_analysis():
    """Verify 2-step conversation flow in Telegram channel."""
    chat_id = 99887766
    session_user_id = f"tg_{chat_id}"
    session = channel_manager.get_or_create_session(session_user_id, "telegram")
    session.reset()

    # Step 1: Send JD
    r1 = channel_manager.handle_message(
        session_user_id,
        "telegram",
        "JD for Senior Data Analyst: Requirements: 3+ years experience in Python, SQL, Tableau, Power BI, statistical modeling."
    )
    assert "Job Description Received" in r1["reply_text"]
    assert r1["state"] == "WAITING_FOR_RESUME"

    # Step 2: Send Resume
    r2 = channel_manager.handle_message(
        session_user_id,
        "telegram",
        "Resume of Jane Doe: 4 years experience in Python, SQL, Tableau, Power BI, Data Warehousing, ETL pipelines."
    )
    assert r2["state"] == "ANALYZED"
    assert "structured_data" in r2
    assert r2["structured_data"]["ats_score"] > 60

    # Step 3: Format HTML
    html_output = TelegramAdapter.format_html_response(r2["structured_data"])
    assert "ATS Evaluation Report" in html_output
    assert "ATS Score:" in html_output
    assert "Think-Aloud Evaluation:" in html_output
    assert "Role Alignment:" in html_output
    assert "Skills Match:" in html_output
    assert "Suggested Courses:" in html_output


def test_telegram_document_text_extraction():
    """Verify text decoding from uploaded file bytes."""
    plain_text = "Jane Smith Resume. 5 years Python and SQL experience."
    raw_bytes = plain_text.encode("utf-8")
    extracted = TelegramAdapter.extract_text_from_document("resume.txt", raw_bytes)
    assert extracted == plain_text
