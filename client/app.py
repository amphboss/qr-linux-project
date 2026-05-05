import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
import threading

API_GENERATE = "http://127.0.0.1:8000/generate"
API_HISTORY = "http://127.0.0.1:8000/history"


class QRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Generator")
        self.root.geometry("500x600")

        # ===== ВВОД =====
        self.label = tk.Label(root, text="Введите текст:")
        self.label.pack(pady=5)

        self.entry = tk.Entry(root, width=40)
        self.entry.pack(pady=5)

        self.button = tk.Button(root, text="Создать QR", command=self.generate_qr)
        self.button.pack(pady=10)

        # ===== КАРТИНКА =====
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        # ===== ИСТОРИЯ =====
        self.history_label = tk.Label(root, text="История QR:")
        self.history_label.pack(pady=5)

        self.listbox = tk.Listbox(root, width=60, height=10)
        self.listbox.pack(pady=5)

        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.refresh_button = tk.Button(root, text="Обновить историю", command=self.load_history)
        self.refresh_button.pack(pady=5)

        self.history_data = []

        # загрузка истории при старте
        self.load_history()

    # ===== ГЕНЕРАЦИЯ QR (в потоке) =====
    def generate_qr(self):
        thread = threading.Thread(target=self.generate_qr_thread)
        thread.start()

    def generate_qr_thread(self):
        text = self.entry.get()

        if not text:
            self.show_error("Введите текст")
            return

        try:
            response = requests.post(API_GENERATE, json={"text": text})
            data = response.json()

            if data["status"] == "success":
                self.update_ui_after_generate(data["file_path"])
            else:
                self.show_error(data["message"])

        except Exception as e:
            self.show_error(str(e))

    # ===== ОБНОВЛЕНИЕ UI БЕЗОПАСНО =====
    def update_ui_after_generate(self, path):
        self.root.after(0, lambda: self._update_ui(path))

    def _update_ui(self, path):
        self.show_image(path)
        self.load_history()

    # ===== ЗАГРУЗКА ИСТОРИИ (в потоке) =====
    def load_history(self):
        thread = threading.Thread(target=self.load_history_thread)
        thread.start()

    def load_history_thread(self):
        try:
            response = requests.get(API_HISTORY)
            data = response.json()

            self.root.after(0, lambda: self.update_history_ui(data))

        except Exception as e:
            self.show_error(str(e))

    def update_history_ui(self, data):
        self.listbox.delete(0, tk.END)

        for item in data:
            display_text = f"{item['id']}: {item['text']}"
            self.listbox.insert(tk.END, display_text)

        self.history_data = data

    # ===== ВЫБОР ИЗ СПИСКА =====
    def on_select(self, event):
        selection = self.listbox.curselection()

        if not selection:
            return

        index = selection[0]
        item = self.history_data[index]

        self.show_image(item["file_path"])

    # ===== ОТОБРАЖЕНИЕ QR =====
    def show_image(self, path):
        try:
            img = Image.open(path)
            img = img.resize((200, 200))

            photo = ImageTk.PhotoImage(img)

            self.image_label.config(image=photo)
            self.image_label.image = photo

        except Exception as e:
            self.show_error(str(e))

    # ===== ОШИБКИ =====
    def show_error(self, message):
        self.root.after(0, lambda: messagebox.showerror("Ошибка", message))


if __name__ == "__main__":
    root = tk.Tk()
    app = QRApp(root)
    root.mainloop()