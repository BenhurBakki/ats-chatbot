"""
WhatsApp Adapter for Meta WhatsApp Cloud API and Twilio WhatsApp.
Handles webhook verification handshakes, incoming messages, and reply dispatches.
"""

import os
import requests
from typing import Dict, Any, Optional
from adapters.channel_manager import channel_manager

META_WA_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
META_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
META_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "ats_bot_verify_token_secret")

class WhatsAppAdapter:
    """Adapter for WhatsApp Business / Meta Cloud API and Twilio."""

    @staticmethod
    def verify_webhook(mode: str, token: str, challenge: str) -> Optional[str]:
        """Handles Meta Cloud API webhook verification handshake."""
        if mode == "subscribe" and token == META_VERIFY_TOKEN:
            return challenge
        return None

    @staticmethod
    def handle_meta_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Parse incoming Meta WhatsApp Cloud API payload and dispatch response."""
        try:
            entry = payload.get("entry", [])[0]
            change = entry.get("changes", [])[0]
            value = change.get("value", {})
            messages = value.get("messages", [])

            if not messages:
                return {"status": "no_message"}

            msg = messages[0]
            from_phone = msg.get("from")
            msg_type = msg.get("type")

            text_content = ""
            if msg_type == "text":
                text_content = msg.get("text", {}).get("body", "")
            elif msg_type == "document":
                # When user sends PDF/DOCX file
                filename = msg.get("document", {}).get("filename", "Resume.pdf")
                text_content = f"Uploaded Resume Document ({filename})"

            if not text_content:
                return {"status": "unsupported_message_type"}

            # Process through unified channel manager
            response = channel_manager.handle_message(
                user_id=from_phone,
                channel="whatsapp",
                text=text_content
            )

            # Send back response via Meta Cloud API if token configured
            WhatsAppAdapter.send_meta_message(from_phone, response["reply_text"])

            return {
                "status": "success",
                "recipient": from_phone,
                "reply": response["reply_text"],
                "structured_data": response.get("structured_data")
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def send_meta_message(recipient_phone: str, text: str) -> bool:
        """Send WhatsApp message using Meta Graph API."""
        if not META_WA_TOKEN or not META_PHONE_ID:
            # Running in simulated mode
            return True

        url = f"https://graph.facebook.com/v19.0/{META_PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {META_WA_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_phone,
            "type": "text",
            "text": {"body": text}
        }
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=10)
            return r.status_code == 200
        except Exception:
            return False
