"""
crypto.py — AES-256-GCM encryption for messages stored in the database.
"""

import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# Fixed key for development. In production: load from environment variable.
_KEY: bytes = bytes.fromhex("603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4")


def encrypt(plaintext: str) -> str:
    aesgcm = AESGCM(_KEY)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()


def decrypt(blob: str) -> str:
    raw = base64.b64decode(blob.encode())
    nonce, ciphertext = raw[:12], raw[12:]
    aesgcm = AESGCM(_KEY)
    return aesgcm.decrypt(nonce, ciphertext, None).decode()
