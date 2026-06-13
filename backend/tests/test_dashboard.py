from datetime import datetime

from app.database.session import SessionLocal
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


def _book(client, slug, service_id, professional_id, cpf, when):
    return client.post(f"/public/{slug}/appointments", json={
        "full_name": "Cliente Teste",
        "birth_date": "1995-05-05",
        "cpf": cpf,
        "phone": "11977777777",
        "email": f"{cpf}@test.com",
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


def test_stats_requires_auth(client):
    response = client.get("/dashboard/stats")
    assert response.status_code == 401


def test_stats_empty_business(client):
    headers, slug, service_id, professional_id = _setup_business(client)

    response = client.get("/dashboard/stats", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["kpis"]["today_appointments"] == 0
    assert body["kpis"]["month_revenue"] == 0
    assert body["kpis"]["total_services"] == 1
    assert body["kpis"]["average_rating"] is None
    assert body["today_appointments_list"] == []


def test_stats_counts_today_revenue(client):
    headers, slug, service_id, professional_id = _setup_business(client)

    today = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    booking = _book(
        client, slug, service_id, professional_id,
        "16899555468", "2026-06-15T09:00:00",
    )
    _set_scheduled_at(booking["public_token"], today)

    response = client.get("/dashboard/stats", headers=headers)
    body = response.json()

    assert body["kpis"]["today_appointments"] == 1
    assert body["kpis"]["today_revenue"] == 50.0
    assert body["kpis"]["average_ticket"] == 50.0


def test_cancelled_appointment_excluded_from_revenue(client):
    headers, slug, service_id, professional_id = _setup_business(client)

    today = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    booking = _book(
        client, slug, service_id, professional_id,
        "16899555468", "2026-06-15T09:00:00",
    )
    _set_scheduled_at(booking["public_token"], today)

    client.post(f"/manage/{booking['public_token']}/cancel")

    response = client.get("/dashboard/stats", headers=headers)
    body = response.json()

    assert body["kpis"]["today_appointments"] == 0
    assert body["kpis"]["today_revenue"] == 0.0


def test_new_clients_month_counts_recent_clients(client):
    headers, slug, service_id, professional_id = _setup_business(client)

    _book(
        client, slug, service_id, professional_id,
        "16899555468", "2026-06-15T09:00:00",
    )

    response = client.get("/dashboard/stats", headers=headers)
    body = response.json()

    # client was created this month via the booking
    assert body["kpis"]["total_clients"] == 1
    assert body["kpis"]["new_clients_month"] == 1


def test_six_month_chart_has_six_points(client):
    headers, slug, service_id, professional_id = _setup_business(client)

    response = client.get("/dashboard/stats", headers=headers)
    body = response.json()

    assert len(body["monthly_revenue_chart"]) == 6
    for point in body["monthly_revenue_chart"]:
        assert "month" in point
        assert "revenue" in point


def test_filter_by_professional(client):
    headers, slug, service_id, professional_id = _setup_business(client)

    today = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    booking = _book(
        client, slug, service_id, professional_id,
        "16899555468", "2026-06-15T09:00:00",
    )
    _set_scheduled_at(booking["public_token"], today)

    # matching professional sees the appointment
    matching = client.get(
        "/dashboard/stats",
        params={"professional_id": professional_id},
        headers=headers,
    ).json()
    assert matching["kpis"]["today_appointments"] == 1

    # a different professional id sees nothing
    other = client.get(
        "/dashboard/stats",
        params={"professional_id": professional_id + 999},
        headers=headers,
    ).json()
    assert other["kpis"]["today_appointments"] == 0


def test_period_summary_defaults_to_month(client):
    headers, slug, service_id, professional_id = _setup_business(client)

    response = client.get("/dashboard/stats", headers=headers)
    body = response.json()

    assert "period" in body
    assert body["period"]["appointments"] == 0
    assert body["period"]["revenue"] == 0


def test_period_summary_respects_date_range(client):
    headers, slug, service_id, professional_id = _setup_business(client)

    booking = _book(
        client, slug, service_id, professional_id,
        "16899555468", "2026-06-15T09:00:00",
    )
    _set_scheduled_at(booking["public_token"], datetime(2026, 3, 10, 9, 0, 0))

    inside = client.get(
        "/dashboard/stats",
        params={"start_date": "2026-03-01", "end_date": "2026-03-31"},
        headers=headers,
    ).json()
    assert inside["period"]["appointments"] == 1
    assert inside["period"]["revenue"] == 50.0
    assert inside["period"]["ticket"] == 50.0

    outside = client.get(
        "/dashboard/stats",
        params={"start_date": "2026-04-01", "end_date": "2026-04-30"},
        headers=headers,
    ).json()
    assert outside["period"]["appointments"] == 0


def test_no_show_excluded_from_revenue(client):
    headers, slug, service_id, professional_id = _setup_business(client)

    today = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    booking = _book(
        client, slug, service_id, professional_id,
        "16899555468", "2026-06-15T09:00:00",
    )
    _set_scheduled_at(booking["public_token"], today)

    # counts as revenue while scheduled
    before = client.get("/dashboard/stats", headers=headers).json()
    assert before["kpis"]["today_revenue"] == 50.0

    # mark as no-show via the owner endpoint
    from app.database.session import SessionLocal
    from app.models.appointment import Appointment as Appt
    db = SessionLocal()
    appt = db.query(Appt).filter(Appt.public_token == booking["public_token"]).first()
    appt.status = "no_show"
    db.commit()
    db.close()

    after = client.get("/dashboard/stats", headers=headers).json()
    assert after["kpis"]["today_revenue"] == 0.0
