"""
Telegram Bot Polling Runner for ATS Chatbot (@BennhurBot).
Runs long-polling so you can test and interact with @BennhurBot immediately
from your local computer without needing an HTTPS webhook or ngrok!
"""

import sys
import os
import time
import json
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adapters.telegram_adapter import (
    TelegramAdapter,
    _telegram_api_call,
    TELEGRAM_BOT_TOKEN
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("telegram_bot")


def run_polling():
    logger.info("Verifying Telegram Bot credentials...")
    bot_info = TelegramAdapter.get_me()
    if not bot_info.get("ok"):
        logger.error(f"Failed to authenticate with Telegram API: {bot_info}")
        logger.error("Please check your TELEGRAM_BOT_TOKEN in .env")
        return

    result = bot_info["result"]
    username = result.get("username", "UnknownBot")
    first_name = result.get("first_name", "Bot")
    logger.info(f"Authenticated as: {first_name} (@{username})")
    print("\n" + "=" * 60)
    print(f"🤖 ATS TELEGRAM BOT IS ONLINE: @{username}")
    print(f"👉 Direct Link: https://t.me/{username}")
    print("✨ Features: Text Chat, PDF/DOCX Resume Uploads, /courses, /example")
    print("=" * 60 + "\n")

    # Clear any old webhook so long polling receives updates
    del_res = TelegramAdapter.delete_webhook()
    logger.info(f"Webhook state reset: {del_res.get('ok', False)}")

    offset = 0
    logger.info("Listening for incoming messages and documents from Telegram...")

    while True:
        try:
            payload = {"offset": offset, "timeout": 20, "allowed_updates": ["message", "edited_message"]}
            res = _telegram_api_call("getUpdates", payload, timeout=30)

            if not res.get("ok"):
                logger.warning(f"getUpdates error: {res.get('description')}")
                time.sleep(3)
                continue

            updates = res.get("result", [])
            for u in updates:
                update_id = u.get("update_id", 0)
                offset = max(offset, update_id + 1)

                msg = u.get("message") or u.get("edited_message") or {}
                chat = msg.get("chat", {})
                user = msg.get("from", {})
                chat_id = chat.get("id")
                username = user.get("username", user.get("first_name", "User"))

                doc = msg.get("document")
                text = msg.get("text")

                if doc:
                    logger.info(f"Received file upload from @{username} (chat_id: {chat_id}): {doc.get('file_name')}")
                elif text:
                    logger.info(f"Received message from @{username} (chat_id: {chat_id}): {text[:50]}...")

                # Process update
                TelegramAdapter.handle_update(u)

        except KeyboardInterrupt:
            logger.info("Telegram Bot stopped by user (Ctrl+C).")
            break
        except Exception as e:
            logger.error(f"Unexpected error in polling loop: {e}", exc_info=True)
            time.sleep(3)


if __name__ == "__main__":
    run_polling()
