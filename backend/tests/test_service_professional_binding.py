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


def _professional_with_login(client, owner, name, email, cpf):
    prof = client.post("/professionals/", json={"name": name}, headers=owner).json()
    client.post(f"/professionals/{prof['id']}/login", json={
        "email": email, "password": "prof123", "cpf": cpf,
        "phone": "11977777777", "birth_date": "1992-02-02",
    }, headers=owner)
    return prof


def _client_record(client, owner):
    return client.post("/clients/", json={
        "full_name": "Paciente", "birth_date": "1990-01-01",
        "phone": "11966666666", "email": "pac@test.com",
    }, headers=owner).json()


WHEN = "2026-09-15T09:00:00"


def test_owner_books_professional_owned_service_with_owner(client):
    owner = _owner(client)
    ana = _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    ana_h = _login(client, "ana@test.com")
    service = client.post("/services/", json={
        "name": "Consulta", "price": 100.0, "duration_minutes": 60,
    }, headers=ana_h).json()
    record = _client_record(client, owner)

    # booking Ana's service with Ana -> ok
    ok = client.post("/appointments/", json={
        "client_id": record["id"], "service_id": service["id"],
        "professional_id": ana["id"], "scheduled_at": WHEN,
    }, headers=owner)
    assert ok.status_code == 200


def test_booking_rejects_wrong_professional_for_service(client):
    owner = _owner(client)
    _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    bruno = client.post("/professionals/", json={"name": "Bruno"}, headers=owner).json()
    ana_h = _login(client, "ana@test.com")
    service = client.post("/services/", json={
        "name": "Consulta", "price": 100.0, "duration_minutes": 60,
    }, headers=ana_h).json()
    record = _client_record(client, owner)

    # Ana's service booked with Bruno -> 400
    resp = client.post("/appointments/", json={
        "client_id": record["id"], "service_id": service["id"],
        "professional_id": bruno["id"], "scheduled_at": WHEN,
    }, headers=owner)
    assert resp.status_code == 400


def test_account_wide_service_works_with_any_professional(client):
    owner = _owner(client)
    bruno = client.post("/professionals/", json={"name": "Bruno"}, headers=owner).json()
    # account-wide service (created by owner, professional_id null)
    service = client.post("/services/", json={
        "name": "Corte", "price": 50.0, "duration_minutes": 60,
    }, headers=owner).json()
    record = _client_record(client, owner)

    ok = client.post("/appointments/", json={
        "client_id": record["id"], "service_id": service["id"],
        "professional_id": bruno["id"], "scheduled_at": WHEN,
    }, headers=owner)
    assert ok.status_code == 200


def test_available_slots_empty_for_wrong_professional(client):
    owner = _owner(client)
    ana = _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    bruno = client.post("/professionals/", json={"name": "Bruno"}, headers=owner).json()
    ana_h = _login(client, "ana@test.com")
    service = client.post("/services/", json={
        "name": "Consulta", "price": 100.0, "duration_minutes": 60,
    }, headers=ana_h).json()

    # slots with the right professional exist...
    with_ana = client.get("/appointments/available-slots", params={
        "date": "2026-09-15", "service_id": service["id"], "professional_id": ana["id"],
    }, headers=owner).json()
    assert len(with_ana) > 0

    # ...but the wrong professional gets none
    with_bruno = client.get("/appointments/available-slots", params={
        "date": "2026-09-15", "service_id": service["id"], "professional_id": bruno["id"],
    }, headers=owner).json()
    assert with_bruno == []


def test_public_booking_respects_binding(client):
    owner = _owner(client)
    ana = _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    bruno = client.post("/professionals/", json={"name": "Bruno"}, headers=owner).json()
    ana_h = _login(client, "ana@test.com")
    service = client.post("/services/", json={
        "name": "Consulta", "price": 100.0, "duration_minutes": 60,
    }, headers=ana_h).json()

    slug = client.get("/auth/me", headers=owner).json()["booking_slug"]

    payload = {
        "full_name": "Cliente", "birth_date": "1995-05-05", "cpf": "16899555468",
        "phone": "11977777777", "email": "cli@test.com",
        "service_id": service["id"], "scheduled_at": WHEN,
    }

    # wrong professional via public booking -> 400
    bad = client.post(f"/public/{slug}/appointments", json={**payload, "professional_id": bruno["id"]})
    assert bad.status_code == 400

    # right professional -> ok
    good = client.post(f"/public/{slug}/appointments", json={**payload, "professional_id": ana["id"]})
    assert good.status_code == 200


def test_booking_rejects_inactive_professional(client):
    owner = _owner(client)
    bruno = client.post("/professionals/", json={"name": "Bruno", "is_active": False}, headers=owner).json()
    service = client.post("/services/", json={
        "name": "Corte", "price": 50.0, "duration_minutes": 60,
    }, headers=owner).json()
    record = _client_record(client, owner)

    resp = client.post("/appointments/", json={
        "client_id": record["id"], "service_id": service["id"],
        "professional_id": bruno["id"], "scheduled_at": WHEN,
    }, headers=owner)
    assert resp.status_code == 404
