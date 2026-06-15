import os
import sys

# default to a local SQLite file for a fast inner loop, but honour a
# pre-set DATABASE_URL (CI points this at a real Postgres)
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

# WeasyPrint needs pango/cairo via brew on macOS; set the library search path
# so cffi's dlopen() finds them when tests call the PDF endpoint.
if sys.platform == "darwin":
    os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib")

import pytest
from fastapi.testclient import TestClient

from app.database.session import Base, engine
from app.core.rate_limit import limiter
from app.main import app


@pytest.fixture(autouse=True)
def _fresh_database():
    Base.metadata.create_all(bind=engine)
    # reset rate-limit counters so they don't leak between tests
    limiter.reset()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def first_professional_id(client):
    def _get(headers):
        response = client.get("/professionals/", headers=headers)
        return response.json()[0]["id"]

    return _get


@pytest.fixture
def sent_emails(monkeypatch):
    captured = []

    def _fake_send_email(to, subject, body):
        captured.append({"to": to, "subject": subject, "body": body})
        return True

    monkeypatch.setattr("app.core.email.send_email", _fake_send_email)

    return captured


@pytest.fixture
def sent_whatsapps(monkeypatch):
    captured = []

    def _fake_send_whatsapp(to, message):
        captured.append({"to": to, "message": message})
        return True

    monkeypatch.setattr("app.core.whatsapp.send_whatsapp", _fake_send_whatsapp)

    return captured


@pytest.fixture
def auth_headers(client):
    def _create_user(email="user@test.com", password="senha123", cpf="52998224725"):
        client.post("/auth/register", json={
            "full_name": "Test User",
            "birth_date": "1990-01-01",
            "cpf": cpf,
            "phone": "11999999999",
            "email": email,
            "password": password,
        })

        response = client.post("/auth/login", data={
            "username": email,
            "password": password,
        })

        token = response.json()["access_token"]

        return {"Authorization": f"Bearer {token}"}

    return _create_user
