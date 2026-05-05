from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./qr_history.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # важно для SQLite
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
