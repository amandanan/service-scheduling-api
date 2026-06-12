def _auth(client):
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
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_settings_defaults(client):
    headers = _auth(client)

    response = client.get("/settings/", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["monthly_goal"] == 10000.0
    assert body["daily_capacity"] == 20
    assert body["client_term_singular"] == "Cliente"
    assert body["client_term_plural"] == "Clientes"
    assert body["full_name"] == "Studio Bella"
    assert body["booking_slug"]


def test_settings_update(client):
    headers = _auth(client)

    response = client.put("/settings/", json={
        "monthly_goal": 25000,
        "daily_capacity": 8,
        "client_term_singular": "Paciente",
        "client_term_plural": "Pacientes",
    }, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["monthly_goal"] == 25000
    assert body["daily_capacity"] == 8
    assert body["client_term_plural"] == "Pacientes"

    # persisted
    again = client.get("/settings/", headers=headers).json()
    assert again["client_term_singular"] == "Paciente"


def test_settings_validation(client):
    headers = _auth(client)

    # capacity must be >= 1
    response = client.put("/settings/", json={
        "monthly_goal": 1000,
        "daily_capacity": 0,
        "client_term_singular": "Cliente",
        "client_term_plural": "Clientes",
    }, headers=headers)
    assert response.status_code == 422


def test_settings_feeds_dashboard_goal(client):
    headers = _auth(client)

    client.put("/settings/", json={
        "monthly_goal": 100,
        "daily_capacity": 4,
        "client_term_singular": "Cliente",
        "client_term_plural": "Clientes",
    }, headers=headers)

    stats = client.get("/dashboard/stats", headers=headers).json()
    assert stats["kpis"]["monthly_goal"] == 100


def test_settings_requires_auth(client):
    assert client.get("/settings/").status_code == 401
