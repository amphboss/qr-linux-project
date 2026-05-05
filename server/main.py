from fastapi import FastAPI
from pydantic import BaseModel
from shared.qr_generator import QRGenerator

app = FastAPI(title="QR Generator API")

qr_generator = QRGenerator()


# Модель входных данных
class QRRequest(BaseModel):
    text: str


@app.post("/generate")
def generate_qr(request: QRRequest):
    try:
        path = qr_generator.generate(request.text)

        return {
            "status": "success",
            "text": request.text,
            "file_path": path
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
