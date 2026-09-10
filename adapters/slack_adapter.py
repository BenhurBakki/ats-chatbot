"""
Slack Adapter for Slack Bolt, Events API, and Slash Commands (/ats-check).
Formats responses with Slack Block Kit UI components.
"""

import os
import requests
from typing import Dict, Any, Optional
from adapters.channel_manager import channel_manager

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")

class SlackAdapter:
    """Adapter for Slack Bot & Slash Commands."""

    @staticmethod
    def handle_events_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Slack Events API payloads."""
        # 1. Slack URL Verification Challenge
        if payload.get("type") == "url_verification":
            return {"challenge": payload.get("challenge")}

        event = payload.get("event", {})
        event_type = event.get("type")
        user_id = event.get("user", "slack_user")
        channel_id = event.get("channel")
        text = event.get("text", "")

        # Avoid reacting to bot's own messages
        if event.get("bot_id"):
            return {"status": "ignored_bot_event"}

        if event_type in ["message", "app_mention"]:
            response = channel_manager.handle_message(
                user_id=user_id,
                channel="slack",
                text=text
            )

            blocks = SlackAdapter.build_slack_blocks(response)
            SlackAdapter.post_slack_message(channel_id, response["reply_text"], blocks)

            return {
                "status": "success",
                "reply_text": response["reply_text"],
                "blocks": blocks
            }

        return {"status": "unhandled_event"}

    @staticmethod
    def handle_slash_command(command_form: Dict[str, str]) -> Dict[str, Any]:
        """Handle Slack /ats-check slash commands."""
        user_id = command_form.get("user_id", "slack_user")
        text = command_form.get("text", "")

        response = channel_manager.handle_message(
            user_id=user_id,
            channel="slack",
            text=text if text else "hello"
        )

        blocks = SlackAdapter.build_slack_blocks(response)

        return {
            "response_type": "in_channel",
            "text": response["reply_text"],
            "blocks": blocks
        }

    @staticmethod
    def build_slack_blocks(response: Dict[str, Any]) -> list:
        """Construct Slack Block Kit UI."""
        data = response.get("structured_data")
        if not data:
            return [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": response.get("reply_text", "")}
                }
            ]

        score = data.get("ats_score", 0)
        skills_match = data.get("breakdown", {}).get("skills_match", 0)
        exp_match = data.get("breakdown", {}).get("experience_match", 0)
        role = data.get("target_role", "Target Role")
        courses = data.get("suggested_courses", [])
        overall = data.get("overall_analytics", {}).get("full_text", "")

        score_emoji = "🟢" if score >= 80 else ("🟡" if score >= 65 else "🔴")

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"📊 ATS Score Report: {role}", "emoji": True}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Overall Score:*\n{score_emoji} *{score}%*"},
                    {"type": "mrkdwn", "text": f"*Skills Match:*\n🎯 *{skills_match}%*"},
                    {"type": "mrkdwn", "text": f"*Experience Match:*\n⏳ *{exp_match}%*"},
                    {"type": "mrkdwn", "text": f"*Candidate:*\n👤 {data.get('candidate_name', 'Candidate')}"}
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🧠 Think-Aloud Evaluation:*\n{data.get('think_aloud', {}).get('skills_match', '')}\n{data.get('think_aloud', {}).get('experience_match', '')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📈 Overall Analytics:*\n{overall}"
                }
            }
        ]

        if courses:
            course_text = "\n".join([f"• <{c['url']}|*{c['title']}*> ({c['provider']})" for c in courses])
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*🎓 Recommended Upskilling Courses:*\n{course_text}"}
            })

        return blocks

    @staticmethod
    def post_slack_message(channel_id: str, text: str, blocks: list = None) -> bool:
        """Post message to Slack channel via Web API."""
        if not SLACK_BOT_TOKEN or not channel_id:
            return True

        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "channel": channel_id,
            "text": text,
            "blocks": blocks or []
        }
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=10)
            return r.status_code == 200
        except Exception:
            return False
