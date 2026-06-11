def _register_business(client):
    response = client.post("/auth/register", json={
        "full_name": "Salao Da Amanda",
        "birth_date": "1990-01-01",
        "cpf": "11144477735",
        "phone": "11999999999",
        "email": "salao@test.com",
        "password": "senha123",
    })

    return response.json()


def _login(client, email="salao@test.com", password="senha123"):
    response = client.post("/auth/login", data={
        "username": email,
        "password": password,
    })

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def _public_professional_id(client, slug):
    response = client.get(f"/public/{slug}/professionals")
    return response.json()[0]["id"]


def test_register_generates_unique_booking_slug(client):
    user_a = _register_business(client)

    response = client.post("/auth/register", json={
        "full_name": "Salao Da Amanda",
        "birth_date": "1990-01-01",
        "cpf": "39053344705",
        "phone": "11988888888",
        "email": "salao2@test.com",
        "password": "senha123",
    })

    user_b = response.json()

    assert user_a["booking_slug"] == "salao-da-amanda"
    assert user_b["booking_slug"] != user_a["booking_slug"]
    assert user_b["booking_slug"].startswith("salao-da-amanda-")


def test_auth_me_returns_current_user(client):
    _register_business(client)
    headers = _login(client)

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "salao@test.com"
    assert response.json()["booking_slug"] == "salao-da-amanda"


def test_public_business_not_found(client):
    response = client.get("/public/inexistente/")

    assert response.status_code == 404


def test_public_business_info(client):
    user = _register_business(client)

    response = client.get(f"/public/{user['booking_slug']}/")

    assert response.status_code == 200
    assert response.json()["full_name"] == "Salao Da Amanda"
    assert response.json()["booking_slug"] == user["booking_slug"]


def test_public_lists_default_professional(client):
    user = _register_business(client)

    response = client.get(f"/public/{user['booking_slug']}/professionals")

    assert response.status_code == 200
    professionals = response.json()
    assert len(professionals) == 1
    assert professionals[0]["name"] == "Salao Da Amanda"


