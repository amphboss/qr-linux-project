import logging
import os
import re
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, field_validator

from shared.qr_generator import QRGenerator
from server.db.database import SessionLocal, engine
from server.models import QRCode, Base

# ===== ЛОГИ =====
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/server.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ===== НАСТРОЙКИ =====
API_KEY = "mysecretkey"

# ===== APP =====
app = FastAPI(title="QR Generator API")

Base.metadata.create_all(bind=engine)

qr_generator = QRGenerator()


# ===== ВАЛИДАЦИЯ =====
class QRRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, value):
        if not value or not value.strip():
            raise ValueError("Пустая строка")

        if len(value) > 200:
            raise ValueError("Слишком длинный текст")

        if re.search(r"[<>$]", value):
            raise ValueError("Недопустимые символы")

        return value.strip()


# ===== API KEY DEPENDENCY =====
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        logger.warning("Неверный API ключ")
        raise HTTPException(status_code=403, detail="Forbidden")


# ===== ROUTES =====
@app.post("/generate")
def generate_qr(
    request: QRRequest,
    _: None = Depends(verify_api_key)
):
    db = SessionLocal()

    logger.info(f"Генерация QR: {request.text}")

    path = qr_generator.generate(request.text)

    qr_record = QRCode(
        text=request.text,
        file_path=path
    )

    db.add(qr_record)
    db.commit()

    db.close()

    return {
        "status": "success",
        "file_path": path
    }


@app.get("/history")
def get_history(
    _: None = Depends(verify_api_key)
):
    db = SessionLocal()

    logger.info("Запрос истории")

    records = db.query(QRCode).all()

    db.close()

    return [
        {
            "id": r.id,
            "text": r.text,
            "file_path": r.file_path
        }
        for r in records
    ]