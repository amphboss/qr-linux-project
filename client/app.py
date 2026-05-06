import customtkinter as ctk
import requests
from PIL import Image
import threading
from tkinter import colorchooser, filedialog
import os

API_GENERATE = "http://127.0.0.1:8000/generate"
API_HISTORY = "http://127.0.0.1:8000/history"
HEADERS = {"x-api-key": "mysecretkey"}

# ===== ЦВЕТА ТЕМ =====
THEMES = {
    "light": {
        "bg": "#ede5f7",
        "card": "#ffffff",
        "accent": "#7c3aed",
        "accent_hover": "#6d28d9",
        "text1": "#1a1a2e",
        "text2": "#6b7280",
        "border": "#e5e7eb",
        "pill": "#f9fafb",
        "input": "#fafafa",
        "hover": "#f3f4f6",
        "icon": "🌙",
    },
    "dark": {
        "bg": "#1a1025",
        "card": "#2d2640",
        "accent": "#a78bfa",
        "accent_hover": "#8b5cf6",
        "text1": "#f1f0f3",
        "text2": "#9ca3af",
        "border": "#4a4458",
        "pill": "#362f48",
        "input": "#362f48",
        "hover": "#3d3556",
        "icon": "☀",
    },
}

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class QRApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QR Code Generator")
        self.geometry("1100x680")

        self.qr_path = None
        self.history_data = []
        self.qr_color = "#000000"
        self.bg_color = "#ffffff"
        self._theme = "light"

        # списки виджетов для перекраски
        self._cards = []
        self._pills = []
        self._labels1 = []
        self._labels2 = []
        self._entries = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_status_bar()
        self.create_left()
        self.create_right()
        self.create_footer()
        self._apply_theme()

        self.check_server()
        self.load_history()

    @property
    def t(self):
        return THEMES[self._theme]

    # ================= STATUS BAR =================
    def create_status_bar(self):
        self.status_label = ctk.CTkLabel(
            self, text="● Проверка...", text_color="gray",
            font=("Segoe UI", 13)
        )
        self.status_label.grid(row=0, column=1, sticky="e", padx=25, pady=(10, 0))
        self._labels2.append(self.status_label)

    # ================= LEFT =================
    def create_left(self):
        self._left_card = ctk.CTkFrame(self, corner_radius=18, border_width=0)
        self._left_card.grid(row=1, column=0, padx=(20, 10), pady=15, sticky="nsew")
        self._cards.append(self._left_card)

        self._header_left = ctk.CTkLabel(
            self._left_card, text="⚙  Настройки",
            font=("Segoe UI", 20, "bold")
        )
        self._header_left.pack(anchor="w", padx=25, pady=(20, 15))

        lbl = ctk.CTkLabel(
            self._left_card, text="Текст / URL",
            font=("Segoe UI", 13, "bold")
        )
        lbl.pack(anchor="w", padx=25)
        self._labels1.append(lbl)

        self.textbox = ctk.CTkTextbox(
            self._left_card, height=80, corner_radius=12,
            border_width=1, font=("Segoe UI", 13)
        )
        self.textbox.pack(fill="x", padx=25, pady=(5, 15))

        # --- Цвета ---
        color_row = ctk.CTkFrame(self._left_card, fg_color="transparent")
        color_row.pack(fill="x", padx=25, pady=(0, 10))
        color_row.grid_columnconfigure((0, 1), weight=1)

        self.qr_color_pill = self._create_color_pill(
            color_row, "💧  Цвет QR-кода", self.qr_color, self.pick_qr_color
        )
        self.qr_color_pill.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.bg_color_pill = self._create_color_pill(
            color_row, "💧  Цвет фона", self.bg_color, self.pick_bg_color
        )
        self.bg_color_pill.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # --- Размер / Рамка ---
        param_row = ctk.CTkFrame(self._left_card, fg_color="transparent")
        param_row.pack(fill="x", padx=25, pady=(0, 10))
        param_row.grid_columnconfigure((0, 1), weight=1)

        size_pill = self._create_param_pill(param_row, "⊞  Размер модуля", "10")
        size_pill.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.size_entry = size_pill._entry

        border_pill = self._create_param_pill(param_row, "{ }  Рамка (отступ)", "4")
        border_pill.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        self.border_entry = border_pill._entry

        # --- Коррекция ошибок ---
        self._error_pill = ctk.CTkFrame(self._left_card, corner_radius=12, border_width=1)
        self._error_pill.pack(fill="x", padx=25, pady=(0, 15))
        self._pills.append(self._error_pill)

        error_inner = ctk.CTkFrame(self._error_pill, fg_color="transparent")
        error_inner.pack(fill="x", padx=12, pady=8)

        lbl_err = ctk.CTkLabel(
            error_inner, text="●  Коррекция ошибок",
            font=("Segoe UI", 12)
        )
        lbl_err.pack(side="left")
        self._labels1.append(lbl_err)

        self.error_level = ctk.CTkOptionMenu(
            error_inner,
            values=[
                "L - Низкий уровень",
                "M - Средний уровень",
                "Q - Высокий уровень",
                "H - Максимальный уровень",
            ],
            corner_radius=8,
            font=("Segoe UI", 12),
            width=200,
        )
        self.error_level.set("M - Средний уровень")
        self.error_level.pack(side="right")

        # --- Кнопки ---
        btn_row = ctk.CTkFrame(self._left_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=25, pady=(0, 25))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        self.generate_btn = ctk.CTkButton(
            btn_row, text="✨  Сгенерировать", height=44,
            corner_radius=12, font=("Segoe UI", 14, "bold"),
            command=self.generate,
        )
        self.generate_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.save_btn = ctk.CTkButton(
            btn_row, text="⬇  Сохранить PNG", height=44,
            corner_radius=12, font=("Segoe UI", 14),
            fg_color="transparent", border_width=1,
            command=self.save_file,
        )
        self.save_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    # ================= PILL HELPERS =================
    def _create_color_pill(self, parent, label, color, cmd):
        pill = ctk.CTkFrame(parent, corner_radius=12, border_width=1)
        self._pills.append(pill)

        inner = ctk.CTkFrame(pill, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=8)

        lbl = ctk.CTkLabel(inner, text=label, font=("Segoe UI", 12))
        lbl.pack(side="left")
        self._labels1.append(lbl)

        arrow = ctk.CTkLabel(inner, text="▾", font=("Segoe UI", 14))
        arrow.pack(side="right")
        self._labels2.append(arrow)

        swatch = ctk.CTkButton(
            inner, text="", width=30, height=22, corner_radius=6,
            fg_color=color, hover_color=color,
            border_width=1, command=cmd,
        )
        swatch.pack(side="right", padx=(5, 4))
        pill._swatch = swatch
        return pill

    def _create_param_pill(self, parent, label, default):
        pill = ctk.CTkFrame(parent, corner_radius=12, border_width=1)
        self._pills.append(pill)

        inner = ctk.CTkFrame(pill, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=8)

        lbl = ctk.CTkLabel(inner, text=label, font=("Segoe UI", 12))
        lbl.pack(side="left")
        self._labels1.append(lbl)

        entry = ctk.CTkEntry(
            inner, width=55, height=28, corner_radius=8,
            border_width=1, font=("Segoe UI", 12),
            justify="center",
        )
        entry.insert(0, default)
        entry.pack(side="right")
        self._entries.append(entry)
        pill._entry = entry
        return pill

    # ================= RIGHT =================
    def create_right(self):
        self._right_card = ctk.CTkFrame(self, corner_radius=18, border_width=0)
        self._right_card.grid(row=1, column=1, padx=(10, 20), pady=15, sticky="nsew")
        self._cards.append(self._right_card)

        top = ctk.CTkFrame(self._right_card, fg_color="transparent")
        top.pack(fill="x", padx=25, pady=(20, 10))

        self._header_right = ctk.CTkLabel(
            top, text="👁  Предпросмотр",
            font=("Segoe UI", 20, "bold")
        )
        self._header_right.pack(side="left")

        self._preview_frame = ctk.CTkFrame(
            self._right_card, corner_radius=14, border_width=1
        )
        self._preview_frame.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        self.image_label = ctk.CTkLabel(self._preview_frame, text="")
        self.image_label.pack(expand=True)

        self.preview_title = ctk.CTkLabel(
            self._preview_frame, text="QR-код появится здесь",
            font=("Segoe UI", 16, "bold")
        )
        self.preview_title.pack()
        self._labels1.append(self.preview_title)

        self.preview_sub = ctk.CTkLabel(
            self._preview_frame, text="Введите текст и нажмите «Сгенерировать»",
            font=("Segoe UI", 12)
        )
        self.preview_sub.pack(pady=(0, 20))
        self._labels2.append(self.preview_sub)

    # ================= FOOTER =================
    def create_footer(self):
        self._footer = ctk.CTkFrame(self, corner_radius=14, height=48)
        self._footer.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="ew")
        self._footer.grid_propagate(False)
        self._cards.append(self._footer)

        inner = ctk.CTkFrame(self._footer, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20)

        self._footer_label = ctk.CTkLabel(
            inner,
            text="ⓘ  Введите данные и настройте параметры для создания QR-кода",
            font=("Segoe UI", 12)
        )
        self._footer_label.pack(side="left", pady=10)
        self._labels2.append(self._footer_label)

        self._theme_btn = ctk.CTkButton(
            inner, text="🌙", width=34, height=34,
            corner_radius=8, font=("Segoe UI", 16),
            command=self.toggle_theme,
        )
        self._theme_btn.pack(side="right", pady=7)

    # ================= COLORS =================
    def pick_qr_color(self):
        color = colorchooser.askcolor(initialcolor=self.qr_color)[1]
        if color:
            self.qr_color = color
            self.qr_color_pill._swatch.configure(fg_color=color, hover_color=color)

    def pick_bg_color(self):
        color = colorchooser.askcolor(initialcolor=self.bg_color)[1]
        if color:
            self.bg_color = color
            self.bg_color_pill._swatch.configure(fg_color=color, hover_color=color)

    # ================= THEME =================
    def toggle_theme(self):
        self._theme = "dark" if self._theme == "light" else "light"
        self._apply_theme()

    def _apply_theme(self):
        t = self.t

        self.configure(fg_color=t["bg"])

        for card in self._cards:
            card.configure(fg_color=t["card"])

        for pill in self._pills:
            pill.configure(fg_color=t["pill"], border_color=t["border"])

        for lbl in self._labels1:
            lbl.configure(text_color=t["text1"])

        for lbl in self._labels2:
            lbl.configure(text_color=t["text2"])

        for entry in self._entries:
            entry.configure(
                fg_color=t["card"], border_color=t["border"],
                text_color=t["text1"]
            )

        # заголовки
        self._header_left.configure(text_color=t["accent"])
        self._header_right.configure(text_color=t["accent"])

        # текстовое поле
        self.textbox.configure(
            fg_color=t["input"], border_color=t["border"],
            text_color=t["text1"]
        )

        # предпросмотр
        self._preview_frame.configure(
            fg_color=t["input"], border_color=t["border"]
        )

        # кнопка генерации
        self.generate_btn.configure(
            fg_color=t["accent"], hover_color=t["accent_hover"]
        )

        # кнопка сохранения
        self.save_btn.configure(
            border_color=t["border"], text_color=t["text1"],
            hover_color=t["hover"]
        )

        # выпадающий список ошибок
        self.error_level.configure(
            fg_color=t["pill"], button_color=t["pill"],
            button_hover_color=t["hover"],
            text_color=t["text1"],
            dropdown_fg_color=t["card"]
        )

        # цветовые сэмплы — рамка
        self.qr_color_pill._swatch.configure(border_color=t["border"])
        self.bg_color_pill._swatch.configure(border_color=t["border"])

        # кнопка темы
        self._theme_btn.configure(
            text=t["icon"], fg_color=t["pill"],
            hover_color=t["hover"], text_color=t["text1"]
        )

        # сохраняем цвет статуса (не перезаписываем зелёный/красный)
        current = self.status_label.cget("text_color")
        if current == "gray":
            self.status_label.configure(text_color=t["text2"])

    # ================= SERVER =================
    def check_server(self):
        def check():
            try:
                requests.get("http://127.0.0.1:8000/docs", timeout=2)
                self.after(0, lambda: self.status_label.configure(
                    text="● Сервер доступен", text_color="#22c55e"))
            except:
                self.after(0, lambda: self.status_label.configure(
                    text="● Сервер недоступен", text_color="#ef4444"))

        threading.Thread(target=check).start()

    # ================= GENERATE =================
    def generate(self):
        threading.Thread(target=self.generate_thread).start()

    def generate_thread(self):
        text = self.textbox.get("1.0", "end").strip()

        error_code = self.error_level.get()[0]

        data = {
            "text": text,
            "fill_color": self.qr_color,
            "back_color": self.bg_color,
            "box_size": int(self.size_entry.get() or 10),
            "border": int(self.border_entry.get() or 4),
            "error": error_code,
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
        self.preview_title.pack_forget()
        self.preview_sub.pack_forget()
        self.load_history()

    # ================= SAVE =================
    def save_file(self):
        if not self.qr_path:
            return

        dest = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Все файлы", "*.*")],
            initialfile=os.path.basename(self.qr_path),
            title="Сохранить QR-код"
        )

        if not dest:
            return

        with open(self.qr_path, "rb") as f:
            with open(dest, "wb") as out:
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
        self.history_data = data


if __name__ == "__main__":
    app = QRApp()
    app.mainloop()
