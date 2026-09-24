import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD_NAME = os.getenv("TRELLO_BOARD_NAME", "RequestFlow Operations")

BASE_URL = "https://api.trello.com/1"


def get_auth_params():
    """Returns standard auth query parameters for Trello API."""
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        raise ValueError(
            "❌ Missing TRELLO_API_KEY or TRELLO_TOKEN in .env file.")
    return {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }


def get_board_id_by_name(board_name: str) -> str:
    """Finds and returns Trello Board ID matching the provided name."""
    url = f"{BASE_URL}/members/me/boards"
    params = get_auth_params()

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        boards = response.json()

        for board in boards:
            if board.get("name").strip().lower() == board_name.strip().lower():
                return board.get("id")

        print(
            f"⚠️ Board '{board_name}' not found. Available boards: {[b['name'] for b in boards]}")
        return None
    except Exception as e:
        print(f"❌ Error fetching Trello boards: {e}")
        return None


def get_board_lists(board_id: str) -> dict:
    """Fetches all lists for a given board ID and returns a dict mapping list names to IDs."""
    url = f"{BASE_URL}/boards/{board_id}/lists"
    params = get_auth_params()

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        lists = response.json()

        # Return dict mapping name lowercased to list id
        return {l.get("name").strip().lower(): l.get("id") for l in lists}
    except Exception as e:
        print(f"❌ Error fetching Trello board lists: {e}")
        return {}


def create_trello_card(user_name: str, user_email: str, category: str, urgency: str, summary: str, details: str) -> dict:
    """
    Creates a new Trello card in the appropriate category list.
    Returns a dict with card_id and short_url.
    """
    board_id = get_board_id_by_name(TRELLO_BOARD_NAME)
    if not board_id:
        raise ValueError(
            f"❌ Could not locate Trello board named '{TRELLO_BOARD_NAME}'.")

    lists_map = get_board_lists(board_id)

    # Target list matching category (default to general if not found)
    target_list_key = category.strip().lower()
    list_id = lists_map.get(target_list_key) or lists_map.get(
        "general") or list(lists_map.values())[0]

    urgency_emoji = "🔴" if urgency == "High" else (
        "🟡" if urgency == "Medium" else "🟢")
    card_title = f"{urgency_emoji} [{urgency.upper()}] {summary[:60]}"

    card_description = (
        f"**User Info:** {user_name} ({user_email})\n"
        f"**Category:** {category}\n"
        f"**Urgency:** {urgency}\n\n"
        f"**Full Request Details:**\n{details}"
    )

    url = f"{BASE_URL}/cards"
    params = get_auth_params()
    params.update({
        "idList": list_id,
        "name": card_title,
        "desc": card_description,
        "pos": "top"  # Put at top of the list
    })

    try:
        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status()
        card_data = response.json()

        print(f"✅ Trello card created successfully in list '{category}'!")
        return {
            "card_id": card_data.get("id"),
            "url": card_data.get("shortUrl")
        }
    except Exception as e:
        print(f"❌ Error creating Trello card: {e}")
        return {"card_id": None, "url": ""}


# Self-testing script
if __name__ == "__main__":
    print("📋 Testing Trello API Handler Module...\n")

    result = create_trello_card(
        user_name="Nima Test",
        user_email="nima@example.com",
        category="Technical",
        urgency="High",
        summary="Payment Gateway Outage 500 Error",
        details="Our payment gateway is completely down and throwing HTTP 500 errors for all customers!"
    )

    print("\n--- Result ---")
    print(f"Card ID: {result.get('card_id')}")
    print(f"Card URL: {result.get('url')}")