def test_public_services_and_available_slots(client):
    user = _register_business(client)
    headers = _login(client)

    service_response = client.post("/services/", json={
        "name": "Corte",
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers)

    service_id = service_response.json()["id"]
    slug = user["booking_slug"]
    professional_id = _public_professional_id(client, slug)

    response = client.get(f"/public/{slug}/services")

    assert response.status_code == 200
    services = response.json()
    assert len(services) == 1
    assert services[0]["id"] == service_id
    assert services[0]["name"] == "Corte"

    response = client.get(
        f"/public/{slug}/available-slots",
        params={"date": "2026-06-15", "service_id": service_id, "professional_id": professional_id},
    )

    assert response.status_code == 200
    assert "09:00" in response.json()


def test_create_public_booking(client):
    user = _register_business(client)
    headers = _login(client)

    service_response = client.post("/services/", json={
        "name": "Corte",
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers)

    service_id = service_response.json()["id"]
    slug = user["booking_slug"]
    professional_id = _public_professional_id(client, slug)

    booking_payload = {
        "full_name": "Cliente Publico",
        "birth_date": "1995-05-05",
        "cpf": "16899555468",
        "phone": "11977777777",
        "email": "clientepublico@test.com",
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": "2026-06-15T09:00:00",
    }

    response = client.post(f"/public/{slug}/appointments", json=booking_payload)

    assert response.status_code == 200
    assert response.json()["service_id"] == service_id
    assert response.json()["professional_id"] == professional_id

    clients_response = client.get("/clients/", headers=headers)
    clients = clients_response.json()

    assert len(clients) == 1
    assert clients[0]["cpf"] == "16899555468"

    appointments_response = client.get("/appointments/", headers=headers)
    assert len(appointments_response.json()) == 1


def test_public_booking_rejects_unavailable_slot(client):
    user = _register_business(client)
    headers = _login(client)

    service_response = client.post("/services/", json={
        "name": "Corte",
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers)

    service_id = service_response.json()["id"]
    slug = user["booking_slug"]
    professional_id = _public_professional_id(client, slug)

    booking_payload = {
        "full_name": "Cliente Publico",
        "birth_date": "1995-05-05",
        "cpf": "16899555468",
        "phone": "11977777777",
        "email": "clientepublico@test.com",
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": "2026-06-15T09:00:00",
    }

    first = client.post(f"/public/{slug}/appointments", json=booking_payload)
    assert first.status_code == 200

    second = client.post(f"/public/{slug}/appointments", json={
        **booking_payload,
        "cpf": "47362510853",
        "email": "outro@test.com",
    })

    assert second.status_code == 409


def test_public_available_slots_excludes_past_date(client):
    user = _register_business(client)
    headers = _login(client)

    service_response = client.post("/services/", json={
        "name": "Corte",
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers)

    service_id = service_response.json()["id"]
    slug = user["booking_slug"]
    professional_id = _public_professional_id(client, slug)

    response = client.get(
        f"/public/{slug}/available-slots",
        params={"date": "2020-01-01", "service_id": service_id, "professional_id": professional_id},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_public_booking_rejects_invalid_cpf(client):
    user = _register_business(client)
    headers = _login(client)

    service_response = client.post("/services/", json={
        "name": "Corte",
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers)

    service_id = service_response.json()["id"]
    slug = user["booking_slug"]
    professional_id = _public_professional_id(client, slug)

    response = client.post(f"/public/{slug}/appointments", json={
        "full_name": "Cliente Publico",
        "birth_date": "1995-05-05",
        "cpf": "12345678900",
        "phone": "11977777777",
        "email": "clientepublico@test.com",
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": "2026-06-15T09:00:00",
    })

    assert response.status_code == 422


def test_public_booking_rejects_past_date(client):
    user = _register_business(client)
    headers = _login(client)

    service_response = client.post("/services/", json={
        "name": "Corte",
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers)

    service_id = service_response.json()["id"]
    slug = user["booking_slug"]
    professional_id = _public_professional_id(client, slug)

    response = client.post(f"/public/{slug}/appointments", json={
        "full_name": "Cliente Publico",
        "birth_date": "1995-05-05",
        "cpf": "16899555468",
        "phone": "11977777777",
        "email": "clientepublico@test.com",
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": "2020-01-01T09:00:00",
    })

    assert response.status_code == 409


def test_public_booking_is_rate_limited(client):
    user = _register_business(client)
    headers = _login(client)

    service_response = client.post("/services/", json={
        "name": "Corte",
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers)

    service_id = service_response.json()["id"]
    slug = user["booking_slug"]
    professional_id = _public_professional_id(client, slug)

    # past date -> each request is rejected by the handler (409),
    # but every request still counts against the rate limit
    payload = {
        "full_name": "Cliente Publico",
        "birth_date": "1995-05-05",
        "cpf": "16899555468",
        "phone": "11977777777",
        "email": "clientepublico@test.com",
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": "2020-01-01T09:00:00",
    }

    statuses = [
        client.post(f"/public/{slug}/appointments", json=payload).status_code
        for _ in range(6)
    ]

    # the limit is 5/minute, so the 6th request is throttled
    assert statuses[-1] == 429
    assert statuses.count(429) == 1


def test_public_booking_reuses_existing_client_by_cpf(client):
    user = _register_business(client)
    headers = _login(client)

    service_response = client.post("/services/", json={
        "name": "Corte",
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers)

    service_id = service_response.json()["id"]
    slug = user["booking_slug"]
    professional_id = _public_professional_id(client, slug)

    booking_payload = {
        "full_name": "Cliente Publico",
        "birth_date": "1995-05-05",
        "cpf": "16899555468",
        "phone": "11977777777",
        "email": "clientepublico@test.com",
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": "2026-06-15T09:00:00",
    }

    client.post(f"/public/{slug}/appointments", json=booking_payload)

    second = client.post(f"/public/{slug}/appointments", json={
        **booking_payload,
        "scheduled_at": "2026-06-15T10:00:00",
    })

    assert second.status_code == 200

    clients_response = client.get("/clients/", headers=headers)
    assert len(clients_response.json()) == 1
