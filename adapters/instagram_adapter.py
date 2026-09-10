"""
Instagram Messaging Adapter for Meta Graph API.
Handles Instagram Direct Message webhooks and quick reply formatting.
"""

import os
import requests
from typing import Dict, Any, Optional
from adapters.channel_manager import channel_manager

INSTAGRAM_PAGE_ACCESS_TOKEN = os.getenv("INSTAGRAM_PAGE_ACCESS_TOKEN", "")
INSTAGRAM_VERIFY_TOKEN = os.getenv("INSTAGRAM_VERIFY_TOKEN", "ats_bot_verify_token_secret")

class InstagramAdapter:
    """Adapter for Instagram Messaging via Meta Graph API."""

    @staticmethod
    def verify_webhook(mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify Instagram webhook handshake."""
        if mode == "subscribe" and token == INSTAGRAM_VERIFY_TOKEN:
            return challenge
        return None

    @staticmethod
    def handle_webhook_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Instagram message payload."""
        try:
            entry = payload.get("entry", [])[0]
            messaging = entry.get("messaging", [])[0]
            sender_id = messaging.get("sender", {}).get("id")
            message = messaging.get("message", {})

            text = message.get("text", "")
            if not text or not sender_id:
                return {"status": "no_text_in_message"}

            response = channel_manager.handle_message(
                user_id=sender_id,
                channel="instagram",
                text=text
            )

            InstagramAdapter.send_instagram_message(sender_id, response["reply_text"])

            return {
                "status": "success",
                "recipient": sender_id,
                "reply": response["reply_text"],
                "structured_data": response.get("structured_data")
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def send_instagram_message(recipient_id: str, text: str) -> bool:
        """Send Direct Message back to Instagram user."""
        if not INSTAGRAM_PAGE_ACCESS_TOKEN:
            return True

        url = "https://graph.facebook.com/v19.0/me/messages"
        headers = {
            "Authorization": f"Bearer {INSTAGRAM_PAGE_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text}
        }
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=10)
            return r.status_code == 200
        except Exception:
            return False
