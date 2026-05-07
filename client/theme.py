from client.config import THEMES


class ThemeMixin:
    """Миксин для управления темой приложения (light/dark)."""

    def _init_theme(self):
        """ Установка темы по умолчанию."""
        self._theme = "light"

    @property
    def t(self):
        """ Текущий словарь цветов (зависит от self._theme)."""
        return THEMES[self._theme]

    def toggle_theme(self):
        """Переключение между светлой и тёмной темой."""
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

        # история
        self.history_list.configure(
            fg_color=t["pill"], text_color=t["text1"]
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
