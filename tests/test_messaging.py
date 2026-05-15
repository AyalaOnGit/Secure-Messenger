"""
test_messaging.py — Messaging tests (send + receive).
"""

from .conftest import register_and_login, auth


class TestMessaging:

    def test_send_message_success(self, client):
        alice_token = register_and_login(client, "alice", "secret123")
        register_and_login(client, "bob", "secret456")

        response = client.post(
            "/messages",
            json={"content": "hello bob", "recipient": "bob"},
            headers=auth(alice_token),
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "hello bob"
        assert data["sender"] == "alice"
        assert data["recipient"] == "bob"

    def test_get_messages_returns_decrypted(self, client):
        alice_token = register_and_login(client, "alice", "secret123")
        register_and_login(client, "bob", "secret456")

        client.post("/messages", json={"content": "hi bob", "recipient": "bob"}, headers=auth(alice_token))

        response = client.get("/messages", headers=auth(alice_token))
        assert response.status_code == 200
        messages = response.json()
        assert len(messages) >= 1
        assert messages[0]["content"] == "hi bob"

    def test_user_sees_only_their_messages(self, client):
        alice_token   = register_and_login(client, "alice",   "secret123")
        bob_token     = register_and_login(client, "bob",     "secret456")
        charlie_token = register_and_login(client, "charlie", "secret789")

        client.post("/messages", json={"content": "hi bob",             "recipient": "bob"}, headers=auth(alice_token))
        client.post("/messages", json={"content": "hi bob from charlie","recipient": "bob"}, headers=auth(charlie_token))

        alice_messages = client.get("/messages", headers=auth(alice_token)).json()
        bob_messages   = client.get("/messages", headers=auth(bob_token)).json()

        assert len(alice_messages) == 1
        assert alice_messages[0]["content"] == "hi bob"
        assert len(bob_messages) == 2
