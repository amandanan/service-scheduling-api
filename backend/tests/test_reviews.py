from datetime import datetime, timedelta

from app.database.session import SessionLocal
from app.models.appointment import Appointment


def _setup_business_with_service(client):
    client.post("/auth/register", json={
        "full_name": "Studio Bella",
        "birth_date": "1990-01-01",
        "cpf": "11144477735",
        "phone": "11999999999",
        "email": "bella@test.com",
        "password": "senha123",
    })

    login = client.post("/auth/login", data={
        "username": "bella@test.com",
        "password": "senha123",
    })
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    service = client.post("/services/", json={
        "name": "Corte",
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers)

    me = client.get("/auth/me", headers=headers).json()
    slug = me["booking_slug"]
    professional_id = client.get(f"/public/{slug}/professionals").json()[0]["id"]

    return headers, slug, service.json()["id"], professional_id


def _book(client, slug, service_id, professional_id, when="2026-06-15T09:00:00"):
    response = client.post(f"/public/{slug}/appointments", json={
        "full_name": "Cliente Publico",
        "birth_date": "1995-05-05",
        "cpf": "16899555468",
        "phone": "11977777777",
        "email": "cliente@test.com",
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": when,
    })

    return response.json()


def _complete_appointment(token):
    db = SessionLocal()

    appointment = db.query(Appointment).filter(
        Appointment.public_token == token
    ).first()

    appointment.scheduled_at = datetime.now() - timedelta(days=1)

    db.commit()
    db.close()


def test_cannot_review_before_appointment_completes(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]

    response = client.post(f"/manage/{token}/review", json={
        "rating": 5,
        "comment": "Ótimo atendimento!",
    })

    assert response.status_code == 409


def test_can_review_completed_appointment(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]
    _complete_appointment(token)

    view = client.get(f"/manage/{token}").json()
    assert view["can_review"] is True
    assert view["review"] is None

    response = client.post(f"/manage/{token}/review", json={
        "rating": 5,
        "comment": "Ótimo atendimento!",
    })

    assert response.status_code == 200
    body = response.json()
    assert body["can_review"] is False
    assert body["review"]["rating"] == 5
    assert body["review"]["comment"] == "Ótimo atendimento!"


def test_cannot_review_twice(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]
    _complete_appointment(token)

    client.post(f"/manage/{token}/review", json={"rating": 4, "comment": "Bom"})

    response = client.post(f"/manage/{token}/review", json={
        "rating": 5,
        "comment": "Outra avaliação",
    })

    assert response.status_code == 409


def test_cannot_review_cancelled_appointment(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]
    _complete_appointment(token)

    client.post(f"/manage/{token}/cancel")

    response = client.post(f"/manage/{token}/review", json={
        "rating": 1,
        "comment": "Cancelado",
    })

    assert response.status_code == 409


def test_review_rating_must_be_in_range(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]
    _complete_appointment(token)

    response = client.post(f"/manage/{token}/review", json={
        "rating": 6,
        "comment": "Inválido",
    })

    assert response.status_code == 422


def test_public_reviews_aggregate(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)

    token_a = _book(client, slug, service_id, professional_id, when="2026-06-15T09:00:00")["public_token"]
    token_b = _book(client, slug, service_id, professional_id, when="2026-06-15T10:00:00")["public_token"]

    _complete_appointment(token_a)
    _complete_appointment(token_b)

    client.post(f"/manage/{token_a}/review", json={"rating": 5, "comment": "Excelente"})
    client.post(f"/manage/{token_b}/review", json={"rating": 3, "comment": "Ok"})

    response = client.get(f"/public/{slug}/reviews")

    assert response.status_code == 200
    body = response.json()
    assert body["total_reviews"] == 2
    assert body["average_rating"] == 4.0
    assert len(body["reviews"]) == 2


def test_public_reviews_empty(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)

    response = client.get(f"/public/{slug}/reviews")

    assert response.status_code == 200
    body = response.json()
    assert body["total_reviews"] == 0
    assert body["average_rating"] is None
    assert body["reviews"] == []


def test_owner_reviews_list(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]
    _complete_appointment(token)

    client.post(f"/manage/{token}/review", json={"rating": 4, "comment": "Muito bom"})

    response = client.get("/reviews/", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["rating"] == 4
    assert body[0]["comment"] == "Muito bom"
    assert body[0]["client_name"] == "Cliente Publico"
    assert body[0]["service_name"] == "Corte"
