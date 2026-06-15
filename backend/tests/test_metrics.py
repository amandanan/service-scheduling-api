from datetime import datetime

from tests._dates import at

from app.database.session import SessionLocal
from app.models.user import User
from app.models.client import Client
from app.models.appointment import Appointment


def _setup_business(client):
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


def _owner_id(email="bella@test.com"):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first().id
    finally:
        db.close()


def _make_client(owner_id, cpf="16899555468"):
    db = SessionLocal()
    try:
        c = Client(owner_id=owner_id, full_name="Cliente", cpf=cpf)
        db.add(c)
        db.commit()
        db.refresh(c)
        return c.id
    finally:
        db.close()


def _add_appt(owner_id, client_id, service_id, professional_id,
              status, price, when=None):
    """Insert an appointment straight into the DB with full control over its
    status / frozen price / scheduling, bypassing availability checks."""
    db = SessionLocal()
    try:
        appt = Appointment(
            owner_id=owner_id,
            client_id=client_id,
            service_id=service_id,
            professional_id=professional_id,
            scheduled_at=when or datetime.now(),
            status=status,
            price_charged=price,
        )
        db.add(appt)
        db.commit()
    finally:
        db.close()


def test_metrics_requires_auth(client):
    response = client.get("/dashboard/metrics")
    assert response.status_code == 401


def test_metrics_empty_business(client):
    headers, slug, service_id, professional_id = _setup_business(client)

    body = client.get("/dashboard/metrics", headers=headers).json()

    assert body["total_appointments"] == 0
    assert body["no_show_rate"] == 0.0
    assert body["cancellation_rate"] == 0.0
    assert body["realization_rate"] == 0.0
    assert body["realized_revenue"] == 0.0
    assert body["expected_revenue"] == 0.0
    assert body["revenue_by_service"] == []


def test_metrics_rates_and_counts(client):
    headers, slug, service_id, professional_id = _setup_business(client)
    owner_id = _owner_id()
    client_id = _make_client(owner_id)

    # 3 completed, 1 no-show, 2 cancelled -> total 6, expected 4
    for _ in range(3):
        _add_appt(owner_id, client_id, service_id, professional_id, "completed", 50.0)
    _add_appt(owner_id, client_id, service_id, professional_id, "no_show", 50.0)
    for _ in range(2):
        _add_appt(owner_id, client_id, service_id, professional_id, "cancelled", 50.0)

    body = client.get("/dashboard/metrics", headers=headers).json()

    assert body["total_appointments"] == 6
    assert body["completed"] == 3
    assert body["no_show"] == 1
    assert body["cancelled"] == 2
    assert body["expected"] == 4

    # no-show rate = no_show / (completed + no_show) = 1/4
    assert body["no_show_rate"] == 25.0
    # cancellation rate = cancelled / total = 2/6
    assert body["cancellation_rate"] == 33.3
    # realization rate = completed / expected = 3/4
    assert body["realization_rate"] == 75.0


def test_revenue_by_service_and_totals(client):
    headers, slug, service_id, professional_id = _setup_business(client)
    owner_id = _owner_id()
    client_id = _make_client(owner_id)

    other = client.post("/services/", json={
        "name": "Barba", "price": 30.0, "duration_minutes": 30,
    }, headers=headers).json()["id"]

    # Corte: 2 completed @ 50 ; Barba: 1 completed @ 30 ; plus a scheduled @ 50
    _add_appt(owner_id, client_id, service_id, professional_id, "completed", 50.0)
    _add_appt(owner_id, client_id, service_id, professional_id, "completed", 50.0)
    _add_appt(owner_id, client_id, other, professional_id, "completed", 30.0)
    _add_appt(owner_id, client_id, service_id, professional_id, "scheduled", 50.0)
    _add_appt(owner_id, client_id, service_id, professional_id, "cancelled", 50.0)

    body = client.get("/dashboard/metrics", headers=headers).json()

    # realized = completed only = 50 + 50 + 30
    assert body["realized_revenue"] == 130.0
    # expected = everything not cancelled = realized + the scheduled one
    assert body["expected_revenue"] == 180.0

    rows = body["revenue_by_service"]
    assert len(rows) == 2
    # sorted by revenue desc -> Corte (100) first, Barba (30) second
    assert rows[0]["service_name"] == "Corte"
    assert rows[0]["revenue"] == 100.0
    assert rows[0]["count"] == 2
    assert rows[1]["service_name"] == "Barba"
    assert rows[1]["revenue"] == 30.0


