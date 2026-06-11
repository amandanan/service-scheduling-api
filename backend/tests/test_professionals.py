def test_default_professional_created_on_register(client, auth_headers):
    headers = auth_headers()

    response = client.get("/professionals/", headers=headers)

    assert response.status_code == 200
    professionals = response.json()
    assert len(professionals) == 1
    assert professionals[0]["is_active"] is True


def test_create_and_list_professional(client, auth_headers):
    headers = auth_headers()

    response = client.post("/professionals/", json={
        "name": "Maria",
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["name"] == "Maria"

    response = client.get("/professionals/", headers=headers)
    assert len(response.json()) == 2


def test_update_professional(client, auth_headers, first_professional_id):
    headers = auth_headers()
    professional_id = first_professional_id(headers)

    response = client.put(f"/professionals/{professional_id}", json={
        "name": "Novo Nome",
        "is_active": False,
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["name"] == "Novo Nome"
    assert response.json()["is_active"] is False


def test_delete_professional(client, auth_headers):
    headers = auth_headers()

    created = client.post("/professionals/", json={"name": "Temp"}, headers=headers)
    professional_id = created.json()["id"]

    response = client.delete(f"/professionals/{professional_id}", headers=headers)
    assert response.status_code == 200

    remaining = client.get("/professionals/", headers=headers).json()
    assert all(p["id"] != professional_id for p in remaining)


def test_professionals_are_isolated_per_user(client, auth_headers):
    headers_a = auth_headers(email="a@test.com", cpf="11144477735")
    headers_b = auth_headers(email="b@test.com", cpf="16899555468")

    client.post("/professionals/", json={"name": "Da A"}, headers=headers_a)

    # user B only sees their own default professional, not user A's
    response = client.get("/professionals/", headers=headers_b)
    names = [p["name"] for p in response.json()]
    assert "Da A" not in names


def test_cannot_update_other_users_professional(client, auth_headers, first_professional_id):
    headers_a = auth_headers(email="a@test.com", cpf="11144477735")
    headers_b = auth_headers(email="b@test.com", cpf="16899555468")

    professional_a = first_professional_id(headers_a)

    response = client.put(f"/professionals/{professional_a}", json={
        "name": "Hack",
        "is_active": True,
    }, headers=headers_b)

    assert response.status_code == 404


def test_inactive_professional_hidden_from_public(client, auth_headers):
    headers = auth_headers()

    extra = client.post("/professionals/", json={"name": "Visivel"}, headers=headers)
    assert extra.status_code == 200

    me = client.get("/auth/me", headers=headers).json()
    slug = me["booking_slug"]

    # deactivate the default professional
    professionals = client.get("/professionals/", headers=headers).json()
    default = next(p for p in professionals if p["name"] != "Visivel")
    client.put(f"/professionals/{default['id']}", json={
        "name": default["name"],
        "is_active": False,
    }, headers=headers)

    public = client.get(f"/public/{slug}/professionals").json()
    names = [p["name"] for p in public]

    assert "Visivel" in names
    assert default["name"] not in names
