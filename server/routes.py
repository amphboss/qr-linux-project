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

qr_generator = QRGenerator()
db_lock = threading.Lock()


@router.post("/generate")
def generate_qr(request: QRRequest, _: None = Depends(verify_api_key)):
    logger.info(f"QR: {request.text}")

    path = qr_generator.generate(
        data=request.text,
        fill_color=request.fill_color,
        back_color=request.back_color,
        box_size=request.box_size,
        border=request.border,
        error=request.error
    )

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
