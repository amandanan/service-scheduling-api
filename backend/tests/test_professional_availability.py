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


def test_professional_sets_own_working_hours(client):
    owner = _owner(client)
    _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    ana = _login(client, "ana@test.com")

    hours = client.get("/professionals/me/working-hours", headers=ana)
    assert hours.status_code == 200
    assert len(hours.json()) == 7  # one row per weekday

    # close Sunday (weekday 6)
    payload = {"days": [{"weekday": 6, "start_time": "09:00", "end_time": "18:00", "is_closed": True}]}
    resp = client.put("/professionals/me/working-hours", json=payload, headers=ana)
    assert resp.status_code == 200

    sunday = [d for d in resp.json() if d["weekday"] == 6][0]
    assert sunday["is_closed"] is True


def test_professional_manages_own_blocks(client):
    owner = _owner(client)
    _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    ana = _login(client, "ana@test.com")

    created = client.post("/professionals/me/blocks", json={
        "start_at": "2026-07-20T12:00:00",
        "end_at": "2026-07-20T13:00:00",
        "reason": "Almoço",
    }, headers=ana)
    assert created.status_code == 200

    blocks = client.get("/professionals/me/blocks", headers=ana).json()
    assert len(blocks) == 1
    assert blocks[0]["reason"] == "Almoço"

    deleted = client.delete(f"/professionals/me/blocks/{created.json()['id']}", headers=ana)
    assert deleted.status_code == 200
    assert client.get("/professionals/me/blocks", headers=ana).json() == []


def test_block_rejects_invalid_range(client):
    owner = _owner(client)
    _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    ana = _login(client, "ana@test.com")

    resp = client.post("/professionals/me/blocks", json={
        "start_at": "2026-07-20T13:00:00",
        "end_at": "2026-07-20T12:00:00",
    }, headers=ana)
    assert resp.status_code == 422


def test_professional_cannot_delete_others_block(client):
    owner = _owner(client)
    _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    _professional_with_login(client, owner, "Bruno", "bruno@test.com", "16899555468")
    ana = _login(client, "ana@test.com")
    bruno = _login(client, "bruno@test.com")

    ana_block = client.post("/professionals/me/blocks", json={
        "start_at": "2026-07-20T12:00:00", "end_at": "2026-07-20T13:00:00",
    }, headers=ana).json()

    # Bruno can't see or delete Ana's block
    assert client.get("/professionals/me/blocks", headers=bruno).json() == []
    assert client.delete(f"/professionals/me/blocks/{ana_block['id']}", headers=bruno).status_code == 404


def test_my_availability_endpoints_require_professional(client):
    owner = _owner(client)
    # an owner is not a professional
    assert client.get("/professionals/me/working-hours", headers=owner).status_code == 403
    assert client.get("/professionals/me/blocks", headers=owner).status_code == 403


def test_professional_block_removes_public_slots(client):
    owner = _owner(client)
    prof = _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    ana = _login(client, "ana@test.com")

    # a service to query availability against
    service = client.post("/services/", json={
        "name": "Consulta", "price": 100.0, "duration_minutes": 60,
    }, headers=ana).json()

    me = client.get("/auth/me", headers=owner).json()
    slug = me["booking_slug"]
    date = "2026-07-20"  # a Monday

    before = client.get(
        f"/public/{slug}/available-slots",
        params={"date": date, "service_id": service["id"], "professional_id": prof["id"]},
    ).json()
    assert len(before) > 0

    # the professional blocks the whole day from their own panel
    client.post("/professionals/me/blocks", json={
        "start_at": f"{date}T00:00:00", "end_at": f"{date}T23:59:59", "reason": "Folga",
    }, headers=ana)

    after = client.get(
        f"/public/{slug}/available-slots",
        params={"date": date, "service_id": service["id"], "professional_id": prof["id"]},
    ).json()
    assert after == []
