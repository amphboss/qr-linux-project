import logging
import os
from fastapi import FastAPI
from pydantic import BaseModel

from shared.qr_generator import QRGenerator
from server.db.database import SessionLocal, engine
from server.models import QRCode, Base

# ===== ЛОГИРОВАНИЕ =====
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/server.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ===== APP =====
app = FastAPI(title="QR Generator API")

Base.metadata.create_all(bind=engine)

qr_generator = QRGenerator()


class QRRequest(BaseModel):
    text: str


@app.post("/generate")
def generate_qr(request: QRRequest):
    db = SessionLocal()

    logger.info(f"Запрос на генерацию QR: {request.text}")

    try:
        path = qr_generator.generate(request.text)

        qr_record = QRCode(
            text=request.text,
            file_path=path
        )

        db.add(qr_record)
        db.commit()

        logger.info(f"QR успешно создан: {path}")

        return {
            "status": "success",
            "file_path": path
        }

    except Exception as e:
        logger.error(f"Ошибка генерации QR: {str(e)}")

        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        db.close()


@app.get("/history")
def get_history():
    db = SessionLocal()

    logger.info("Запрос истории QR")

    try:
        records = db.query(QRCode).all()

        return [
            {
                "id": r.id,
                "text": r.text,
                "file_path": r.file_path
            }
            for r in records
        ]

    except Exception as e:
        logger.error(f"Ошибка получения истории: {str(e)}")
        return []

    finally:
        db.close()
