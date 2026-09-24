import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define Google API Scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_gspread_client():
    """Authenticates and returns the gspread client using Service Account credentials."""
    credentials_path = os.getenv(
        "GOOGLE_CREDENTIALS_PATH", "credentials/google_service_account.json")

    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            f"❌ Missing credentials file at path: {credentials_path}")

    creds = Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client


def fetch_form_responses():
    """
    Fetches all rows from the target Google Sheet.
    Returns a list of dictionaries representing form submissions.
    """
    sheet_name = os.getenv("GOOGLE_SHEET_NAME")
    if not sheet_name:
        raise ValueError("❌ Missing GOOGLE_SHEET_NAME in .env file.")

    try:
        client = get_gspread_client()
        sheet = client.open(sheet_name).sheet1

        # Get all records as list of dicts (uses row 1 as header keys)
        records = sheet.get_all_records()
        return records

    except Exception as e:
        print(f"❌ Error fetching responses from Google Sheet: {e}")
        return []


# Self-testing block
if __name__ == "__main__":
    print("📊 Testing Google Sheets API Integration...\n")
    responses = fetch_form_responses()

    print(f"✅ Total Form Responses Found: {len(responses)}\n")
    for idx, resp in enumerate(responses, start=1):
        print(f"--- Submission #{idx} ---")
        for key, value in resp.items():
            print(f"  • {key}: {value}")
        print("-" * 35)
