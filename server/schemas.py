import re
from pydantic import BaseModel, field_validator


class QRRequest(BaseModel):
    text: str
    fill_color: str = "#000000"
    back_color: str = "#ffffff"
    box_size: int = 10
    border: int = 4
    error: str = "M"

    @field_validator("text")
    @classmethod
    def validate_text(cls, value):
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
