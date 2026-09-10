"""
Unit tests for multi-channel webhook adapters (WhatsApp, Slack, Instagram).
"""

from adapters.whatsapp_adapter import WhatsAppAdapter
from adapters.slack_adapter import SlackAdapter
from adapters.instagram_adapter import InstagramAdapter
from adapters.channel_manager import channel_manager

def test_meta_whatsapp_verification():
    token = "ats_bot_verify_token_secret"
    res = WhatsAppAdapter.verify_webhook("subscribe", token, "123456789")
    assert res == "123456789"

    failed_res = WhatsAppAdapter.verify_webhook("subscribe", "wrong_token", "123456789")
    assert failed_res is None

def test_slack_url_verification():
    payload = {
        "type": "url_verification",
        "token": "slack_token",
        "challenge": "test_challenge_code_abc"
    }
    res = SlackAdapter.handle_events_payload(payload)
    assert res.get("challenge") == "test_challenge_code_abc"

def test_conversational_state_flow():
    user_id = "test_user_wa_99"
    # Step 1: Send JD
    r1 = channel_manager.handle_message(user_id, "whatsapp", "JD for Data Analyst: Python, SQL")
    assert "Job Description Received" in r1["reply_text"]
    assert r1["state"] == "WAITING_FOR_RESUME"

    # Step 2: Send Resume
    r2 = channel_manager.handle_message(user_id, "whatsapp", "Jane Smith Resume: 3 years Python, SQL")
    assert "ATS Score:" in r2["reply_text"]
    assert "Breakdown: [Skills match:" in r2["reply_text"]
    assert r2["state"] == "ANALYZED"
