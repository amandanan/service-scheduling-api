def _register_owner(client, email, cpf):
    client.post("/auth/register", json={
        "full_name": "Dono " + email,
        "birth_date": "1990-01-01",
        "cpf": cpf,
        "phone": "11999999999",
        "email": email,
        "password": "senha123",
    })
    login = client.post("/auth/login", data={
        "username": email,
        "password": "senha123",
    })
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _login(client, email, password):
    login = client.post("/auth/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _create_staff(client, owner_headers, email="recep@test.com", cpf="39053344705"):
    return client.post("/staff/", json={
        "full_name": "Recepcionista",
        "birth_date": "1995-05-05",
        "cpf": cpf,
        "phone": "11977777777",
        "email": email,
        "password": "senha123",
    }, headers=owner_headers)


def test_owner_creates_and_lists_staff(client):
    owner = _register_owner(client, "owner@test.com", "11144477735")

    response = _create_staff(client, owner)
    assert response.status_code == 200
    assert response.json()["role"] == "staff"

    listed = client.get("/staff/", headers=owner)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_staff_can_login_and_has_staff_role(client):
    owner = _register_owner(client, "owner@test.com", "11144477735")
    _create_staff(client, owner)

    staff = _login(client, "recep@test.com", "senha123")
    me = client.get("/auth/me", headers=staff).json()
    assert me["role"] == "staff"


def test_staff_sees_owner_data(client):
    owner = _register_owner(client, "owner@test.com", "11144477735")

    # owner creates a client
    client.post("/clients/", json={
        "full_name": "Cliente do Dono",
        "birth_date": "1990-01-01",
        "cpf": "16899555468",
        "phone": "11966666666",
        "email": "cli@test.com",
    }, headers=owner)

    _create_staff(client, owner)
    staff = _login(client, "recep@test.com", "senha123")

    # staff sees the same client list as the owner
    staff_clients = client.get("/clients/", headers=staff).json()
    assert len(staff_clients) == 1
    assert staff_clients[0]["full_name"] == "Cliente do Dono"


def test_staff_creates_data_under_owner_account(client):
    owner = _register_owner(client, "owner@test.com", "11144477735")
    _create_staff(client, owner)
    staff = _login(client, "recep@test.com", "senha123")

    # staff registers a client
    created = client.post("/clients/", json={
        "full_name": "Cliente da Recep",
        "birth_date": "1990-01-01",
        "cpf": "16899555468",
        "phone": "11966666666",
        "email": "cli2@test.com",
    }, headers=staff)
    assert created.status_code == 200

    # the owner sees it too — it belongs to the account, not the staff user
    owner_clients = client.get("/clients/", headers=owner).json()
    assert any(c["full_name"] == "Cliente da Recep" for c in owner_clients)


def test_accounts_are_isolated(client):
    owner_a = _register_owner(client, "a@test.com", "11144477735")
    owner_b = _register_owner(client, "b@test.com", "39053344705")

    client.post("/clients/", json={
        "full_name": "Cliente A",
        "birth_date": "1990-01-01",
        "cpf": "16899555468",
        "phone": "11966666666",
        "email": "clia@test.com",
    }, headers=owner_a)

    # owner B must not see owner A's clients
    assert client.get("/clients/", headers=owner_b).json() == []


def test_staff_cannot_manage_staff(client):
    owner = _register_owner(client, "owner@test.com", "11144477735")
    _create_staff(client, owner)
    staff = _login(client, "recep@test.com", "senha123")

    # listing and creating staff is owner-only
    assert client.get("/staff/", headers=staff).status_code == 403

    response = client.post("/staff/", json={
        "full_name": "Outro",
        "birth_date": "1995-05-05",
        "cpf": "16899555468",
        "phone": "11977777777",
        "email": "outro@test.com",
        "password": "senha123",
    }, headers=staff)
    assert response.status_code == 403


def test_staff_cannot_edit_settings(client):
    owner = _register_owner(client, "owner@test.com", "11144477735")
    _create_staff(client, owner)
    staff = _login(client, "recep@test.com", "senha123")

    response = client.put("/settings/", json={
        "monthly_goal": 5000,
        "daily_capacity": 10,
        "client_term_singular": "Paciente",
        "client_term_plural": "Pacientes",
    }, headers=staff)
    assert response.status_code == 403


def test_staff_reads_owner_settings(client):
    owner = _register_owner(client, "owner@test.com", "11144477735")

    client.put("/settings/", json={
        "monthly_goal": 5000,
        "daily_capacity": 10,
        "client_term_singular": "Paciente",
        "client_term_plural": "Pacientes",
    }, headers=owner)

    _create_staff(client, owner)
    staff = _login(client, "recep@test.com", "senha123")

    settings = client.get("/settings/", headers=staff).json()
    assert settings["client_term_plural"] == "Pacientes"
    assert settings["monthly_goal"] == 5000


def test_delete_staff(client):
    owner = _register_owner(client, "owner@test.com", "11144477735")
    created = _create_staff(client, owner).json()

    response = client.delete(f"/staff/{created['id']}", headers=owner)
    assert response.status_code == 200

    assert client.get("/staff/", headers=owner).json() == []
