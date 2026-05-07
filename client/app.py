import customtkinter as ctk
import threading
from tkinter import colorchooser

from client.theme import ThemeMixin
from client.handlers import HandlersMixin

# Установка базового режима CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class QRApp(ThemeMixin, HandlersMixin, ctk.CTk):
    """Главное окно приложения. Наследует ThemeMixin (темы) и HandlersMixin (логика)."""

    def __init__(self):
        super().__init__()

        self.title("QR Code Generator")
        self.geometry("1100x680")

        # Состояние приложения
        self.qr_path = None          # путь к последнему QR
        self.history_data = []       # кэш истории
        self.qr_color = "#000000"    # цвет QR-кода
        self.bg_color = "#ffffff"    # цвет фона QR
        self._lock = threading.Lock()  # мьютекс для потокобезопасности
        self._init_theme()

        # Списки виджетов для массовой перекраски при смене темы
        self._cards = []    # карточки-контейнеры
        self._pills = []    # пилл-компоненты (параметры)
        self._labels1 = []  # основной текст
        self._labels2 = []  # второстепенный текст
        self._entries = []  # поля ввода

        # Сетка: 2 колонки, растягиваются равномерно
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Построение интерфейса
        self.create_status_bar()
        self.create_left()      # левая панель: ввод и параметры
        self.create_right()     # правая панель: предпросмотр и история
        self.create_footer()    # нижняя панель: подсказка + кнопка темы
        self._apply_theme()     # применяем цвета текущей темы

        # Фоновые задачи при старте
        self.check_server()     # проверка сервера
        self.load_history()     # загрузка истории

    # ================= STATUS BAR =================
    def create_status_bar(self):
        """Индикатор статуса сервера (правый верхний угол)."""
        self.status_label = ctk.CTkLabel(
            self, text="● Проверка...", text_color="gray",
            font=("Segoe UI", 13)
        )
        self.status_label.grid(row=0, column=1, sticky="e", padx=25, pady=(10, 0))

    # ================= LEFT =================
    def create_left(self):
        """Левая панель: поле текста, цвета, параметры, кнопки."""
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
        color_row.grid_columnconfigure(0, weight=1, uniform="col")
        color_row.grid_columnconfigure(1, weight=1, uniform="col")

        self.qr_color_pill = self._create_color_pill(
            color_row, "💧  Цвет QR-кода", self.qr_color, self.pick_qr_color
        )
        self.qr_color_pill.grid(row=0, column=0, padx=(0, 5), sticky="nsew")

        self.bg_color_pill = self._create_color_pill(
            color_row, "💧  Цвет фона", self.bg_color, self.pick_bg_color
        )
        self.bg_color_pill.grid(row=0, column=1, padx=(5, 0), sticky="nsew")

        # --- Размер / Рамка ---
        param_row = ctk.CTkFrame(self._left_card, fg_color="transparent")
        param_row.pack(fill="x", padx=25, pady=(0, 10))
        param_row.grid_columnconfigure(0, weight=1, uniform="par")
        param_row.grid_columnconfigure(1, weight=1, uniform="par")

        size_pill = self._create_param_pill(param_row, "⊞  Размер модуля", "10")
        size_pill.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        self.size_entry = size_pill._entry

        border_pill = self._create_param_pill(param_row, "{ }  Рамка (отступ)", "4")
        border_pill.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
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
        btn_row.grid_columnconfigure(0, weight=1, uniform="btn")
        btn_row.grid_columnconfigure(1, weight=1, uniform="btn")

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
        """Создание пилл-компонента выбора цвета с превью."""
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
        """Создание пилл-компонента с полем ввода числового параметра."""
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
        """Правая панель: предпросмотр QR-кода и история."""
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
        self._preview_frame.pack(fill="both", expand=True, padx=25, pady=(0, 10))

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

        # --- История ---
        self._history_header = ctk.CTkLabel(
            self._right_card, text="📋  История",
            font=("Segoe UI", 14, "bold")
        )
        self._history_header.pack(anchor="w", padx=25, pady=(5, 3))
        self._labels1.append(self._history_header)

        self._history_frame = ctk.CTkFrame(
            self._right_card, corner_radius=12, border_width=1, height=120
        )
        self._history_frame.pack(fill="x", padx=25, pady=(0, 20))
        self._history_frame.pack_propagate(False)
        self._pills.append(self._history_frame)

        self.history_list = ctk.CTkTextbox(
            self._history_frame, font=("Segoe UI", 12),
            corner_radius=10, border_width=0, activate_scrollbars=True,
        )
        self.history_list.pack(fill="both", expand=True, padx=6, pady=6)
        self.history_list.configure(state="disabled")

    # ================= FOOTER =================
    def create_footer(self):
        """Нижняя панель: подсказка и кнопка смены темы."""
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
        """Открытие палитры для выбора цвета QR-кода."""
        color = colorchooser.askcolor(initialcolor=self.qr_color)[1]
        if color:
            self.qr_color = color
            self.qr_color_pill._swatch.configure(fg_color=color, hover_color=color)

    def pick_bg_color(self):
        """Открытие палитры для выбора цвета фона."""
        color = colorchooser.askcolor(initialcolor=self.bg_color)[1]
        if color:
            self.bg_color = color
            self.bg_color_pill._swatch.configure(fg_color=color, hover_color=color)


if __name__ == "__main__":
    app = QRApp()
    app.mainloop()
