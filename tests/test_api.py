from fastapi.testclient import TestClient

from app.main import app


def test_create_payload():
    with TestClient(app) as client:
        response = client.post(
            "/payload",
            json={
                "list_1": ["hello", "world"],
                "list_2": ["foo", "bar"],
            },
        )

    assert response.status_code == 200
    assert len(response.json()["id"]) == 64


def test_get_payload():
    with TestClient(app) as client:
        create_response = client.post(
            "/payload",
            json={
                "list_1": ["hello", "world"],
                "list_2": ["foo", "bar"],
            },
        )

        payload_id = create_response.json()["id"]

        get_response = client.get(f"/payload/{payload_id}")

    assert get_response.status_code == 200
    assert get_response.json() == {
        "output": "HELLO, FOO, WORLD, BAR"
    }


def test_get_unknown_payload():
    with TestClient(app) as client:
        response = client.get(
            "/payload/0000000000000000000000000000000000000000000000000000000000000000"
        )

    assert response.status_code == 404