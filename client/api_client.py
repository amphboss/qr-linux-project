import requests
from client.config import API_GENERATE, API_HISTORY, API_HEALTH, HEADERS


class APIClient:
    """HTTP-клиент для взаимодействия с QR-сервером."""

    @staticmethod
    def check_server() -> bool:
        try:
            requests.get(API_HEALTH, timeout=2)
            return True
        except Exception:
            return False

    @staticmethod
    def generate(data: dict) -> requests.Response:
        return requests.post(API_GENERATE, json=data, headers=HEADERS)

    @staticmethod
    def get_history() -> list:
        r = requests.get(API_HISTORY, headers=HEADERS)
        return r.json()
