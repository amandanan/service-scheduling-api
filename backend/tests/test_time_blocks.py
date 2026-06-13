def _service(client, headers):
    return client.post("/services/", json={
        "name": "Corte",
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers).json()["id"]


def _slots(client, headers, service_id, professional_id, date="2026-06-15"):
    return client.get(
        "/appointments/available-slots",
        params={"date": date, "service_id": service_id, "professional_id": professional_id},
        headers=headers,
    ).json()


def test_create_and_list_block(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)

    response = client.post("/blocks/", json={
        "professional_id": professional_id,
        "start_at": "2026-06-15T12:00:00",
        "end_at": "2026-06-15T13:00:00",
        "reason": "Almoço",
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["reason"] == "Almoço"

    listed = client.get("/blocks/", params={"professional_id": professional_id}, headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_block_removes_overlapping_slots(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)
    service_id = _service(client, headers)

    # 14:00 is available before the block
    before = _slots(client, headers, service_id, professional_id)
    assert "14:00" in before

    client.post("/blocks/", json={
        "professional_id": professional_id,
        "start_at": "2026-06-15T14:00:00",
        "end_at": "2026-06-15T15:00:00",
    }, headers=headers)

    after = _slots(client, headers, service_id, professional_id)
    assert "14:00" not in after
    # a slot well outside the block stays available
    assert "16:00" in after


def test_full_day_block_returns_no_slots(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)
    service_id = _service(client, headers)

    client.post("/blocks/", json={
        "professional_id": professional_id,
        "start_at": "2026-06-15T00:00:00",
        "end_at": "2026-06-15T23:59:59",
        "reason": "Folga",
    }, headers=headers)

    assert _slots(client, headers, service_id, professional_id) == []


def test_delete_block_restores_slots(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)
    service_id = _service(client, headers)

    block = client.post("/blocks/", json={
        "professional_id": professional_id,
        "start_at": "2026-06-15T14:00:00",
        "end_at": "2026-06-15T15:00:00",
    }, headers=headers).json()

    assert "14:00" not in _slots(client, headers, service_id, professional_id)

    client.delete(f"/blocks/{block['id']}", headers=headers)

    assert "14:00" in _slots(client, headers, service_id, professional_id)


def test_block_rejects_invalid_range(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)

    response = client.post("/blocks/", json={
        "professional_id": professional_id,
        "start_at": "2026-06-15T15:00:00",
        "end_at": "2026-06-15T14:00:00",
    }, headers=headers)

    assert response.status_code == 422


def test_block_requires_own_professional(client, auth_headers):
    owner = auth_headers(email="owner1@test.com", cpf="11144477735")
    other = auth_headers(email="owner2@test.com", cpf="39053344705")

    other_prof = client.get("/professionals/", headers=other).json()[0]["id"]

    response = client.post("/blocks/", json={
        "professional_id": other_prof,
        "start_at": "2026-06-15T14:00:00",
        "end_at": "2026-06-15T15:00:00",
    }, headers=owner)

    assert response.status_code == 404
