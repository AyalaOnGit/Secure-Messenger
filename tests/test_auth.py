"""
test_auth.py — Authentication tests (register + login).
"""

from .conftest import register_and_login, auth


class TestAuthentication:

    def test_register_success(self, client):
        response = client.post("/register", json={"username": "alice", "password": "secret123"})
        assert response.status_code == 201

    def test_register_duplicate_username(self, client):
        client.post("/register", json={"username": "alice", "password": "secret123"})
        response = client.post("/register", json={"username": "alice", "password": "other-password"})
        assert response.status_code == 400

    def test_register_password_too_short(self, client):
        response = client.post("/register", json={"username": "alice", "password": "abc"})
        assert response.status_code == 422

    def test_login_success(self, client):
        client.post("/register", json={"username": "alice", "password": "secret123"})
        response = client.post("/login", json={"username": "alice", "password": "secret123"})
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client):
        client.post("/register", json={"username": "alice", "password": "secret123"})
        response = client.post("/login", json={"username": "alice", "password": "wrongpassword"})
        assert response.status_code == 401

    def test_login_unknown_user(self, client):
        response = client.post("/login", json={"username": "ghost", "password": "secret123"})
        assert response.status_code == 401

    def test_messages_require_token(self, client):
        response = client.get("/messages")
        assert response.status_code in (401, 403)

    def test_messages_reject_bad_token(self, client):
        response = client.get("/messages", headers={"Authorization": "Bearer fake-token"})
        assert response.status_code == 401

    def test_messages_accept_valid_token(self, client):
        token = register_and_login(client)
        response = client.get("/messages", headers=auth(token))
        assert response.status_code == 200
