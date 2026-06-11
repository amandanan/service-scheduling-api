def test_create_and_list_client(client, auth_headers):
    headers = auth_headers()

    response = client.post("/clients/", json={
        "full_name": "Cliente A",
        "birth_date": "1990-01-01",
        "cpf": "22222222222",
        "phone": "11988888888",
        "email": "cliente@test.com",
    }, headers=headers)

    assert response.status_code == 200

    response = client.get("/clients/", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_clients_are_isolated_per_user(client, auth_headers):
    headers_a = auth_headers(email="a@test.com", cpf="11111111111")
    headers_b = auth_headers(email="b@test.com", cpf="33333333333")

    client.post("/clients/", json={
        "full_name": "Cliente A",
        "birth_date": "1990-01-01",
        "cpf": "22222222222",
        "phone": "11988888888",
        "email": "cliente@test.com",
    }, headers=headers_a)

    response = client.get("/clients/", headers=headers_b)

    assert response.status_code == 200
    assert response.json() == []


def test_user_cannot_access_other_users_client(client, auth_headers):
    headers_a = auth_headers(email="a@test.com", cpf="11111111111")
    headers_b = auth_headers(email="b@test.com", cpf="33333333333")

    response = client.post("/clients/", json={
        "full_name": "Cliente A",
        "birth_date": "1990-01-01",
        "cpf": "22222222222",
        "phone": "11988888888",
        "email": "cliente@test.com",
    }, headers=headers_a)

    client_id = response.json()["id"]

    response = client.get(f"/clients/{client_id}", headers=headers_b)
    assert response.status_code == 404

    response = client.delete(f"/clients/{client_id}", headers=headers_b)
    assert response.status_code == 404
