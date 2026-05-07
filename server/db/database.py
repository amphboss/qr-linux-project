from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Путь к файлу БД (SQLite хранит данные локально)
DATABASE_URL = "sqlite:///./qr_history.db"

# Создание движка SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # разрешаем доступ из разных потоков
)

# Фабрика сессий для работы с БД
SessionLocal = sessionmaker(bind=engine)

# Базовый класс для описания моделей
Base = declarative_base()
