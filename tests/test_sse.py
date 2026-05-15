"""
test_sse.py — SSE stream tests.

These tests run against a real uvicorn server (live_server fixture from conftest.py)
because TestClient cannot handle concurrent streaming connections.
"""

import json
import queue
import threading
import time

import httpx


def _rl(username, password, base) -> str:
    """Register and login, return token."""
    httpx.post(f"{base}/register", json={"username": username, "password": password})
    r = httpx.post(f"{base}/login", json={"username": username, "password": password})
    return r.json()["access_token"]


def _bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestSSEStream:

    def test_stream_rejects_no_token(self, live_server):
        r = httpx.get(f"{live_server}/stream")
        assert r.status_code in (401, 403)

    def test_stream_rejects_bad_token(self, live_server):
        r = httpx.get(f"{live_server}/stream", headers={"Authorization": "Bearer bad-token"})
        assert r.status_code == 401

    def test_stream_accepts_valid_token(self, live_server):
        token = _rl("alice_sv", "secret123", live_server)
        with httpx.stream("GET", f"{live_server}/stream", headers=_bearer(token), timeout=3) as r:
            assert r.status_code == 200

    def test_sse_stream_receives_broadcast(self, live_server):
        token = _rl("alice_b", "secret123", live_server)
        received: queue.Queue = queue.Queue()

        def listen():
            with httpx.stream("GET", f"{live_server}/stream", headers=_bearer(token), timeout=10) as r:
                for line in r.iter_lines():
                    if line.startswith("data:"):
                        received.put(json.loads(line[len("data:"):].strip()))
                        return

        t = threading.Thread(target=listen, daemon=True)
        t.start()
        time.sleep(0.2)

        httpx.post(f"{live_server}/messages",
                   json={"content": "hello!", "recipient": "alice_b"},
                   headers=_bearer(token))

        t.join(timeout=5)
        msg = received.get(timeout=5)
        assert msg["content"] == "hello!"
        assert msg["sender"] == "alice_b"

    def test_only_relevant_messages_arrive(self, live_server):
        alice_token = _rl("alice_r", "secret123", live_server)
        bob_token   = _rl("bob_r",   "secret456", live_server)
        received: queue.Queue = queue.Queue()

        def listen():
            with httpx.stream("GET", f"{live_server}/stream", headers=_bearer(alice_token), timeout=10) as r:
                for line in r.iter_lines():
                    if line.startswith("data:"):
                        received.put(json.loads(line[len("data:"):].strip()))
                        return

        t = threading.Thread(target=listen, daemon=True)
        t.start()
        time.sleep(0.2)

        httpx.post(f"{live_server}/messages",
                   json={"content": "hi alice", "recipient": "alice_r"},
                   headers=_bearer(bob_token))

        t.join(timeout=5)
        msg = received.get(timeout=5)
        assert msg["sender"] == "bob_r"
        assert msg["recipient"] == "alice_r"

    def test_concurrent_clients_both_receive(self, live_server):
        alice_token = _rl("alice_c", "secret123", live_server)
        bob_token   = _rl("bob_c",   "secret456", live_server)
        alice_q: queue.Queue = queue.Queue()
        bob_q:   queue.Queue = queue.Queue()

        def listen(token, q):
            with httpx.stream("GET", f"{live_server}/stream", headers=_bearer(token), timeout=10) as r:
                for line in r.iter_lines():
                    if line.startswith("data:"):
                        q.put(json.loads(line[len("data:"):].strip()))
                        if q.qsize() >= 2:
                            return

        ta = threading.Thread(target=listen, args=(alice_token, alice_q), daemon=True)
        tb = threading.Thread(target=listen, args=(bob_token,   bob_q),   daemon=True)
        ta.start()
        tb.start()
        time.sleep(0.2)

        httpx.post(f"{live_server}/messages",
                   json={"content": "hey bob",   "recipient": "bob_c"},
                   headers=_bearer(alice_token))
        httpx.post(f"{live_server}/messages",
                   json={"content": "hey alice", "recipient": "alice_c"},
                   headers=_bearer(bob_token))

        ta.join(timeout=5)
        tb.join(timeout=5)
        bob_msgs   = [bob_q.get(timeout=5)   for _ in range(bob_q.qsize()   or 1)]
        alice_msgs = [alice_q.get(timeout=5) for _ in range(alice_q.qsize() or 1)]
        assert any(m["content"] == "hey bob"   for m in bob_msgs)
        assert any(m["content"] == "hey alice" for m in alice_msgs)
