"""
Tests for app.py — the HTTP layer.

Use Flask's built-in test client — no real server needed.
"""

import pytest

from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health_returns_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_find_parking_rejects_missing_fields(client):
    res = client.post("/find-parking", json={"start": [51.13, 71.43]})
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_input"


def test_find_parking_rejects_wrong_types(client):
    res = client.post(
        "/find-parking",
        json={"start": "not-coords", "dest": [51.12, 71.42]},
    )
    assert res.status_code == 400


@pytest.mark.slow
def test_find_parking_returns_results(client):
    from unittest.mock import patch

    fake = [
        {
            "id": "a",
            "coords": (51.126, 71.429),
            "name": "A",
            "address": "",
            "capacity": 100,
            "price": "100 тнг./час",
            "tags": [],
        },
        {
            "id": "b",
            "coords": (51.124, 71.427),
            "name": "B",
            "address": "",
            "capacity": 50,
            "price": None,
            "tags": [],
        },
    ]
    with patch("src.finder.get_parkings_near", return_value=fake):
        res = client.post(
            "/find-parking",
            json={"start": [51.13, 71.43], "dest": [51.125, 71.428]},
        )
    assert res.status_code == 200
    body = res.get_json()
    assert "parkings" in body
    assert len(body["parkings"]) <= 5
