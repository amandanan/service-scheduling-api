


def _owner(client, email="dono@test.com", cpf="11144477735"):
    client.post("/auth/register", json={
        "full_name": "Dono", "birth_date": "1990-01-01", "cpf": cpf,
        "phone": "11999999999", "email": email, "password": "senha123",
    })
    login = client.post("/auth/login", data={"username": email, "password": "senha123"})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _login(client, email, password="prof123"):
    r = client.post("/auth/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _create_professional_with_login(client, owner, name="Dra. Ana", email="ana@test.com", cpf="39053344705"):
    prof = client.post("/professionals/", json={"name": name}, headers=owner).json()
    resp = client.post(f"/professionals/{prof['id']}/login", json={
        "email": email, "password": "prof123", "cpf": cpf,
        "phone": "11977777777", "birth_date": "1992-02-02",
    }, headers=owner)
    return prof, resp


def test_provision_professional_login(client):
    owner = _owner(client)
    prof, resp = _create_professional_with_login(client, owner)

    assert resp.status_code == 200
    assert resp.json()["user_id"] is not None

    # the professional can now sign in and is seen as a professional
    prof_headers = _login(client, "ana@test.com")
    me = client.get("/auth/me", headers=prof_headers).json()
    assert me["role"] == "professional"


def test_cannot_provision_login_twice(client):
    owner = _owner(client)
    prof, _ = _create_professional_with_login(client, owner)

    again = client.post(f"/professionals/{prof['id']}/login", json={
        "email": "outra@test.com", "password": "prof123", "cpf": "16899555468",
        "phone": "11955555555", "birth_date": "1992-02-02",
    }, headers=owner)
    assert again.status_code == 409


def test_professional_sees_own_profile_and_agenda(client):
    owner = _owner(client)
    prof, _ = _create_professional_with_login(client, owner)
    prof_headers = _login(client, "ana@test.com")

    me = client.get("/professionals/me", headers=prof_headers).json()
    assert me["id"] == prof["id"]
    assert me["name"] == "Dra. Ana"

    # an appointment for this professional shows in their agenda
    service = client.post("/services/", json={
        "name": "Consulta", "price": 100.0, "duration_minutes": 60,
    }, headers=owner).json()
    booking_client = client.post("/clients/", json={
        "full_name": "Paciente", "birth_date": "1990-01-01",
        "phone": "11966666666", "email": "pac@test.com",
    }, headers=owner).json()
    client.post("/appointments/", json={
        "client_id": booking_client["id"], "service_id": service["id"],
        "professional_id": prof["id"], "scheduled_at": "2026-09-15T09:00:00",
    }, headers=owner)

    agenda = client.get("/professionals/me/appointments", headers=prof_headers).json()
    assert len(agenda) == 1
    assert agenda[0]["professional_id"] == prof["id"]


def test_professional_agenda_is_scoped(client):
    owner = _owner(client)
    prof_a, _ = _create_professional_with_login(client, owner, name="Ana", email="ana@test.com", cpf="39053344705")
    prof_b = client.post("/professionals/", json={"name": "Bruno"}, headers=owner).json()

    service = client.post("/services/", json={
        "name": "Consulta", "price": 100.0, "duration_minutes": 60,
    }, headers=owner).json()
    c = client.post("/clients/", json={
        "full_name": "Paciente", "birth_date": "1990-01-01",
        "phone": "11966666666", "email": "pac@test.com",
    }, headers=owner).json()

    # appointment belongs to professional B, not A
    client.post("/appointments/", json={
        "client_id": c["id"], "service_id": service["id"],
        "professional_id": prof_b["id"], "scheduled_at": "2026-09-15T09:00:00",
    }, headers=owner)

    ana = _login(client, "ana@test.com")
    assert client.get("/professionals/me/appointments", headers=ana).json() == []


def test_professional_blocked_from_management(client):
    owner = _owner(client)
    _create_professional_with_login(client, owner)
    prof = _login(client, "ana@test.com")

    # management endpoints are off-limits to a professional
    assert client.get("/clients/", headers=prof).status_code == 403
    assert client.get("/professionals/", headers=prof).status_code == 403
    assert client.get("/dashboard/stats", headers=prof).status_code == 403
    assert client.post("/services/", json={
        "name": "X", "price": 10.0, "duration_minutes": 30,
    }, headers=prof).status_code == 403


def test_management_routes_still_work_for_owner(client):
    owner = _owner(client)
    # sanity: owner retains full access after the RBAC change
    assert client.get("/clients/", headers=owner).status_code == 200
    assert client.get("/dashboard/stats", headers=owner).status_code == 200


def test_me_appointments_requires_professional_role(client):
    owner = _owner(client)
    # an owner is not a professional -> 403 on the professional endpoint
    assert client.get("/professionals/me/appointments", headers=owner).status_code == 403
