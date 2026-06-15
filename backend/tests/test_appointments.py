from tests._dates import WEEKDAY_STR, at
def _create_client_and_service(api, headers):
    client_response = api.post("/clients/", json={
        "full_name": "Cliente A",
        "birth_date": "1990-01-01",
        "cpf": "39053344705",
        "phone": "11988888888",
        "email": "cliente@test.com",
    }, headers=headers)

    service_response = api.post("/services/", json={
        "name": "Corte",
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers)

    return client_response.json()["id"], service_response.json()["id"]


def test_create_appointment(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)
    client_id, service_id = _create_client_and_service(client, headers)

    response = client.post("/appointments/", json={
        "client_id": client_id,
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": at(9),
    }, headers=headers)

    assert response.status_code == 200


def test_overlapping_appointment_is_not_offered_as_available_slot(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)
    client_id, service_id = _create_client_and_service(client, headers)

    client.post("/appointments/", json={
        "client_id": client_id,
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": at(9),
    }, headers=headers)

    response = client.get(
        "/appointments/available-slots",
        params={"date": WEEKDAY_STR, "service_id": service_id, "professional_id": professional_id},
        headers=headers,
    )

    assert response.status_code == 200
    slots = response.json()

    assert "09:00" not in slots
    assert "09:30" not in slots
    assert "10:00" in slots


def test_cannot_create_appointment_with_other_users_client(client, auth_headers, first_professional_id):
    headers_a = auth_headers(email="a@test.com", cpf="11144477735")
    headers_b = auth_headers(email="b@test.com", cpf="16899555468")

    professional_b = first_professional_id(headers_b)
    client_id, service_id = _create_client_and_service(client, headers_a)

    response = client.post("/appointments/", json={
        "client_id": client_id,
        "service_id": service_id,
        "professional_id": professional_b,
        "scheduled_at": at(9),
    }, headers=headers_b)

    assert response.status_code == 404


def test_cannot_create_appointment_in_the_past(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)
    client_id, service_id = _create_client_and_service(client, headers)

    response = client.post("/appointments/", json={
        "client_id": client_id,
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": "2020-01-01T09:00:00",
    }, headers=headers)

    assert response.status_code == 400


def test_cannot_create_appointment_with_other_users_professional(client, auth_headers, first_professional_id):
    headers_a = auth_headers(email="a@test.com", cpf="11144477735")
    headers_b = auth_headers(email="b@test.com", cpf="16899555468")

    professional_b = first_professional_id(headers_b)
    client_id, service_id = _create_client_and_service(client, headers_a)

    response = client.post("/appointments/", json={
        "client_id": client_id,
        "service_id": service_id,
        "professional_id": professional_b,
        "scheduled_at": at(9),
    }, headers=headers_a)

    assert response.status_code == 404


def test_appointments_are_isolated_per_user(client, auth_headers, first_professional_id):
    headers_a = auth_headers(email="a@test.com", cpf="11144477735")
    headers_b = auth_headers(email="b@test.com", cpf="16899555468")

    professional_a = first_professional_id(headers_a)
    client_id, service_id = _create_client_and_service(client, headers_a)

    client.post("/appointments/", json={
        "client_id": client_id,
        "service_id": service_id,
        "professional_id": professional_a,
        "scheduled_at": at(9),
    }, headers=headers_a)

    response = client.get("/appointments/", headers=headers_b)

    assert response.status_code == 200
    assert response.json() == []


def test_new_appointment_defaults_to_scheduled(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)
    client_id, service_id = _create_client_and_service(client, headers)

    response = client.post("/appointments/", json={
        "client_id": client_id,
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": at(9),
    }, headers=headers)

    assert response.json()["status"] == "scheduled"


def test_update_appointment_status(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)
    client_id, service_id = _create_client_and_service(client, headers)

    appointment = client.post("/appointments/", json={
        "client_id": client_id,
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": at(9),
    }, headers=headers).json()

    response = client.patch(
        f"/appointments/{appointment['id']}/status",
        json={"status": "completed"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_update_appointment_status_rejects_invalid(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)
    client_id, service_id = _create_client_and_service(client, headers)

    appointment = client.post("/appointments/", json={
        "client_id": client_id,
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": at(9),
    }, headers=headers).json()

    response = client.patch(
        f"/appointments/{appointment['id']}/status",
        json={"status": "banana"},
        headers=headers,
    )

    assert response.status_code == 422
