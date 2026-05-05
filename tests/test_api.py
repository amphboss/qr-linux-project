from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

API_KEY = "mysecretkey"
HEADERS = {"x-api-key": API_KEY}


def test_generate_qr_success():
    response = client.post(
        "/generate",
        json={"text": "test qr"},
        headers=HEADERS
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "file_path" in data


def test_generate_qr_no_api_key():
    response = client.post(
        "/generate",
        json={"text": "test"}
    )

    assert response.status_code == 422 or response.status_code == 403


def test_generate_qr_invalid_text():
    response = client.post(
        "/generate",
        json={"text": ""},
        headers=HEADERS
    )

    assert response.status_code == 422


def test_generate_qr_too_long():
    long_text = "a" * 300

    response = client.post(
        "/generate",
        json={"text": long_text},
        headers=HEADERS
    )

    assert response.status_code == 422


def test_history():
    # сначала создаём QR
    client.post(
        "/generate",
        json={"text": "history test"},
        headers=HEADERS
    )

    response = client.get("/history", headers=HEADERS)

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0


def test_history_no_api_key():
    response = client.get("/history")

    assert response.status_code == 422 or response.status_code == 403
