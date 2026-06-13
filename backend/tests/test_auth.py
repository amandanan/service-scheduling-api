def test_register_and_login(client):
    response = client.post("/auth/register", json={
        "full_name": "Amanda Teste",
        "birth_date": "1990-01-01",
        "cpf": "11144477735",
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
        "cpf": "11144477735",
        "phone": "11999999999",
        "email": "amanda@test.com",
        "password": "senha123",
    }

    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json={**payload, "cpf": "39053344705"})

    assert response.status_code == 400


def test_register_rejects_invalid_cpf(client):
    response = client.post("/auth/register", json={
        "full_name": "Amanda Teste",
        "birth_date": "1990-01-01",
        "cpf": "12345678900",
        "phone": "11999999999",
        "email": "amanda@test.com",
        "password": "senha123",
    })

    assert response.status_code == 422


def test_login_with_wrong_password(client):
    client.post("/auth/register", json={
        "full_name": "Amanda Teste",
        "birth_date": "1990-01-01",
        "cpf": "11144477735",
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


def _register_and_login(client, email="amanda@test.com"):
    client.post("/auth/register", json={
        "full_name": "Amanda Teste",
        "birth_date": "1990-01-01",
        "cpf": "11144477735",
        "phone": "11999999999",
        "email": email,
        "password": "senha123",
    })
    return client.post("/auth/login", data={
        "username": email,
        "password": "senha123",
    }).json()


def test_login_returns_refresh_token(client):
    tokens = _register_and_login(client)
    assert "access_token" in tokens
    assert "refresh_token" in tokens


def test_refresh_returns_new_access_token(client):
    tokens = _register_and_login(client)

    response = client.post("/auth/refresh", json={
        "refresh_token": tokens["refresh_token"],
    })

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body

    # the new access token works on a protected route
    headers = {"Authorization": f"Bearer {body['access_token']}"}
    assert client.get("/auth/me", headers=headers).status_code == 200


def test_refresh_rejects_access_token(client):
    tokens = _register_and_login(client)

    # an access token must not be accepted where a refresh token is expected
    response = client.post("/auth/refresh", json={
        "refresh_token": tokens["access_token"],
    })

    assert response.status_code == 401


def test_access_token_cannot_be_a_refresh_token(client):
    tokens = _register_and_login(client)

    # a refresh token must not authenticate API requests
    headers = {"Authorization": f"Bearer {tokens['refresh_token']}"}
    assert client.get("/auth/me", headers=headers).status_code == 401


def test_forgot_password_always_succeeds(client, sent_emails):
    _register_and_login(client)

    # existing account -> e-mail sent
    response = client.post("/auth/forgot-password", json={"email": "amanda@test.com"})
    assert response.status_code == 200
    assert len(sent_emails) == 1
    assert "redefinir-senha" in sent_emails[0]["body"]

    # unknown account -> same response, no e-mail
    response = client.post("/auth/forgot-password", json={"email": "naoexiste@test.com"})
    assert response.status_code == 200
    assert len(sent_emails) == 1


def test_reset_password_flow(client, sent_emails):
    _register_and_login(client)

    client.post("/auth/forgot-password", json={"email": "amanda@test.com"})

    # pull the reset token straight out of the e-mail link
    body = sent_emails[0]["body"]
    token = body.split("/redefinir-senha/")[1].split()[0].strip()

    response = client.post("/auth/reset-password", json={
        "token": token,
        "new_password": "novasenha456",
    })
    assert response.status_code == 200

    # old password no longer works, new one does
    assert client.post("/auth/login", data={
        "username": "amanda@test.com", "password": "senha123",
    }).status_code == 400
    assert client.post("/auth/login", data={
        "username": "amanda@test.com", "password": "novasenha456",
    }).status_code == 200


def test_reset_password_rejects_bad_token(client):
    response = client.post("/auth/reset-password", json={
        "token": "not-a-real-token",
        "new_password": "novasenha456",
    })
    assert response.status_code == 400
