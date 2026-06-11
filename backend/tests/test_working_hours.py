def test_get_default_working_hours(client, auth_headers):
    headers = auth_headers()

    response = client.get("/working-hours/", headers=headers)

    assert response.status_code == 200

    days = response.json()
    assert len(days) == 7

    sunday = next(d for d in days if d["weekday"] == 6)
    assert sunday["is_closed"] is True


def test_update_working_hours(client, auth_headers):
    headers = auth_headers()

    response = client.put("/working-hours/", json={
        "days": [
            {"weekday": 0, "start_time": "09:00", "end_time": "17:00", "is_closed": False},
            {"weekday": 1, "start_time": "09:00", "end_time": "17:00", "is_closed": False},
            {"weekday": 2, "start_time": "09:00", "end_time": "17:00", "is_closed": False},
            {"weekday": 3, "start_time": "09:00", "end_time": "17:00", "is_closed": False},
            {"weekday": 4, "start_time": "09:00", "end_time": "17:00", "is_closed": False},
            {"weekday": 5, "start_time": "00:00", "end_time": "00:00", "is_closed": True},
            {"weekday": 6, "start_time": "00:00", "end_time": "00:00", "is_closed": True},
        ]
    }, headers=headers)

    assert response.status_code == 200

    monday = next(d for d in response.json() if d["weekday"] == 0)
    assert monday["start_time"] == "09:00:00"
    assert monday["end_time"] == "17:00:00"


def test_available_slots_respect_working_hours(client, auth_headers):
    headers = auth_headers()

    client.put("/working-hours/", json={
        "days": [
            {"weekday": 0, "start_time": "09:00", "end_time": "12:00", "is_closed": False},
            {"weekday": 1, "start_time": "09:00", "end_time": "12:00", "is_closed": False},
            {"weekday": 2, "start_time": "09:00", "end_time": "12:00", "is_closed": False},
            {"weekday": 3, "start_time": "09:00", "end_time": "12:00", "is_closed": False},
            {"weekday": 4, "start_time": "09:00", "end_time": "12:00", "is_closed": False},
            {"weekday": 5, "start_time": "00:00", "end_time": "00:00", "is_closed": True},
            {"weekday": 6, "start_time": "00:00", "end_time": "00:00", "is_closed": True},
        ]
    }, headers=headers)

    service_response = client.post("/services/", json={
        "name": "Corte",
        "price": 50.0,
        "duration_minutes": 60,
    }, headers=headers)

    service_id = service_response.json()["id"]

    # 2026-06-15 is a Monday
    response = client.get(
        "/appointments/available-slots",
        params={"date": "2026-06-15", "service_id": service_id},
        headers=headers,
    )

    assert response.status_code == 200
    slots = response.json()
    assert "08:00" not in slots
    assert "09:00" in slots
    assert "11:00" in slots

    # 2026-06-21 is a Sunday -> closed
    response = client.get(
        "/appointments/available-slots",
        params={"date": "2026-06-21", "service_id": service_id},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == []
