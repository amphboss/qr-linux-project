import qrcode
import os
from datetime import datetime


class QRGenerator:
    def __init__(self, output_dir="generated_qr"):
        self.output_dir = output_dir

        # создаем папку если нет
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate(self, data: str) -> str:
        """
        Генерация QR-кода из строки.
        Возвращает путь к файлу.
        """

        if not data or not data.strip():
            raise ValueError("Пустые данные для QR")

        # уникальное имя файла
        filename = f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)

        # генерация QR
        qr = qrcode.make(data)
        qr.save(filepath)

        return filepath
