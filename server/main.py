from fastapi import FastAPI
from pydantic import BaseModel
from shared.qr_generator import QRGenerator

from server.db.database import SessionLocal, engine
from server.models import QRCode, Base

app = FastAPI(title="QR Generator API")

# создаём таблицы
Base.metadata.create_all(bind=engine)

qr_generator = QRGenerator()


class QRRequest(BaseModel):
    text: str


@app.post("/generate")
def generate_qr(request: QRRequest):
    db = SessionLocal()

    try:
        path = qr_generator.generate(request.text)

        qr_record = QRCode(
            text=request.text,
            file_path=path
        )

        db.add(qr_record)
        db.commit()

        return {
            "status": "success",
            "file_path": path
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        db.close()


@app.get("/history")
def get_history():
    db = SessionLocal()

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

    finally:
        db.close()
