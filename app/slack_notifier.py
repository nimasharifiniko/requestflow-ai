import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_slack_notification(user_name: str, user_email: str, category: str, urgency: str, summary: str, trello_url: str) -> bool:
    """
    Sends a formatted alert message to Slack via Incoming Webhook.
    """
    if not SLACK_WEBHOOK_URL:
        print(
            "⚠️ Warning: SLACK_WEBHOOK_URL is missing in .env. Skipping Slack notification.")
        return False

    urgency_emoji = "🔴" if urgency == "High" else (
        "🟡" if urgency == "Medium" else "🟢")

    # Construct Slack Block Kit / Markdown message
    slack_payload = {
        "text": f"{urgency_emoji} New Support Request: [{category}] from {user_name}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{urgency_emoji} New {urgency.upper()} Urgency Request Detected",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*User:* {user_name}"},
                    {"type": "mrkdwn", "text": f"*Email:* {user_email}"},
                    {"type": "mrkdwn", "text": f"*Category:* `{category}`"},
                    {"type": "mrkdwn", "text": f"*Urgency:* `{urgency}`"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:* {summary}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📋 View Trello Card",
                            "emoji": True
                        },
                        "url": trello_url if trello_url else "https://trello.com",
                        "style": "primary" if urgency == "High" else "default"
                    }
                ]
            },
            {"type": "divider"}
        ]
    }

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps(slack_payload),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        print("✅ Slack alert notification sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Error sending Slack notification: {e}")
        return False


# Self-testing script
if __name__ == "__main__":
    print("📢 Testing Slack Notifier Module...\n")

    test_success = send_slack_notification(
        user_name="Nima Test",
        user_email="nima@example.com",
        category="Billing",
        urgency="High",
        summary="Payment gateway is down and throwing 500 errors!",
        trello_url="https://trello.com/c/hy1EmGzj"
    )

    print(f"\nNotification Status: {'SUCCESS' if test_success else 'FAILED'}")
