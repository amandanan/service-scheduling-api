def _create_client_and_service(api, headers, service_name="Corte"):
    client_response = api.post("/clients/", json={
        "full_name": "Cliente A",
        "birth_date": "1990-01-01",
        "cpf": "39053344705",
        "phone": "11988888888",
        "email": "cliente@test.com",
    }, headers=headers)

    service_response = api.post("/services/", json={
        "name": service_name,
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers)

    return client_response.json()["id"], service_response.json()["id"]


def _create_package(api, headers, service_id, total_sessions=10):
    response = api.post("/packages/", json={
        "name": "Pacote 10 sessões",
        "service_id": service_id,
        "total_sessions": total_sessions,
        "price": 400.0,
    }, headers=headers)

    return response.json()["id"]


def test_create_and_list_packages(client, auth_headers):
    headers = auth_headers()
    _, service_id = _create_client_and_service(client, headers)

    response = client.post("/packages/", json={
        "name": "Pacote 10 sessões",
        "service_id": service_id,
        "total_sessions": 10,
        "price": 400.0,
    }, headers=headers)

    assert response.status_code == 200
    package = response.json()
    assert package["name"] == "Pacote 10 sessões"
    assert package["total_sessions"] == 10

    response = client.get("/packages/", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_cannot_create_package_for_other_users_service(client, auth_headers):
    headers_a = auth_headers(email="a@test.com", cpf="11144477735")
    headers_b = auth_headers(email="b@test.com", cpf="16899555468")

    _, service_id = _create_client_and_service(client, headers_a)

    response = client.post("/packages/", json={
        "name": "Pacote 10 sessões",
        "service_id": service_id,
        "total_sessions": 10,
        "price": 400.0,
    }, headers=headers_b)

    assert response.status_code == 404


def test_update_and_delete_package(client, auth_headers):
    headers = auth_headers()
    _, service_id = _create_client_and_service(client, headers)
    package_id = _create_package(client, headers, service_id)

    response = client.put(f"/packages/{package_id}", json={
        "name": "Pacote 5 sessões",
        "service_id": service_id,
        "total_sessions": 5,
        "price": 250.0,
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["total_sessions"] == 5

    response = client.delete(f"/packages/{package_id}", headers=headers)

    assert response.status_code == 200


def test_cannot_delete_package_already_sold(client, auth_headers):
    headers = auth_headers()
    client_id, service_id = _create_client_and_service(client, headers)
    package_id = _create_package(client, headers, service_id)

    client.post("/packages/purchases", json={
        "client_id": client_id,
        "package_id": package_id,
    }, headers=headers)

    response = client.delete(f"/packages/{package_id}", headers=headers)

    assert response.status_code == 400


def test_purchase_package_and_view_balance(client, auth_headers):
    headers = auth_headers()
    client_id, service_id = _create_client_and_service(client, headers)
    package_id = _create_package(client, headers, service_id, total_sessions=10)

    response = client.post("/packages/purchases", json={
        "client_id": client_id,
        "package_id": package_id,
    }, headers=headers)

    assert response.status_code == 200
    purchase = response.json()
    assert purchase["total_sessions"] == 10
    assert purchase["remaining_sessions"] == 10
    assert purchase["client_id"] == client_id

    response = client.get("/packages/purchases", params={"client_id": client_id}, headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_appointment_redeems_package_session(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)
    client_id, service_id = _create_client_and_service(client, headers)
    package_id = _create_package(client, headers, service_id, total_sessions=2)

    purchase = client.post("/packages/purchases", json={
        "client_id": client_id,
        "package_id": package_id,
    }, headers=headers).json()

    response = client.post("/appointments/", json={
        "client_id": client_id,
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": "2026-06-15T09:00:00",
        "client_package_id": purchase["id"],
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["client_package_id"] == purchase["id"]

    balance = client.get("/packages/purchases", params={"client_id": client_id}, headers=headers).json()
    assert balance[0]["remaining_sessions"] == 1


def test_appointment_redemption_fails_when_no_sessions_remaining(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)
    client_id, service_id = _create_client_and_service(client, headers)
    package_id = _create_package(client, headers, service_id, total_sessions=1)

    purchase = client.post("/packages/purchases", json={
        "client_id": client_id,
        "package_id": package_id,
    }, headers=headers).json()

    client.post("/appointments/", json={
        "client_id": client_id,
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": "2026-06-15T09:00:00",
        "client_package_id": purchase["id"],
    }, headers=headers)

    response = client.post("/appointments/", json={
        "client_id": client_id,
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": "2026-06-16T09:00:00",
        "client_package_id": purchase["id"],
    }, headers=headers)

    assert response.status_code == 400


def test_appointment_redemption_fails_for_wrong_service(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)
    client_id, service_id = _create_client_and_service(client, headers)
    package_id = _create_package(client, headers, service_id, total_sessions=2)

    purchase = client.post("/packages/purchases", json={
        "client_id": client_id,
        "package_id": package_id,
    }, headers=headers).json()

    other_service = client.post("/services/", json={
        "name": "Manicure",
        "price": 30.0,
        "duration_minutes": 30,
    }, headers=headers).json()

    response = client.post("/appointments/", json={
        "client_id": client_id,
        "service_id": other_service["id"],
        "professional_id": professional_id,
        "scheduled_at": "2026-06-15T09:00:00",
        "client_package_id": purchase["id"],
    }, headers=headers)

    assert response.status_code == 400


def test_deleting_appointment_refunds_package_session(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)
    client_id, service_id = _create_client_and_service(client, headers)
    package_id = _create_package(client, headers, service_id, total_sessions=2)

    purchase = client.post("/packages/purchases", json={
        "client_id": client_id,
        "package_id": package_id,
    }, headers=headers).json()

    appointment = client.post("/appointments/", json={
        "client_id": client_id,
        "service_id": service_id,
        "professional_id": professional_id,
        "scheduled_at": "2026-06-15T09:00:00",
        "client_package_id": purchase["id"],
    }, headers=headers).json()

    balance = client.get("/packages/purchases", params={"client_id": client_id}, headers=headers).json()
    assert balance[0]["remaining_sessions"] == 1

    response = client.delete(f"/appointments/{appointment['id']}", headers=headers)
    assert response.status_code == 200

    balance = client.get("/packages/purchases", params={"client_id": client_id}, headers=headers).json()
    assert balance[0]["remaining_sessions"] == 2
