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


def _booking_for(client, owner, professional_id, cpf="16899555468"):
    service = client.post("/services/", json={
        "name": "Consulta", "price": 100.0, "duration_minutes": 60,
    }, headers=owner).json()
    record = client.post("/clients/", json={
        "full_name": "Paciente", "birth_date": "1990-01-01",
        "phone": "11966666666", "email": f"{cpf}@test.com",
    }, headers=owner).json()
    return client.post("/appointments/", json={
        "client_id": record["id"], "service_id": service["id"],
        "professional_id": professional_id, "scheduled_at": "2026-09-15T09:00:00",
    }, headers=owner).json()


def test_professional_marks_own_completed(client):
    owner = _owner(client)
    ana = _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    appointment = _booking_for(client, owner, ana["id"])
    ana_h = _login(client, "ana@test.com")

    resp = client.patch(f"/appointments/{appointment['id']}/status",
                        json={"status": "completed"}, headers=ana_h)
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


def test_professional_marks_own_no_show(client):
    owner = _owner(client)
    ana = _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    appointment = _booking_for(client, owner, ana["id"])
    ana_h = _login(client, "ana@test.com")

    resp = client.patch(f"/appointments/{appointment['id']}/status",
                        json={"status": "no_show"}, headers=ana_h)
    assert resp.status_code == 200
    assert resp.json()["status"] == "no_show"


def test_professional_cannot_set_other_statuses(client):
    owner = _owner(client)
    ana = _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    appointment = _booking_for(client, owner, ana["id"])
    ana_h = _login(client, "ana@test.com")

    # a professional can't move it back to confirmed/scheduled
    resp = client.patch(f"/appointments/{appointment['id']}/status",
                        json={"status": "confirmed"}, headers=ana_h)
    assert resp.status_code == 403


def test_professional_cannot_touch_others_appointment(client):
    owner = _owner(client)
    ana = _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    _professional_with_login(client, owner, "Bruno", "bruno@test.com", "39053344705")
    appointment = _booking_for(client, owner, ana["id"])  # Ana's appointment
    bruno_h = _login(client, "bruno@test.com")

    resp = client.patch(f"/appointments/{appointment['id']}/status",
                        json={"status": "completed"}, headers=bruno_h)
    assert resp.status_code == 404


def test_management_still_sets_any_status(client):
    owner = _owner(client)
    ana = _professional_with_login(client, owner, "Ana", "ana@test.com", "52998224725")
    appointment = _booking_for(client, owner, ana["id"])

    # owner retains full control, including confirmed
    resp = client.patch(f"/appointments/{appointment['id']}/status",
                        json={"status": "confirmed"}, headers=owner)
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"
