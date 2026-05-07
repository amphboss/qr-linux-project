import logging
import os
from fastapi import FastAPI

from server.db.database import engine
from server.models import Base
from server.routes import router

# ===== ЛОГИ =====
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/server.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ===== ПРИЛОЖЕНИЕ =====
app = FastAPI(title="QR Generator API")

Base.metadata.create_all(bind=engine)

app.include_router(router)