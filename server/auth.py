from fastapi import HTTPException, Header

# Секретный ключ для аутентификации клиентов
API_KEY = "mysecretkey"


def verify_api_key(x_api_key: str = Header(...)):
    """Проверка API-ключа из заголовка x-api-key. 403 при несовпадении."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
