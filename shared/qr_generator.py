import qrcode
import os
from datetime import datetime


class QRGenerator:
    """Пользовательская библиотека для генерации QR-кодов в формате PNG."""

    def __init__(self, output_dir="generated_qr"):
        self.output_dir = output_dir
        # Создаём выходную директорию если не существует
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate(self, data: str, fill_color: str = "#000000", back_color: str = "#ffffff",
                 box_size: int = 10, border: int = 4, error: str = "M") -> str:
        """
        Генерация QR-кода из строки.
        Возвращает путь к сохранённому PNG-файлу.
        """
        # Валидация входных данных
        if not data or not data.strip():
            raise ValueError("Пустые данные для QR")

        # Сопоставление букв с константами библиотеки qrcode
        error_levels = {
            "L": qrcode.constants.ERROR_CORRECT_L,   # 7% восстановления
            "M": qrcode.constants.ERROR_CORRECT_M,   # 15%
            "Q": qrcode.constants.ERROR_CORRECT_Q,   # 25%
            "H": qrcode.constants.ERROR_CORRECT_H,   # 30%
        }

        # Уникальное имя на основе времени
        filename = f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)

        # Создание QR-кода
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_levels.get(error, qrcode.constants.ERROR_CORRECT_M),
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)     # добавляем данные
        qr.make(fit=True)     # автоподбор размера матрицы

        # Рендер и сохранение изображения
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        img.save(filepath)

        return filepath
