def test_register_and_login(client):
    response = client.post("/auth/register", json={
        "full_name": "Amanda Teste",
        "birth_date": "1990-01-01",
        "cpf": "11111111111",
        "phone": "11999999999",
        "email": "amanda@test.com",
        "password": "senha123",
    })

    assert response.status_code == 200

    response = client.post("/auth/login", data={
        "username": "amanda@test.com",
        "password": "senha123",
    })

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_register_duplicate_email(client):
    payload = {
        "full_name": "Amanda Teste",
        "birth_date": "1990-01-01",
        "cpf": "11111111111",
        "phone": "11999999999",
        "email": "amanda@test.com",
        "password": "senha123",
    }

    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json={**payload, "cpf": "22222222222"})

    assert response.status_code == 400


def test_login_with_wrong_password(client):
    client.post("/auth/register", json={
        "full_name": "Amanda Teste",
        "birth_date": "1990-01-01",
        "cpf": "11111111111",
        "phone": "11999999999",
        "email": "amanda@test.com",
        "password": "senha123",
    })

    response = client.post("/auth/login", data={
        "username": "amanda@test.com",
        "password": "errada",
    })

    assert response.status_code == 400


def test_protected_route_requires_token(client):
    response = client.get("/clients/")

    assert response.status_code == 401
