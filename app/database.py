import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join("data", "processed_requests.db")


def get_connection():
    """Establish connection to SQLite database."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables for tracking processed form responses."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_hash TEXT UNIQUE NOT NULL,
                user_name TEXT,
                user_email TEXT,
                category TEXT,
                urgency TEXT,
                trello_card_url TEXT,
                processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    print("[Database] Processed requests table initialized.")


def is_request_processed(request_hash: str) -> bool:
    """Check if a specific request hash has already been processed."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM processed_requests WHERE request_hash = ?", (request_hash,))
        return cursor.fetchone() is not None


def mark_request_as_processed(request_hash: str, user_name: str, user_email: str, category: str, urgency: str, trello_url: str):
    """Mark a request hash as processed in SQLite database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO processed_requests (request_hash, user_name, user_email, category, urgency, trello_card_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (request_hash, user_name, user_email, category, urgency, trello_url))
        conn.commit()


def get_all_processed_records():
    """Fetch all processed request history."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM processed_requests ORDER BY processed_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# Self-testing block
if __name__ == "__main__":
    init_db()
    test_hash = "hash_test_12345"

    print(f"Is hash processed? {is_request_processed(test_hash)}")
    mark_request_as_processed(test_hash, "Nima Test", "nima@example.com",
                              "Billing", "High", "https://trello.com/c/test")
    print(f"Is hash processed after saving? {is_request_processed(test_hash)}")

    records = get_all_processed_records()
    print(f"📊 Total records in DB: {len(records)}")
