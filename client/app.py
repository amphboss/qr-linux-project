import customtkinter as ctk
import requests
from PIL import Image
import threading
from tkinter import colorchooser
import os

API_GENERATE = "http://127.0.0.1:8000/generate"
API_HISTORY = "http://127.0.0.1:8000/history"
HEADERS = {"x-api-key": "mysecretkey"}

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class QRApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QR Code Generator")
        self.geometry("1100x650")

        self.qr_path = None
        self.history_data = []

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_left()
        self.create_right()

        self.check_server()
        self.load_history()

    # ================= LEFT =================
    def create_left(self):
        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        ctk.CTkLabel(frame, text="⚙ Настройки", font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=15)

        self.textbox = ctk.CTkTextbox(frame, height=100)
        self.textbox.pack(fill="x", padx=20, pady=10)

        # Цвета
        color_frame = ctk.CTkFrame(frame, fg_color="transparent")
        color_frame.pack(fill="x", padx=20)

        self.qr_color = "#000000"
        self.bg_color = "#ffffff"

        self.color_btn = ctk.CTkButton(color_frame, text="Цвет QR", command=self.pick_qr_color)
        self.color_btn.pack(side="left", padx=5)

        self.bg_btn = ctk.CTkButton(color_frame, text="Фон", command=self.pick_bg_color)
        self.bg_btn.pack(side="left", padx=5)

        # Параметры
        param_frame = ctk.CTkFrame(frame, fg_color="transparent")
        param_frame.pack(fill="x", padx=20, pady=10)

        self.size_entry = ctk.CTkEntry(param_frame, placeholder_text="Размер (10)")
        self.size_entry.pack(side="left", padx=5)

        self.border_entry = ctk.CTkEntry(param_frame, placeholder_text="Отступ (4)")
        self.border_entry.pack(side="left", padx=5)

        # Коррекция ошибок
        self.error_level = ctk.CTkOptionMenu(
            frame,
            values=["L", "M", "Q", "H"]
        )
        self.error_level.set("M")
        self.error_level.pack(fill="x", padx=20, pady=10)

        # Кнопки
        self.generate_btn = ctk.CTkButton(frame, text="✨ Сгенерировать", height=40, command=self.generate)
        self.generate_btn.pack(fill="x", padx=20, pady=10)

        self.save_btn = ctk.CTkButton(frame, text="💾 Сохранить PNG", command=self.save_file)
        self.save_btn.pack(fill="x", padx=20, pady=5)

        # История
        ctk.CTkLabel(frame, text="История").pack(anchor="w", padx=20, pady=(10, 0))

        self.history_list = ctk.CTkTextbox(frame, height=150)
        self.history_list.pack(fill="both", padx=20, pady=10)

    # ================= RIGHT =================
    def create_right(self):
        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(top, text="👁 Предпросмотр", font=("Segoe UI", 18, "bold")).pack(side="left", padx=20, pady=15)

        self.status_label = ctk.CTkLabel(top, text="● Проверка...", text_color="gray")
        self.status_label.pack(side="right", padx=20)

        self.image_label = ctk.CTkLabel(frame, text="QR-код появится здесь")
        self.image_label.pack(expand=True)

    # ================= COLORS =================
    def pick_qr_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.qr_color = color

    def pick_bg_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.bg_color = color

    # ================= SERVER =================
    def check_server(self):
        def check():
            try:
                requests.get("http://127.0.0.1:8000/docs", timeout=2)
                self.after(0, lambda: self.status_label.configure(text="● Сервер доступен", text_color="green"))
            except:
                self.after(0, lambda: self.status_label.configure(text="● Сервер недоступен", text_color="red"))

        threading.Thread(target=check).start()

    # ================= GENERATE =================
    def generate(self):
        threading.Thread(target=self.generate_thread).start()

    def generate_thread(self):
        text = self.textbox.get("1.0", "end").strip()

        data = {
            "text": text,
            "fill_color": self.qr_color,
            "back_color": self.bg_color,
            "box_size": int(self.size_entry.get() or 10),
            "border": int(self.border_entry.get() or 4),
            "error": self.error_level.get()
        }

        try:
            r = requests.post(API_GENERATE, json=data, headers=HEADERS)

            print("STATUS:", r.status_code)
            print("TEXT:", r.text)

            if r.status_code != 200:
                print("Ошибка сервера")
                return

            res = r.json()

            if res.get("status") == "success":
                self.after(0, lambda: self.update_ui(res["file_path"]))
            else:
                print("Ошибка API:", res)

        except Exception as e:
            print("EXCEPTION:", e)

    def update_ui(self, path):
        self.qr_path = path
        img = ctk.CTkImage(Image.open(path), size=(280, 280))
        self.image_label.configure(image=img, text="")
        self.image_label.image = img
        self.load_history()

    # ================= SAVE =================
    def save_file(self):
        if not self.qr_path:
            return

        new_path = "saved_qr.png"
        with open(self.qr_path, "rb") as f:
            with open(new_path, "wb") as out:
                out.write(f.read())

    # ================= HISTORY =================
    def load_history(self):
        threading.Thread(target=self.history_thread).start()

    def history_thread(self):
        try:
            r = requests.get(API_HISTORY, headers=HEADERS)
            data = r.json()
            self.after(0, lambda: self.update_history(data))
        except:
            pass

    def update_history(self, data):
        self.history_list.delete("1.0", "end")

        for item in data:
            self.history_list.insert("end", f"{item['id']}: {item['text']}\n")

        self.history_data = data


if __name__ == "__main__":
    app = QRApp()
    app.mainloop()
