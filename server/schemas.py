import re
from pydantic import BaseModel, field_validator


class QRRequest(BaseModel):
    """Модель запроса на генерацию QR-кода с валидацией всех полей."""
    text: str                        # текст для кодирования
    fill_color: str = "#000000"      # цвет QR-кода
    back_color: str = "#ffffff"      # цвет фона
    box_size: int = 10               # размер одного модуля (пиксели)
    border: int = 4                  # ширина рамки (модули)
    error: str = "M"                 # уровень коррекции (L/M/Q/H)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value):
        """Проверка текста: не пустой, не длиннее 200, без опасных символов."""
        if not value or not value.strip():
            raise ValueError("Пустая строка")

        if len(value) > 200:
            raise ValueError("Слишком длинный текст")

        if re.search(r"[<>$]", value):
            raise ValueError("Недопустимые символы")

        return value.strip()

    @field_validator("box_size")
    @classmethod
    def validate_box(cls, v):
        if v < 1 or v > 50:
            raise ValueError("Размер вне диапазона")
        return v

    @field_validator("border")
    @classmethod
    def validate_border(cls, v):
        if v < 0 or v > 20:
            raise ValueError("Отступ вне диапазона")
        return v
