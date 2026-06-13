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


def test_booking_returns_public_token(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)

    booking = _book(client, slug, service_id, professional_id)

    assert "public_token" in booking
    assert booking["public_token"]


def test_view_appointment_by_token(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]

    response = client.get(f"/manage/{token}")

    assert response.status_code == 200
    body = response.json()
    assert body["business_name"] == "Studio Bella"
    assert body["service_name"] == "Corte"
    assert body["status"] == "scheduled"


def test_view_appointment_unknown_token(client):
    response = client.get("/manage/doesnotexist")

    assert response.status_code == 404


def test_cancel_frees_the_slot(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]

    # slot taken
    slots = client.get(
        f"/public/{slug}/available-slots",
        params={"date": "2026-06-15", "service_id": service_id, "professional_id": professional_id},
    ).json()
    assert "09:00" not in slots

    cancel = client.post(f"/manage/{token}/cancel")
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "cancelled"

    # slot is free again
    slots = client.get(
        f"/public/{slug}/available-slots",
        params={"date": "2026-06-15", "service_id": service_id, "professional_id": professional_id},
    ).json()
    assert "09:00" in slots

    # cancelled appointment no longer in the owner's agenda
    appointments = client.get("/appointments/", headers=headers).json()
    assert appointments == []


def test_reschedule_moves_the_appointment(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]

    response = client.post(f"/manage/{token}/reschedule", json={
        "scheduled_at": "2026-06-15T10:00:00",
    })

    assert response.status_code == 200

    slots = client.get(
        f"/public/{slug}/available-slots",
        params={"date": "2026-06-15", "service_id": service_id, "professional_id": professional_id},
    ).json()

    # old slot free, new slot taken
    assert "09:00" in slots
    assert "10:00" not in slots


def test_reschedule_to_unavailable_slot_is_rejected(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]

    response = client.post(f"/manage/{token}/reschedule", json={
        "scheduled_at": "2020-01-01T09:00:00",
    })

    assert response.status_code == 409


def test_client_can_confirm_appointment(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]

    view = client.get(f"/manage/{token}").json()
    assert view["can_confirm"] is True
    assert view["status"] == "scheduled"

    response = client.post(f"/manage/{token}/confirm")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "confirmed"
    assert body["can_confirm"] is False


def test_cannot_confirm_cancelled_appointment(client):
    headers, slug, service_id, professional_id = _setup_business_with_service(client)
    token = _book(client, slug, service_id, professional_id)["public_token"]

    client.post(f"/manage/{token}/cancel")

    response = client.post(f"/manage/{token}/confirm")
    assert response.status_code == 409
