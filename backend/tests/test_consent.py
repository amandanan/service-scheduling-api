from app.database.session import SessionLocal
from app.models.notification_log import NotificationLog


def _setup_business_with_service(client):
    client.post("/auth/register", json={
        "full_name": "Studio Bella", "birth_date": "1990-01-01",
        "cpf": "11144477735", "phone": "11999999999",
        "email": "bella@test.com", "password": "senha123",
    })
    login = client.post("/auth/login", data={"username": "bella@test.com", "password": "senha123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    service = client.post("/services/", json={
        "name": "Corte", "price": 50.0, "duration_minutes": 60,
    }, headers=headers)
    me = client.get("/auth/me", headers=headers).json()
    slug = me["booking_slug"]
    professional_id = client.get(f"/public/{slug}/professionals").json()[0]["id"]
    return headers, slug, service.json()["id"], professional_id


def _book(client, slug, service_id, professional_id, consent, cpf="16899555468"):
    return client.post(f"/public/{slug}/appointments", json={
        "full_name": "Cliente", "birth_date": "1995-05-05", "cpf": cpf,
        "phone": "11977777777", "email": f"{cpf}@test.com",
        "service_id": service_id, "professional_id": professional_id,
        "scheduled_at": "2026-09-15T09:00:00",
        "notification_consent": consent,
    }).json()


def _logs():
    db = SessionLocal()
    try:
        return db.query(NotificationLog).all()
    finally:
        db.close()


def test_booking_with_consent_sends_and_logs(client, sent_emails, sent_whatsapps):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)

    _book(client, slug, service_id, professional_id, consent=True)

    assert len(sent_emails) == 1
    assert len(sent_whatsapps) == 1

    logs = _logs()
    channels = sorted(log.channel for log in logs)
    assert channels == ["email", "whatsapp"]
    assert all(log.status == "sent" for log in logs)
    assert all(log.notification_type == "confirmation" for log in logs)


def test_booking_without_consent_skips_and_logs(client, sent_emails, sent_whatsapps):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)

    _book(client, slug, service_id, professional_id, consent=False)

    # nothing is sent
    assert sent_emails == []
    assert sent_whatsapps == []

    # but the skip is recorded for the LGPD audit trail
    logs = _logs()
    assert len(logs) == 1
    assert logs[0].status == "skipped_no_consent"


def test_client_consent_defaults_true_and_is_exposed(client, auth_headers):
    headers = auth_headers()
    created = client.post("/clients/", json={
        "full_name": "Sem flag", "birth_date": "1990-01-01",
        "phone": "11966666666", "email": "x@test.com",
    }, headers=headers)
    assert created.status_code == 200
    assert created.json()["notification_consent"] is True


def test_client_created_without_consent(client, auth_headers):
    headers = auth_headers()
    created = client.post("/clients/", json={
        "full_name": "Opt out", "birth_date": "1990-01-01",
        "phone": "11966666666", "email": "y@test.com",
        "notification_consent": False,
    }, headers=headers)
    assert created.json()["notification_consent"] is False


def test_reminder_respects_consent(client, sent_emails):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    _book(client, slug, service_id, professional_id, consent=False)
    sent_emails.clear()

    from datetime import datetime, timedelta
    from app.models.appointment import Appointment
    from app.core.reminders import send_due_reminders

    db = SessionLocal()
    try:
        appointment = db.query(Appointment).first()
        appointment.scheduled_at = datetime.now() + timedelta(hours=2)
        db.commit()
        # the reminder runs but sends nothing because consent is denied
        send_due_reminders(db)
    finally:
        db.close()

    assert sent_emails == []
