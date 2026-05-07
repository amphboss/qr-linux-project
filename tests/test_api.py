import os
import pytest
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


# ===== Защита =====

def test_generate_wrong_api_key():
    response = client.post(
        "/generate",
        json={"text": "test"},
        headers={"x-api-key": "wrongkey"}
    )

    assert response.status_code == 403


def test_generate_xss_characters():
    response = client.post(
        "/generate",
        json={"text": "<script>alert(1)</script>"},
        headers=HEADERS
    )

    assert response.status_code == 422


def test_generate_sql_injection():
    response = client.post(
        "/generate",
        json={"text": "'; DROP TABLE qr_codes; --"},
        headers=HEADERS
    )

    # должен либо отклонить (есть $), либо безопасно обработать через ORM
    assert response.status_code in (200, 422)


# ===== Параметры =====

def test_generate_custom_colors():
    response = client.post(
        "/generate",
        json={"text": "color", "fill_color": "#ff0000", "back_color": "#00ff00"},
        headers=HEADERS
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_generate_custom_box_size():
    response = client.post(
        "/generate",
        json={"text": "size", "box_size": 5},
        headers=HEADERS
    )

    assert response.status_code == 200


def test_generate_box_size_too_large():
    response = client.post(
        "/generate",
        json={"text": "big", "box_size": 100},
        headers=HEADERS
    )

    assert response.status_code == 422


def test_generate_box_size_zero():
    response = client.post(
        "/generate",
        json={"text": "zero", "box_size": 0},
        headers=HEADERS
    )

    assert response.status_code == 422


def test_generate_border_negative():
    response = client.post(
        "/generate",
        json={"text": "neg", "border": -1},
        headers=HEADERS
    )

    assert response.status_code == 422


def test_generate_border_too_large():
    response = client.post(
        "/generate",
        json={"text": "brd", "border": 50},
        headers=HEADERS
    )

    assert response.status_code == 422


def test_generate_error_level_h():
    response = client.post(
        "/generate",
        json={"text": "high error", "error": "H"},
        headers=HEADERS
    )

    assert response.status_code == 200


# ===== Файл =====

def test_generate_file_exists():
    response = client.post(
        "/generate",
        json={"text": "file check"},
        headers=HEADERS
    )

    data = response.json()
    assert os.path.isfile(data["file_path"])


# ===== История =====

def test_history_contains_fields():
    client.post(
        "/generate",
        json={"text": "fields test"},
        headers=HEADERS
    )

    response = client.get("/history", headers=HEADERS)
    data = response.json()

    assert len(data) > 0
    item = data[-1]
    assert "id" in item
    assert "text" in item
    assert "file_path" in item


def test_history_order_after_generate():
    client.post(
        "/generate",
        json={"text": "order test"},
        headers=HEADERS
    )

    response = client.get("/history", headers=HEADERS)
    data = response.json()
    texts = [item["text"] for item in data]

    assert "order test" in texts
