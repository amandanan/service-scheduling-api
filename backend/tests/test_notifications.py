import logging

from app.core.email import send_email
from app.core.whatsapp import send_whatsapp, normalize_phone
from app.core.notifications import send_appointment_reminder


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


def test_public_booking_sends_confirmation_email(client, sent_emails):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)

    response = client.post(f"/public/{slug}/appointments", json={
        "full_name": "Cliente Publico",
        "birth_date": "1995-05-05",
        "cpf": "16899555468",
        "phone": "11977777777",
        "email": "cliente@test.com",
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": "2026-06-15T09:00:00",
    })

    assert response.status_code == 200
    booking = response.json()

    assert len(sent_emails) == 1
    sent = sent_emails[0]

    assert sent["to"] == "cliente@test.com"
    assert "Studio Bella" in sent["subject"]
    assert "Corte" in sent["body"]
    assert booking["public_token"] in sent["body"]


def test_public_booking_sends_whatsapp_confirmation(client, sent_whatsapps):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)

    response = client.post(f"/public/{slug}/appointments", json={
        "full_name": "Cliente Publico",
        "birth_date": "1995-05-05",
        "cpf": "16899555468",
        "phone": "11977777777",
        "email": "cliente@test.com",
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": "2026-06-15T09:00:00",
    })

    assert response.status_code == 200
    booking = response.json()

    assert len(sent_whatsapps) == 1
    sent = sent_whatsapps[0]

    # the client's phone is forwarded; normalisation happens inside send_whatsapp
    assert sent["to"] == "11977777777"
    assert "Corte" in sent["message"]
    assert booking["public_token"] in sent["message"]


def test_booking_without_phone_skips_whatsapp(client, sent_whatsapps, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)

    # client created without a phone number
    client_response = client.post("/clients/", json={
        "full_name": "Sem Telefone",
        "birth_date": "1990-01-01",
        "phone": "",
        "email": "semfone@test.com",
    }, headers=headers)

    service_response = client.post("/services/", json={
        "name": "Corte",
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers)

    client.post("/appointments/", json={
        "client_id": client_response.json()["id"],
        "service_id": service_response.json()["id"],
        "professional_id": professional_id,
        "scheduled_at": "2026-06-15T09:00:00",
    }, headers=headers)

    assert sent_whatsapps == []


def test_normalize_phone():
    assert normalize_phone("(11) 97777-7777") == "5511977777777"
    assert normalize_phone("11977777777") == "5511977777777"
    assert normalize_phone("5511977777777") == "5511977777777"
    assert normalize_phone("") == ""


def test_send_whatsapp_logs_when_provider_not_configured(monkeypatch, caplog):
    monkeypatch.delenv("WHATSAPP_API_URL", raising=False)

    with caplog.at_level(logging.INFO, logger="app.core.whatsapp"):
        send_whatsapp("11977777777", "Mensagem de teste")

    assert any("WhatsApp not sent" in record.message for record in caplog.records)


def test_authenticated_booking_sends_confirmation_email(client, auth_headers, first_professional_id, sent_emails):
    headers = auth_headers()
    professional_id = first_professional_id(headers)

    client_response = client.post("/clients/", json={
        "full_name": "Cliente A",
        "birth_date": "1990-01-01",
        "cpf": "39053344705",
        "phone": "11988888888",
        "email": "clientea@test.com",
    }, headers=headers)

    service_response = client.post("/services/", json={
        "name": "Corte",
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers)

    response = client.post("/appointments/", json={
        "client_id": client_response.json()["id"],
        "service_id": service_response.json()["id"],
        "professional_id": professional_id,
        "scheduled_at": "2026-06-15T09:00:00",
    }, headers=headers)

    assert response.status_code == 200

    assert len(sent_emails) == 1
    assert sent_emails[0]["to"] == "clientea@test.com"


def test_send_email_logs_when_smtp_not_configured(monkeypatch, caplog):
    monkeypatch.delenv("SMTP_HOST", raising=False)

    with caplog.at_level(logging.INFO, logger="app.core.email"):
        send_email("cliente@test.com", "Assunto", "Corpo")

    assert any("Email not sent" in record.message for record in caplog.records)


def test_send_appointment_reminder(client, sent_emails):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)

    booking = client.post(f"/public/{slug}/appointments", json={
        "full_name": "Cliente Publico",
        "birth_date": "1995-05-05",
        "cpf": "16899555468",
        "phone": "11977777777",
        "email": "cliente@test.com",
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": "2026-06-15T09:00:00",
    }).json()

    sent_emails.clear()

    from app.database.session import SessionLocal
    from app.models.appointment import Appointment
    from app.models.client import Client
    from app.models.professional import Professional
    from app.models.service import Service
    from app.models.user import User

    db = SessionLocal()

    try:
        appointment = db.query(Appointment).filter(Appointment.public_token == booking["public_token"]).first()
        business = db.query(User).filter(User.id == appointment.owner_id).first()
        service = db.query(Service).filter(Service.id == appointment.service_id).first()
        professional = db.query(Professional).filter(Professional.id == appointment.professional_id).first()
        appointment_client = db.query(Client).filter(Client.id == appointment.client_id).first()

        send_appointment_reminder(db, appointment, business, service, professional, appointment_client)

    finally:
        db.close()

    assert len(sent_emails) == 1
    assert "Lembrete" in sent_emails[0]["subject"]
