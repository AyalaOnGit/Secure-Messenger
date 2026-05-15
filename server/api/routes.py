"""
routes.py — HTTP route handlers (thin layer).
"""

import asyncio
import json

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..db.models import get_db
from ..schemas import RegisterRequest, LoginRequest, TokenResponse, SendMessageRequest, MessageResponse
from ..core.auth import require_auth
from ..core.broadcaster import broadcaster
from ..service import AuthService, MessageService


router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService(db).register(body.username, body.password)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login(body.username, body.password)


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    body: SendMessageRequest,
    db: Session = Depends(get_db),
    username: str = Depends(require_auth),
):
    response = MessageService(db).send(username, body.recipient, body.content)
    await broadcaster.publish(response.model_dump(mode="json"))
    return response


@router.get("/messages", response_model=list[MessageResponse])
def get_messages(
    db: Session = Depends(get_db),
    username: str = Depends(require_auth),
):
    return MessageService(db).get_for_user(username)


@router.get("/stream")
async def stream(
    db: Session = Depends(get_db),
    username: str = Depends(require_auth),
) -> StreamingResponse:
    async def event_generator():
        q = broadcaster.subscribe()
        try:
            while True:
                message = await q.get()
                if (
                    message["recipient"] is None or
                    message["sender"] == username or
                    message["recipient"] == username
                ):
                    yield f"data: {json.dumps(message)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            broadcaster.unsubscribe(q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
