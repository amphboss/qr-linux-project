import logging
import os
from fastapi import FastAPI

from server.db.database import engine
from server.models import Base
from server.routes import router

# Создание папки для логов (если не существует)
if not os.path.exists("logs"):
    os.makedirs("logs")

# Настройка журналирования в файл
logging.basicConfig(
    filename="logs/server.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Создание FastAPI-приложения
app = FastAPI(title="QR Generator API")

# Создание таблиц в БД (если ещё не существуют)
Base.metadata.create_all(bind=engine)

# Подключение маршрутов (/generate, /history)
app.include_router(router)