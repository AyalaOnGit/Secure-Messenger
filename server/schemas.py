"""
schemas.py — Pydantic request/response shapes.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SendMessageRequest(BaseModel):
    content:   str = Field(min_length=1, max_length=2000)
    recipient: str | None = Field(default=None, min_length=3, max_length=50)


class MessageResponse(BaseModel):
    id:         int
    sender:     str
    recipient:  str | None
    content:    str
    created_at: datetime

    model_config = {"from_attributes": True}
