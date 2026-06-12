def test_create_and_list_client(client, auth_headers):
    headers = auth_headers()

    response = client.post("/clients/", json={
        "full_name": "Cliente A",
        "birth_date": "1990-01-01",
        "cpf": "39053344705",
        "phone": "11988888888",
        "email": "cliente@test.com",
    }, headers=headers)

    assert response.status_code == 200

    response = client.get("/clients/", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_client_rejects_invalid_cpf(client, auth_headers):
    headers = auth_headers()

    response = client.post("/clients/", json={
        "full_name": "Cliente A",
        "birth_date": "1990-01-01",
        "cpf": "12345678900",
        "phone": "11988888888",
        "email": "cliente@test.com",
    }, headers=headers)

    assert response.status_code == 422


def test_create_client_normalizes_masked_cpf(client, auth_headers):
    headers = auth_headers()

    response = client.post("/clients/", json={
        "full_name": "Cliente A",
        "birth_date": "1990-01-01",
        "cpf": "390.533.447-05",
        "phone": "11988888888",
        "email": "cliente@test.com",
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["cpf"] == "39053344705"


def test_same_cpf_masked_and_unmasked_is_rejected_as_duplicate(client, auth_headers):
    headers = auth_headers()

    payload = {
        "full_name": "Cliente A",
        "birth_date": "1990-01-01",
        "cpf": "39053344705",
        "phone": "11988888888",
        "email": "cliente@test.com",
    }

    first = client.post("/clients/", json=payload, headers=headers)
    assert first.status_code == 200

    # same CPF, masked form + different email -> still a duplicate CPF
    second = client.post("/clients/", json={
        **payload,
        "cpf": "390.533.447-05",
        "email": "outro@test.com",
    }, headers=headers)

    assert second.status_code == 400


def test_clients_are_isolated_per_user(client, auth_headers):
    headers_a = auth_headers(email="a@test.com", cpf="11144477735")
    headers_b = auth_headers(email="b@test.com", cpf="16899555468")

    client.post("/clients/", json={
        "full_name": "Cliente A",
        "birth_date": "1990-01-01",
        "cpf": "39053344705",
        "phone": "11988888888",
        "email": "cliente@test.com",
    }, headers=headers_a)

    response = client.get("/clients/", headers=headers_b)

    assert response.status_code == 200
    assert response.json() == []


def test_user_cannot_access_other_users_client(client, auth_headers):
    headers_a = auth_headers(email="a@test.com", cpf="11144477735")
    headers_b = auth_headers(email="b@test.com", cpf="16899555468")

    response = client.post("/clients/", json={
        "full_name": "Cliente A",
        "birth_date": "1990-01-01",
        "cpf": "39053344705",
        "phone": "11988888888",
        "email": "cliente@test.com",
    }, headers=headers_a)

    client_id = response.json()["id"]

    response = client.get(f"/clients/{client_id}", headers=headers_b)
    assert response.status_code == 404

    response = client.delete(f"/clients/{client_id}", headers=headers_b)
    assert response.status_code == 404


def test_create_client_without_cpf(client, auth_headers):
    headers = auth_headers()

    response = client.post("/clients/", json={
        "full_name": "Sem CPF",
        "birth_date": "1990-01-01",
        "phone": "11988888888",
        "email": "semcpf@test.com",
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["cpf"] is None


def test_create_multiple_clients_without_cpf(client, auth_headers):
    headers = auth_headers()

    first = client.post("/clients/", json={
        "full_name": "Cliente Um",
        "birth_date": "1990-01-01",
        "phone": "11988888888",
        "email": "um@test.com",
    }, headers=headers)
    assert first.status_code == 200

    # a second CPF-less client must not collide with the first
    second = client.post("/clients/", json={
        "full_name": "Cliente Dois",
        "birth_date": "1991-02-02",
        "phone": "11977777777",
        "email": "dois@test.com",
    }, headers=headers)
    assert second.status_code == 200
