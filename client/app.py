import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk


API_URL = "http://127.0.0.1:8000/generate"


class QRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Generator")
        self.root.geometry("400x500")

        # поле ввода
        self.label = tk.Label(root, text="Введите текст:")
        self.label.pack(pady=10)

        self.entry = tk.Entry(root, width=40)
        self.entry.pack(pady=5)

        # кнопка
        self.button = tk.Button(root, text="Создать QR", command=self.generate_qr)
        self.button.pack(pady=10)

        # место для картинки
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

    def generate_qr(self):
        text = self.entry.get()

        if not text:
            messagebox.showerror("Ошибка", "Введите текст")
            return

        try:
            response = requests.post(API_URL, json={"text": text})
            data = response.json()

            if data["status"] == "success":
                path = data["file_path"]

                img = Image.open(path)
                img = img.resize((200, 200))

                photo = ImageTk.PhotoImage(img)

                self.image_label.config(image=photo)
                self.image_label.image = photo

            else:
                messagebox.showerror("Ошибка", data["message"])

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = QRApp(root)
    root.mainloop()
