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


def _staff(client, owner, email="recep@test.com", cpf="39053344705"):
    client.post("/staff/", json={
        "full_name": "Recep", "birth_date": "1990-01-01", "cpf": cpf,
        "phone": "11955554444", "email": email, "password": "senha123",
    }, headers=owner)
    return _login(client, email, "senha123")


SERVICE = {"name": "Consulta", "price": 100.0, "duration_minutes": 60}


def test_owner_creates_account_wide_service(client):
    owner = _owner(client)
    resp = client.post("/services/", json=SERVICE, headers=owner)
    assert resp.status_code == 200
    body = resp.json()
    assert body["professional_id"] is None
    assert body["is_active"] is True


def test_validation_rejects_bad_duration_or_price(client):
    owner = _owner(client)
    assert client.post("/services/", json={**SERVICE, "duration_minutes": 0}, headers=owner).status_code == 422
    assert client.post("/services/", json={**SERVICE, "price": -1}, headers=owner).status_code == 422


def test_professional_creates_own_service(client):
    owner = _owner(client)
    prof = _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    prof_h = _login(client, "ana@test.com")

    resp = client.post("/services/", json={**SERVICE, "description": "Avaliação inicial"}, headers=prof_h)
    assert resp.status_code == 200
    # the service is owned by the professional regardless of any payload
    assert resp.json()["professional_id"] == prof["id"]

    # it shows up in the professional's own list
    own = client.get("/services/", headers=prof_h).json()
    assert len(own) == 1


def test_professional_only_sees_own_services(client):
    owner = _owner(client)
    _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    prof_h = _login(client, "ana@test.com")

    # owner creates an account-wide service; professional creates their own
    client.post("/services/", json=SERVICE, headers=owner)
    client.post("/services/", json={**SERVICE, "name": "Retorno"}, headers=prof_h)

    own = client.get("/services/", headers=prof_h).json()
    assert [s["name"] for s in own] == ["Retorno"]

    # owner sees both
    all_services = client.get("/services/", headers=owner).json()
    assert len(all_services) == 2


def test_professional_cannot_touch_others_service(client):
    owner = _owner(client)
    _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    _professional_with_login(client, owner, "Bruno", "bruno@test.com", "16899555468")

    ana_h = _login(client, "ana@test.com")
    bruno_h = _login(client, "bruno@test.com")

    ana_service = client.post("/services/", json=SERVICE, headers=ana_h).json()

    # Bruno can neither see, edit nor inactivate Ana's service
    assert client.get(f"/services/{ana_service['id']}", headers=bruno_h).status_code == 404
    assert client.put(f"/services/{ana_service['id']}", json={**SERVICE, "is_active": True}, headers=bruno_h).status_code == 404
    assert client.delete(f"/services/{ana_service['id']}", headers=bruno_h).status_code == 404


def test_owner_can_manage_any_service(client):
    owner = _owner(client)
    _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    ana_h = _login(client, "ana@test.com")
    ana_service = client.post("/services/", json=SERVICE, headers=ana_h).json()

    # owner edits a professional's service
    resp = client.put(f"/services/{ana_service['id']}", json={
        "name": "Consulta Premium", "price": 150.0, "duration_minutes": 90, "is_active": True,
    }, headers=owner)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Consulta Premium"


def test_staff_cannot_write_services_but_can_read(client):
    owner = _owner(client)
    staff = _staff(client, owner)
    client.post("/services/", json=SERVICE, headers=owner)

    # staff reads the catalog (needed to create appointments)
    assert client.get("/services/", headers=staff).status_code == 200
    # but cannot create/edit
    assert client.post("/services/", json=SERVICE, headers=staff).status_code == 403


def test_inactive_service_hidden_from_public_booking(client):
    owner = _owner(client)
    service = client.post("/services/", json=SERVICE, headers=owner).json()

    me = client.get("/auth/me", headers=owner).json()
    slug = me["booking_slug"]

    assert len(client.get(f"/public/{slug}/services").json()) == 1

    # inactivate via soft delete
    client.delete(f"/services/{service['id']}", headers=owner)

    assert client.get(f"/public/{slug}/services").json() == []
