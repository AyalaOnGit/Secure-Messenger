"""
seed.py — Populate the database via the API.

Usage (server must be running first):
    python seed.py
"""

import httpx

BASE = "http://localhost:8000"

USERS = [
    ("alice",   "alice123"),
    ("bob",     "bob123"),
    ("charlie", "charlie123"),
]

MESSAGES = [
    ("alice",   "bob",     "Hey Bob, how are you?"),
    ("bob",     "alice",   "All good! You?"),
    ("alice",   "charlie", "Charlie, join the call at 3pm"),
    ("charlie", "alice",   "Sure, I'll be there!"),
    ("bob",     "charlie", "Don't forget the report"),
]


def main():
    tokens = {}

    for username, password in USERS:
        httpx.post(f"{BASE}/register", json={"username": username, "password": password})
        r = httpx.post(f"{BASE}/login", json={"username": username, "password": password})
        tokens[username] = r.json()["access_token"]
        print(f"  [+] {username}")

    print()

    for sender, recipient, content in MESSAGES:
        httpx.post(
            f"{BASE}/messages",
            json={"recipient": recipient, "content": content},
            headers={"Authorization": f"Bearer {tokens[sender]}"},
        )
        print(f"  [{sender} → {recipient}]: {content}")

    print("\nDone!")


if __name__ == "__main__":
    main()
