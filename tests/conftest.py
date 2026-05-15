"""
conftest.py — Shared pytest fixtures for all test files.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.main import app
from server.db.models import Base, get_db


TEST_DB_URL = "sqlite:///./data/test_messenger.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def live_server():
    """Start a real uvicorn server for SSE tests."""
    import socket, subprocess, sys, time, httpx

    with socket.socket() as s:
        s.bind(("", 0))
        port = s.getsockname()[1]

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server.main:app", "--port", str(port), "--log-level", "error"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    for _ in range(30):
        try:
            httpx.get(f"{base}/docs", timeout=0.5)
            break
        except Exception:
            time.sleep(0.2)

    yield base
    proc.terminate()
    proc.wait()


# ---------------------------------------------------------------------------
# Helpers (importable by all test files)
# ---------------------------------------------------------------------------

def register_and_login(client, username="alice", password="secret123") -> str:
    client.post("/register", json={"username": username, "password": password})
    response = client.post("/login", json={"username": username, "password": password})
    return response.json()["access_token"]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
