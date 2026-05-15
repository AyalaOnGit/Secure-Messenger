"""
main.py — Application entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db.models import create_tables
from .api.routes import router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Secure Messenger",
    description="Authenticated, encrypted REST API with real-time SSE",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(router)
