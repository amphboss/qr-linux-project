# QR Code Generator — Клиент-серверное приложение

Клиент-серверное приложение для генерации QR-кодов в экосистеме Linux.
Курсовой проект по дисциплине «Системное программирование».

## Требования

- Python 3.10+
- Linux (Ubuntu / Debian / Fedora)
- Для GUI: установленный `python3-tk` (`sudo apt install python3-tk`)

## Установка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/amphboss/qr-linux-project.git
cd qr-linux-project

# 2. Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt
```

## Запуск

```bash
# Терминал 1 — запуск сервера
python run.py

# Терминал 2 — запуск клиента
python run_client.py
```

Сервер запускается на `http://127.0.0.1:8000`. Клиент подключается к нему автоматически.

## Запуск через Docker

```bash
cd docker
docker-compose up --build
```

## Запуск тестов

```bash
python -m pytest tests/ -v
```

## API

Все запросы требуют заголовок `x-api-key: mysecretkey`.

### POST /generate

Генерация QR-кода.

**Запрос:**
```json
{
  "text": "https://example.com",
  "fill_color": "#000000",
  "back_color": "#ffffff",
  "box_size": 10,
  "border": 4,
  "error": "M"
}
```

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|-------------|----------|
| text | string | — | Текст или URL (обязательный, до 200 символов) |
| fill_color | string | #000000 | Цвет QR-кода |
| back_color | string | #ffffff | Цвет фона |
| box_size | int | 10 | Размер модуля (1–50) |
| border | int | 4 | Ширина рамки (0–20) |
| error | string | M | Уровень коррекции (L / M / Q / H) |

**Ответ (200):**
```json
{
  "status": "success",
  "file_path": "generated_qr/qr_20260506_152010.png"
}
```

### GET /history

Получение истории генерации.

**Ответ (200):**
```json
[
  {"id": 1, "text": "hello", "file_path": "generated_qr/qr_20260506_152010.png"},
  {"id": 2, "text": "https://github.com", "file_path": "generated_qr/qr_20260506_152027.png"}
]
```

### Интерактивная документация

После запуска сервера доступна по адресу: `http://127.0.0.1:8000/docs` (Swagger UI).

## Структура проекта

```
qr-linux-project/
├── client/                     # Клиентский модуль (GUI)
│   ├── __init__.py
│   ├── app.py                  # Построение интерфейса (виджеты)
│   ├── config.py               # Константы: URL API, темы оформления
│   ├── api_client.py           # HTTP-клиент (запросы к серверу)
│   ├── theme.py                # Управление темой (ThemeMixin)
│   └── handlers.py             # Обработчики событий (HandlersMixin)
│
├── server/                     # Серверный модуль (REST API)
│   ├── __init__.py
│   ├── main.py                 # Создание FastAPI-приложения, логирование
│   ├── routes.py               # Эндпоинты /generate и /history
│   ├── schemas.py              # Pydantic-модели с валидацией
│   ├── auth.py                 # Аутентификация по API-ключу
│   ├── models.py               # SQLAlchemy-модель QRCode
│   └── db/
│       └── database.py         # Подключение к SQLite
│
├── shared/                     # Общий модуль
│   ├── __init__.py
│   └── qr_generator.py        # Пользовательская библиотека генерации QR
│
├── tests/                      # Тесты (pytest)
│   ├── __init__.py
│   ├── test_api.py             # 19 тестов API
│   └── test_qr_generator.py   # 17 тестов генератора
│
├── docker/                     # Docker-конфигурация
│   ├── docker-compose.yml
│   ├── server.Dockerfile
│   └── client.Dockerfile
│
├── logs/                       # Журналы (server.log, client.log)
├── generated_qr/               # Сгенерированные QR-коды
├── run.py                      # Точка входа: сервер
├── run_client.py               # Точка входа: клиент
├── requirements.txt            # Зависимости с фиксированными версиями
└── README.md
```

## Основные функции

| Модуль | Функция / Класс | Описание |
|--------|-----------------|----------|
| `shared/qr_generator.py` | `QRGenerator.generate()` | Генерация QR-кода с заданными параметрами, сохранение в PNG |
| `server/routes.py` | `generate_qr()` | POST-эндпоинт: генерация + запись в БД |
| `server/routes.py` | `get_history()` | GET-эндпоинт: список всех сгенерированных QR |
| `server/auth.py` | `verify_api_key()` | Проверка API-ключа в заголовке запроса |
| `server/schemas.py` | `QRRequest` | Валидация входных данных (текст, размеры, цвета) |
| `client/api_client.py` | `APIClient.generate()` | HTTP-запрос на генерацию QR |
| `client/api_client.py` | `APIClient.get_history()` | HTTP-запрос на получение истории |
| `client/api_client.py` | `APIClient.check_server()` | Проверка доступности сервера |
| `client/handlers.py` | `HandlersMixin` | Обработчики: генерация, сохранение, история |
| `client/theme.py` | `ThemeMixin` | Переключение и применение светлой/тёмной темы |
| `client/app.py` | `QRApp` | Главный класс GUI-приложения |

## Технологический стек

- **Клиент:** Python, CustomTkinter, Requests, Pillow
- **Сервер:** Python, FastAPI, SQLAlchemy, SQLite, Uvicorn
- **Общее:** qrcode (пользовательская библиотека-обёртка)
- **Тесты:** pytest, FastAPI TestClient
- **Деплой:** Docker, Docker Compose
- **VCS:** Git, GitHub
