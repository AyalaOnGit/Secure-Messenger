# 🔐 Secure Messenger

A real-time, end-to-end encrypted messaging system built with **FastAPI**, **SSE**, and a **terminal client**.  
Messages are encrypted at rest using AES-256-GCM. Authentication is handled via JWT tokens.

---

## 📽️ Demo


<video src="assets\demo.mp4" autoplay loop muted playsinline width="100%">
</video>

> Two users chatting in real time from separate terminals — no browser, no frontend.

---

## ✨ Features

- 🔐 **End-to-end encryption** — AES-256-GCM, messages stored as ciphertext
- 🪪 **JWT authentication** — every request is verified
- ⚡ **Real-time messaging** — Server-Sent Events (SSE), no polling
- 📢 **Broadcast** — send to one person or everyone
- 💻 **Terminal client** — colorful CLI, works out of the box
- 🗄️ **Database migrations** — Alembic for schema evolution without data loss

---

## 🏗️ Project Structure

```
server/
  api/
    routes.py        # HTTP handlers (thin layer)
  core/
    auth.py          # JWT + bcrypt
    crypto.py        # AES-256-GCM encryption
    broadcaster.py   # SSE fan-out to all connected clients
  db/
    models.py        # SQLAlchemy ORM tables
    repository.py    # All DB queries
  schemas.py         # Pydantic request/response shapes
  service.py         # Business logic
  main.py            # App entry point

client/
  client.py          # Terminal chat client

tests/
  conftest.py        # Shared fixtures
  test_auth.py       # Authentication tests
  test_encryption.py # Encryption tests
  test_messaging.py  # Messaging tests
  test_sse.py        # Real-time SSE tests

scripts/
  seed.py            # Populate DB with test data

data/
  messenger.db       # SQLite database

migrations/          # Alembic migration scripts
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the server

```bash
uvicorn server.main:app --reload
```

### 3. Seed test data (optional)

```bash
python scripts/seed.py
```

Creates 3 users: **alice** / `alice123`, **bob** / `bob123`, **charlie** / `charlie123`

### 4. Run the client

```bash
python -m client.client
```

---

## 💬 Using the Client

```
╔══════════════════════════════╗
║     🔐 Secure Messenger      ║
╚══════════════════════════════╝
  1) Register
  2) Login
  Choose (1/2): 2
  Username: alice
  Password: alice123

  ── History ──────────────────────────
  💬 bob → you   Hey Alice!
  ─────────────────────────────────────
  ✓ Welcome, alice!
  recipient:message  │  all:message  │  quit
  ─────────────────────────────────────

  > bob:hello!          ← private message to bob
  > all:hey everyone!   ← broadcast to all users
  > quit
```

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/register` | ❌ | Register a new user |
| `POST` | `/login` | ❌ | Login, receive JWT token |
| `POST` | `/messages` | ✅ | Send a message |
| `GET` | `/messages` | ✅ | Get message history |
| `GET` | `/stream` | ✅ | SSE stream for real-time messages |

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔒 How Encryption Works

```
User types:  "Hello Bob"
                │
                ▼
     Server encrypts with AES-256-GCM
     ciphertext = "gAAAAABm5jZ9...WkZI3vA4="
                │
                ▼
     Stored in DB as ciphertext (never plain text)
                │
                ▼
     On read: server decrypts → returns plain text
```

Even if someone steals the database file, they see only unreadable ciphertext.

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

```
tests/test_auth.py::TestAuthentication::test_register_success        PASSED
tests/test_auth.py::TestAuthentication::test_login_success            PASSED
tests/test_encryption.py::TestEncryption::test_decrypt_round_trip     PASSED
tests/test_messaging.py::TestMessaging::test_send_message_success     PASSED
tests/test_sse.py::TestSSEStream::test_sse_stream_receives_broadcast  PASSED
...
23 passed in 12s
```

---

## 🗄️ Database Migrations (Alembic)

```bash
# Create initial migration
alembic revision --autogenerate -m "initial"
alembic upgrade head

# After changing a model
alembic revision --autogenerate -m "add_email_to_users"
alembic upgrade head

# Useful commands
alembic history    # show all migrations
alembic current    # show current DB version
alembic downgrade -1  # undo last migration
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | FastAPI |
| Real-time | Server-Sent Events (SSE) |
| Database | SQLite + SQLAlchemy |
| Migrations | Alembic |
| Encryption | AES-256-GCM (cryptography) |
| Authentication | JWT (python-jose) + bcrypt |
| HTTP client | httpx |
| Tests | pytest |
