from sqlalchemy import Column, Integer, String
from server.db.database import Base


class QRCode(Base):
    """Модель таблицы истории генераций QR-кодов."""
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True)  # уникальный ID
    text = Column(String, nullable=False)               # закодированный текст
    file_path = Column(String, nullable=False)           # путь к PNG-файлу
