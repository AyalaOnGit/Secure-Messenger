"""
service.py — Business logic layer.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .core.auth import hash_password, verify_password, create_token
from .core.crypto import encrypt, decrypt
from .db.repository import UserRepository, MessageRepository
from .schemas import TokenResponse, MessageResponse


class AuthService:

    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def register(self, username: str, password: str) -> dict:
        if self.users.get_by_username(username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username already taken")
        self.users.create(username, hash_password(password))
        return {"message": "registered successfully"}

    def login(self, username: str, password: str) -> TokenResponse:
        user = self.users.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return TokenResponse(access_token=create_token(username))


class MessageService:

    def __init__(self, db: Session):
        self.messages = MessageRepository(db)

    def send(self, sender: str, recipient: str, content: str) -> MessageResponse:
        msg = self.messages.create(sender, recipient, encrypt(content))
        return MessageResponse(
            id=msg.id,
            sender=msg.sender,
            recipient=msg.recipient,
            content=content,
            created_at=msg.created_at,
        )

    def get_for_user(self, username: str) -> list[MessageResponse]:
        return [
            MessageResponse(
                id=m.id,
                sender=m.sender,
                recipient=m.recipient,
                content=decrypt(m.ciphertext),
                created_at=m.created_at,
            )
            for m in self.messages.get_for_user(username)
        ]