def test_revenue_uses_frozen_price_not_current(client):
    headers, slug, service_id, professional_id = _setup_business(client)

    # book through the public flow so price_charged is captured (50.0)
    booking = client.post(f"/public/{slug}/appointments", json={
        "full_name": "Cliente Teste",
        "birth_date": "1995-05-05",
        "cpf": "16899555468",
        "phone": "11977777777",
        "email": "ct@test.com",
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": at(9),
    }).json()

    # complete it and pull it into the current period
    db = SessionLocal()
    appt = db.query(Appointment).filter(
        Appointment.public_token == booking["public_token"]
    ).first()
    appt.status = "completed"
    appt.scheduled_at = datetime.now()
    db.commit()
    db.close()

    # now the service price changes; the report must NOT follow it
    client.put(f"/services/{service_id}", json={
        "name": "Corte", "price": 80.0, "duration_minutes": 60,
    }, headers=headers)

    body = client.get("/dashboard/metrics", headers=headers).json()

    assert body["realized_revenue"] == 50.0
    assert body["revenue_by_service"][0]["revenue"] == 50.0


def test_cancellation_attribution(client):
    headers, slug, service_id, professional_id = _setup_business(client)
    owner_id = _owner_id()

    # reception cancel (hard route -> soft cancel) attributes "reception"
    client_id = _make_client(owner_id)
    _add_appt(owner_id, client_id, service_id, professional_id, "scheduled", 50.0)
    db = SessionLocal()
    appt_id = db.query(Appointment).filter(
        Appointment.owner_id == owner_id
    ).first().id
    db.close()
    assert client.delete(f"/appointments/{appt_id}", headers=headers).status_code == 200

    # client cancel through the token route attributes "client" (>24h ahead)
    booking = client.post(f"/public/{slug}/appointments", json={
        "full_name": "Cliente Teste",
        "birth_date": "1995-05-05",
        "cpf": "39053344705",
        "phone": "11977777777",
        "email": "ct2@test.com",
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": at(10),
    }).json()
    # pull it into the current period but keep it future enough was at()+30d;
    # the token route checks the real scheduled_at, so cancel before moving it
    cancel = client.post(f"/manage/{booking['public_token']}/cancel")
    assert cancel.status_code == 200
    db = SessionLocal()
    appt = db.query(Appointment).filter(
        Appointment.public_token == booking["public_token"]
    ).first()
    appt.scheduled_at = datetime.now()
    db.commit()
    db.close()

    body = client.get("/dashboard/metrics", headers=headers).json()

    assert body["cancelled"] == 2
    assert body["cancelled_by_reception"] == 1
    assert body["cancelled_by_client"] == 1


def test_metrics_respects_period(client):
    headers, slug, service_id, professional_id = _setup_business(client)
    owner_id = _owner_id()
    client_id = _make_client(owner_id)

    _add_appt(owner_id, client_id, service_id, professional_id, "completed", 50.0,
              when=datetime.now())
    _add_appt(owner_id, client_id, service_id, professional_id, "completed", 99.0,
              when=datetime(2026, 1, 10, 9, 0, 0))

    # default period (current month) sees only the recent one
    default_body = client.get("/dashboard/metrics", headers=headers).json()
    assert default_body["completed"] == 1
    assert default_body["realized_revenue"] == 50.0

    # explicit January window sees only the old one
    jan = client.get(
        "/dashboard/metrics",
        params={"start_date": "2026-01-01", "end_date": "2026-01-31"},
        headers=headers,
    ).json()
    assert jan["completed"] == 1
    assert jan["realized_revenue"] == 99.0
