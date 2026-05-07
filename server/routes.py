import logging
import threading
from fastapi import APIRouter, Depends

from shared.qr_generator import QRGenerator
from server.db.database import SessionLocal
from server.models import QRCode
from server.schemas import QRRequest
from server.auth import verify_api_key

logger = logging.getLogger(__name__)

router = APIRouter()

qr_generator = QRGenerator()       # экземпляр генератора QR
db_lock = threading.Lock()          # мьютекс для защиты SQLite от конкурентного доступа


@router.post("/generate")
def generate_qr(request: QRRequest, _: None = Depends(verify_api_key)):
    """Эндпоинт генерации QR: создаёт изображение и сохраняет запись в БД."""
    logger.info(f"QR: {request.text}")

    # Генерация QR-кода (сохраняет PNG на диск)
    path = qr_generator.generate(
        data=request.text,
        fill_color=request.fill_color,
        back_color=request.back_color,
        box_size=request.box_size,
        border=request.border,
        error=request.error
    )

    # Запись в БД под мьютексом (защита от параллельных записей)
    with db_lock:
        db = SessionLocal()
        try:
            qr_record = QRCode(
                text=request.text,
                file_path=path
            )
            db.add(qr_record)
            db.commit()
        finally:
            db.close()

    return {
        "status": "success",
        "file_path": path
    }


@router.get("/history")
def get_history(_: None = Depends(verify_api_key)):
    """Эндпоинт истории: возвращает все записи из БД."""
    # Чтение под мьютексом
    with db_lock:
        db = SessionLocal()
        try:
            records = db.query(QRCode).all()
            result = [
                {
                    "id": r.id,
                    "text": r.text,
                    "file_path": r.file_path
                }
                for r in records
            ]
        finally:
            db.close()

    return result
