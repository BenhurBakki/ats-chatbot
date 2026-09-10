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

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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
    print(f"[*] ATS TELEGRAM BOT IS ONLINE: @{username}")
    print(f"[*] Direct Link: https://t.me/{username}")
    print("[*] Features: Text Chat, PDF/DOCX Resume Uploads, /courses, /example")
    print("=" * 60 + "\n", flush=True)

    # Clear any old webhook so long polling receives updates
    del_res = TelegramAdapter.delete_webhook()
    logger.info(f"Webhook state reset: {del_res.get('ok', False)}")

    offset = 0
    logger.info("Listening for incoming messages and documents from Telegram...")

    # Aggregator for multi-file batches uploaded at once (e.g. albums, multi-select, zip)
    pending_batches = {}  # chat_id -> {"user_info": dict, "docs": list, "last_time": float}
    BATCH_WAIT_SECONDS = 1.2

    while True:
        try:
            # If we have files waiting to be flushed, use short polling timeout
            poll_timeout = 1 if len(pending_batches) > 0 else 20
            payload = {"offset": offset, "timeout": poll_timeout, "allowed_updates": ["message", "edited_message"]}
            res = _telegram_api_call("getUpdates", payload, timeout=poll_timeout + 10)

            if res.get("ok"):
                updates = res.get("result", [])
                for u in updates:
                    update_id = u.get("update_id", 0)
                    offset = max(offset, update_id + 1)

                    msg = u.get("message") or u.get("edited_message") or {}
                    chat = msg.get("chat", {})
                    user = msg.get("from", {})
                    chat_id = chat.get("id")
                    if not chat_id:
                        continue

                    username = user.get("username", user.get("first_name", "User"))
                    doc = msg.get("document")
                    photo = msg.get("photo")
                    text = msg.get("text")

                    # Check for Document or Photo Attachment
                    if doc or photo:
                        if doc:
                            file_id = doc.get("file_id")
                            filename = doc.get("file_name", "Resume.pdf")
                        else:
                            file_id = photo[-1].get("file_id")
                            filename = "scan_resume.jpg"

                        logger.info(f"Received file upload from @{username} (chat_id: {chat_id}): {filename}")
                        TelegramAdapter.send_chat_action(chat_id, "upload_document")

                        if chat_id not in pending_batches:
                            pending_batches[chat_id] = {
                                "user_info": user,
                                "docs": [],
                                "last_time": time.time()
                            }
                        pending_batches[chat_id]["docs"].append({
                            "file_id": file_id,
                            "filename": filename
                        })
                        pending_batches[chat_id]["last_time"] = time.time()

                    # Text message / Command
                    elif text:
                        # Flush any pending files for this chat first
                        if chat_id in pending_batches:
                            b = pending_batches.pop(chat_id)
                            TelegramAdapter.handle_batch_update(chat_id, b["user_info"], b["docs"])

                        logger.info(f"Received message from @{username} (chat_id: {chat_id}): {text[:50]}...")
                        TelegramAdapter.handle_update(u)

            # Check for completed batches whose wait time has elapsed
            now = time.time()
            chats_to_flush = [
                cid for cid, b in pending_batches.items()
                if (now - b["last_time"]) >= BATCH_WAIT_SECONDS
            ]
            for cid in chats_to_flush:
                b = pending_batches.pop(cid)
                logger.info(f"Processing batch of {len(b['docs'])} file(s) for chat_id {cid}...")
                TelegramAdapter.handle_batch_update(cid, b["user_info"], b["docs"])

        except KeyboardInterrupt:
            logger.info("Telegram Bot stopped by user (Ctrl+C).")
            break
        except Exception as e:
            logger.error(f"Unexpected error in polling loop: {e}", exc_info=True)
            time.sleep(2)


if __name__ == "__main__":
    run_polling()
