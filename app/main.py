from app.database import init_db, is_request_processed, mark_request_as_processed
from app.slack_notifier import send_slack_notification
from app.trello_handler import create_trello_card
from app.classifier import classify_request
from app.form_watcher import fetch_form_responses
import os
import sys
import time
import hashlib
from dotenv import load_dotenv

# Ensure root directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


load_dotenv()

# Check interval in seconds (default: 30 seconds)
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))


def generate_request_hash(timestamp: str, email: str, details: str) -> str:
    """Generates a unique MD5 hash for a form submission to prevent duplicates."""
    raw_str = f"{timestamp.strip()}_{email.strip().lower()}_{details.strip()}"
    return hashlib.md5(raw_str.encode("utf-8")).hexdigest()


def process_pending_requests():
    """Fetches form responses and processes only new, unhandled submissions."""
    print(
        f"\n⏰ [{time.strftime('%Y-%m-%d %H:%M:%S')}] Polling Google Sheet for new submissions...")

    responses = fetch_form_responses()
    if not responses:
        print("ℹ️ No submissions found in Google Sheet.")
        return

    new_requests_count = 0

    for idx, item in enumerate(responses, start=1):
        timestamp = str(item.get("Timestamp", ""))
        name = item.get("Full Name", "Anonymous")
        email = item.get("Email Address", "N/A")
        details = item.get("Request Details", "")

        if not details:
            continue

        req_hash = generate_request_hash(timestamp, email, details)

        # Skip if already processed in SQLite DB
        if is_request_processed(req_hash):
            continue

        new_requests_count += 1
        print(f"\n🔥 [NEW REQUEST DETECTED] Submission #{idx}")
        print(f"👤 User: {name} ({email})")
        print(f"💬 Details: \"{details}\"")

        # 1. AI Classification
        print("🤖 Step 1/3: Running AI Triage Engine...")
        analysis = classify_request(details)

        category = analysis.get("category", "General")
        urgency = analysis.get("urgency", "Low")
        summary = analysis.get("summary", details[:60])

        print(f"   • Category: {category}")
        print(f"   • Urgency: {urgency}")

        # 2. Trello Card Creation
        print("📋 Step 2/3: Creating Trello Card...")
        trello_res = create_trello_card(
            user_name=name,
            user_email=email,
            category=category,
            urgency=urgency,
            summary=summary,
            details=details
        )
        trello_url = trello_res.get("url", "")

        # 3. Slack Notification Alert
        print("📢 Step 3/3: Sending Slack Team Alert...")
        send_slack_notification(
            user_name=name,
            user_email=email,
            category=category,
            urgency=urgency,
            summary=summary,
            trello_url=trello_url
        )

        # 4. Mark as processed in Database
        mark_request_as_processed(
            request_hash=req_hash,
            user_name=name,
            user_email=email,
            category=category,
            urgency=urgency,
            trello_url=trello_url
        )
        print("💾 Marked request as processed in SQLite database.")

    if new_requests_count == 0:
        print(
            "ℹ️ All existing form responses are already processed. Waiting for new forms...")
    else:
        print(
            f"\n✅ Batch complete! Successfully processed {new_requests_count} new request(s).")


def start_autonomous_agent():
    """Starts the continuous background monitoring loop."""
    init_db()
    print("==================================================================")
    print("🚀 RequestFlow AI — Autonomous Ingestion Agent Active")
    print(
        f"⏱️ Monitoring Google Sheet every {POLL_INTERVAL_SECONDS} seconds...")
    print("==================================================================")

    try:
        while True:
            process_pending_requests()
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n🛑 RequestFlow AI Agent stopped by user. Exiting safely.")


if __name__ == "__main__":
    start_autonomous_agent()
