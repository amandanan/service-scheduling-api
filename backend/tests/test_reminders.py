from tests._dates import at
from datetime import datetime, timedelta

from app.database.session import SessionLocal
from app.models.appointment import Appointment
from app.core.reminders import send_due_reminders


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


def _book(client, slug, service_id, professional_id, when=at(9)):
    return client.post(f"/public/{slug}/appointments", json={
        "full_name": "Cliente Publico",
        "birth_date": "1995-05-05",
        "cpf": "16899555468",
        "phone": "11977777777",
        "email": "cliente@test.com",
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": when,
    }).json()


def _set_scheduled_at(token, when):
    db = SessionLocal()
    appointment = db.query(Appointment).filter(
        Appointment.public_token == token
    ).first()
    appointment.scheduled_at = when
    db.commit()
    db.close()


def _reminder_sent_at(token):
    db = SessionLocal()
    try:
        appointment = db.query(Appointment).filter(
            Appointment.public_token == token
        ).first()
        return appointment.reminder_sent_at
    finally:
        db.close()


def test_sends_reminder_for_upcoming_appointment(client, sent_emails, sent_whatsapps):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]

    # happens in 2 hours -> inside the 24h window
    _set_scheduled_at(token, datetime.now() + timedelta(hours=2))

    sent_emails.clear()
    sent_whatsapps.clear()

    db = SessionLocal()
    try:
        count = send_due_reminders(db)
    finally:
        db.close()

    assert count == 1
    assert len(sent_emails) == 1
    assert "Lembrete" in sent_emails[0]["subject"]
    assert len(sent_whatsapps) == 1
    assert _reminder_sent_at(token) is not None


def test_reminder_is_sent_only_once(client, sent_emails):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]
    _set_scheduled_at(token, datetime.now() + timedelta(hours=2))

    db = SessionLocal()
    try:
        assert send_due_reminders(db) == 1
        # second run finds nothing new
        assert send_due_reminders(db) == 0
    finally:
        db.close()


def test_no_reminder_outside_window(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]

    # happens in 3 days -> outside the default 24h window
    _set_scheduled_at(token, datetime.now() + timedelta(days=3))

    db = SessionLocal()
    try:
        assert send_due_reminders(db) == 0
    finally:
        db.close()

    assert _reminder_sent_at(token) is None


def test_no_reminder_for_cancelled_appointment(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]
    _set_scheduled_at(token, datetime.now() + timedelta(hours=2))

    # cancel directly (the client 24h rule blocks token-cancel near the time)
    db = SessionLocal()
    appointment = db.query(Appointment).filter(
        Appointment.public_token == token
    ).first()
    appointment.status = "cancelled"
    db.commit()
    db.close()

    db = SessionLocal()
    try:
        assert send_due_reminders(db) == 0
    finally:
        db.close()


def test_no_reminder_for_past_appointment(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]

    _set_scheduled_at(token, datetime.now() - timedelta(hours=1))

    db = SessionLocal()
    try:
        assert send_due_reminders(db) == 0
    finally:
        db.close()
