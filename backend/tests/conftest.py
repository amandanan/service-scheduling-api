import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest
from fastapi.testclient import TestClient

from app.database.session import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def _fresh_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    def _create_user(email="user@test.com", password="senha123", cpf="00000000000"):
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
