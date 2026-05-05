from sqlalchemy import Column, Integer, String
from server.db.database import Base


class QRCode(Base):
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
