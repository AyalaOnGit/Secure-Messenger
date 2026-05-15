"""
client.py — CLI client for Secure Messenger.

Usage:
    python -m client.client

Sending:
    recipient:message     → private message
    all:message           → broadcast to everyone
"""

import json
import threading
import sys

import httpx

BASE_URL = "http://localhost:8000"

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
WHITE   = "\033[97m"

SEP = color = None  # defined below after color()


def color(text, *codes):
    return "".join(codes) + text + RESET


SEP = color("  " + "─" * 37, DIM)


def clear_line():
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()


def print_message(msg: dict, current_user: str):
    sender    = msg["sender"]
    recipient = msg.get("recipient")
    content   = msg["content"]

    if recipient is None:
        tag = color(f" 📢 {sender} → everyone ", BOLD, YELLOW)
    elif sender == current_user:
        tag = color(f" ➤ you → {recipient} ", BOLD, GREEN)
    else:
        tag = color(f" 💬 {sender} → you ", BOLD, CYAN)

    clear_line()
    print(f"  {tag}  {color(content, WHITE)}")


def prompt_auth() -> tuple[str, str]:
    print(color("\n╔══════════════════════════════╗", CYAN))
    print(color("║     🔐 Secure Messenger      ║", CYAN, BOLD))
    print(color("╚══════════════════════════════╝", CYAN))
    print(f"  {color('1)', YELLOW)} Register")
    print(f"  {color('2)', YELLOW)} Login")
    choice   = input(color("  Choose (1/2): ", DIM)).strip()
    username = input(color("  Username: ", DIM)).strip()
    password = input(color("  Password: ", DIM))

    endpoint = "/register" if choice == "1" else "/login"
    r = httpx.post(f"{BASE_URL}{endpoint}", json={"username": username, "password": password})

    if r.status_code not in (200, 201):
        print(color(f"\n  ✗ {r.json().get('detail', r.text)}", RED))
        return prompt_auth()

    if choice == "1":
        print(color("\n  ✓ Registered! Please login.", GREEN))
        return prompt_auth()

    return username, r.json()["access_token"]


def listen_for_messages(token: str, current_user: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    try:
        with httpx.stream("GET", f"{BASE_URL}/stream", headers=headers, timeout=None) as r:
            for line in r.iter_lines():
                if line.startswith("data:"):
                    data = line[len("data:"):].strip()
                    if not data:
                        continue
                    try:
                        msg = json.loads(data)
                        print_message(msg, current_user)
                        print(color("  > ", CYAN), end="", flush=True)
                    except json.JSONDecodeError:
                        pass
    except Exception:
        print(color("\n  [Connection lost]", RED))


def main():
    username, token = prompt_auth()
    headers = {"Authorization": f"Bearer {token}"}

    # Message history
    r = httpx.get(f"{BASE_URL}/messages", headers=headers)
    if r.status_code == 200 and r.json():
        print(color("\n  ── History ──────────────────────────", DIM))
        for msg in r.json():
            print_message(msg, username)

    # Separator + welcome + instructions
    print(f"\n{SEP}")
    print(color(f"  ✓ Welcome, {username}!", GREEN, BOLD))
    print(color("  recipient:message  │  all:message  │  quit", DIM))
    print(f"{SEP}\n")

    t = threading.Thread(target=listen_for_messages, args=(token, username), daemon=True)
    t.start()

    while True:
        try:
            line = input(color("  > ", CYAN)).strip()
        except (EOFError, KeyboardInterrupt):
            print(color("\n  Goodbye!", YELLOW))
            break

        if line.lower() == "quit":
            print(color("\n  Goodbye!", YELLOW))
            break

        if ":" not in line:
            print(color("  Format: recipient:message  or  all:message", DIM))
            continue

        target, _, content = line.partition(":")
        target  = target.strip()
        content = content.strip()

        payload = {"content": content}
        if target.lower() != "all":
            payload["recipient"] = target

        r = httpx.post(f"{BASE_URL}/messages", json=payload, headers=headers)
        if r.status_code != 201:
            detail = r.json().get("detail", r.text) if r.content else r.status_code
            print(color(f"  ✗ {detail}", RED))


if __name__ == "__main__":
    main()
