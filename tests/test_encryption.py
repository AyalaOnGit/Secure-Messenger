"""
test_encryption.py — Encryption tests (crypto layer + storage).
"""

import pytest
from server.core.crypto import encrypt, decrypt
from .conftest import register_and_login, auth, TestingSession


class TestEncryption:

    def test_encrypt_is_not_plain_text(self):
        assert encrypt("hello world") != "hello world"

    def test_decrypt_round_trip(self):
        original = "this is a secret message"
        assert decrypt(encrypt(original)) == original

    def test_same_message_encrypts_differently_each_time(self):
        assert encrypt("hello") != encrypt("hello")

    def test_tampered_ciphertext_raises(self):
        blob = encrypt("original")
        tampered = blob[:-4] + "XXXX"
        with pytest.raises(Exception):
            decrypt(tampered)

    def test_messages_are_stored_encrypted(self, client):
        from server.db.models import Message
        token = register_and_login(client)
        client.post("/messages", json={"content": "secret text", "recipient": "alice"}, headers=auth(token))
        db = TestingSession()
        row = db.query(Message).first()
        db.close()
        assert row.ciphertext != "secret text"
        assert decrypt(row.ciphertext) == "secret text"
