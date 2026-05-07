import requests
from client.config import API_GENERATE, API_HISTORY, API_HEALTH, HEADERS


class APIClient:
    """HTTP-клиент для взаимодействия с QR-сервером."""

    @staticmethod
    def check_server() -> bool:
        """Ping сервера с таймаутом 2 сек. True — доступен, False — нет."""
        try:
            requests.get(API_HEALTH, timeout=2)
            return True
        except Exception:
            return False

    @staticmethod
    def generate(data: dict) -> requests.Response:
        """POST-запрос на генерацию QR-кода. Возвращает объект Response."""
        return requests.post(API_GENERATE, json=data, headers=HEADERS)

    @staticmethod
    def get_history() -> list:
        """GET-запрос истории генераций. Возвращает список записей."""
        r = requests.get(API_HISTORY, headers=HEADERS)
        return r.json()
