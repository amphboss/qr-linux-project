import qrcode
import os
from datetime import datetime


class QRGenerator:
    def __init__(self, output_dir="generated_qr"):
        self.output_dir = output_dir

        # создаем папку если нет
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate(self, data: str, fill_color: str = "#000000", back_color: str = "#ffffff",
                 box_size: int = 10, border: int = 4, error: str = "M") -> str:
        """
        Генерация QR-кода из строки.
        Возвращает путь к файлу.
        """

        if not data or not data.strip():
            raise ValueError("Пустые данные для QR")

        error_levels = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H,
        }

        # уникальное имя файла
        filename = f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)

        # генерация QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_levels.get(error, qrcode.constants.ERROR_CORRECT_M),
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        img.save(filepath)

        return filepath
