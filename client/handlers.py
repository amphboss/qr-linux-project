import threading
import os
import customtkinter as ctk
from PIL import Image
from tkinter import filedialog, messagebox

from client.api_client import APIClient


class HandlersMixin:
    """Миксин с обработчиками событий (генерация, сохранение, история, сервер)."""

    # ================= SERVER =================
    def check_server(self):
        """ Периодическая проверка доступности сервера (каждые 5 сек)."""
        def check():
            if APIClient.check_server():
                self.after(0, lambda: self.status_label.configure(
                    text="● Сервер доступен", text_color="#22c55e"))
            else:
                self.after(0, lambda: self.status_label.configure(
                    text="● Сервер недоступен", text_color="#ef4444"))

        # Запуск в отдельном потоке, чтобы не блокировать UI
        threading.Thread(target=check, daemon=True).start()
        self.after(5000, self.check_server)  # повтор через 5 сек

    # ================= GENERATE =================
    def generate(self):
        """Запуск генерации в фоновом потоке."""
        threading.Thread(target=self._generate_thread).start()

    def _show_error(self, title, message):
        """Показ ошибки в главном потоке (из фонового)."""
        self.after(0, lambda: messagebox.showerror(title, message))

    def _show_warning(self, title, message):
        """Показ предупреждения в главном потоке."""
        self.after(0, lambda: messagebox.showwarning(title, message))

    def _generate_thread(self):
        """ Фоновый поток: сбор параметров, отправка на сервер, обработка ответа."""
        text = self.textbox.get("1.0", "end").strip()

        if not text:
            self._show_warning("Пустой ввод", "Введите текст или URL для генерации QR-кода.")
            return

        # Первый символ значения = буква уровня (L/M/Q/H)
        error_code = self.error_level.get()[0]

        try:
            box_size = int(self.size_entry.get() or 10)
            border = int(self.border_entry.get() or 4)
        except ValueError:
            self._show_error("Ошибка параметров", "Размер модуля и рамка должны быть числами.")
            return

        # Формирование JSON-тела запроса
        data = {
            "text": text,
            "fill_color": self.qr_color,
            "back_color": self.bg_color,
            "box_size": box_size,
            "border": border,
            "error": error_code,
        }

        try:
            r = APIClient.generate(data)  # HTTP POST на сервер

            if r.status_code == 422:
                detail = r.json().get("detail", [])
                msgs = [d.get("msg", "") for d in detail] if isinstance(detail, list) else [str(detail)]
                self._show_error("Ошибка валидации", "\n".join(msgs))
                return

            if r.status_code != 200:
                self._show_error("Ошибка сервера", f"Сервер вернул код {r.status_code}.")
                return

            res = r.json()

            if res.get("status") == "success":
                self.after(0, lambda: self._update_ui(res["file_path"]))
            else:
                self._show_error("Ошибка API", str(res))

        except Exception as e:
            self._show_error("Нет соединения", "Не удалось подключиться к серверу.\nУбедитесь, что сервер запущен.")

    def _update_ui(self, path):
        """ Обновление интерфейса после успешной генерации."""
        with self._lock:  # потокобезопасная запись пути
            self.qr_path = path
        img = ctk.CTkImage(Image.open(path), size=(280, 280))
        self.image_label.configure(image=img, text="")
        self.image_label.image = img  # сохраняем ссылку от сборщика мусора
        self.preview_title.pack_forget()  # убираем placeholder-текст
        self.preview_sub.pack_forget()
        self.load_history()

    # ================= SAVE =================
    def save_file(self):
        """ Сохранение QR-кода в файл, выбранный пользователем."""
        with self._lock:  # потокобезопасное чтение пути
            path = self.qr_path

        if not path:
            messagebox.showwarning("Нечего сохранять", "Сначала сгенерируйте QR-код.")
            return

        dest = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Все файлы", "*.*")],
            initialfile=os.path.basename(path),
            title="Сохранить QR-код"
        )

        if not dest:
            return

        with open(path, "rb") as f:
            with open(dest, "wb") as out:
                out.write(f.read())

    # ================= HISTORY =================
    def load_history(self):
        """Загрузка истории в фоновом потоке."""
        threading.Thread(target=self._history_thread, daemon=True).start()

    def _history_thread(self):
        """ Запрос истории с сервера и передача в UI-поток."""
        try:
            data = APIClient.get_history()
            self.after(0, lambda: self._update_history(data))
        except:
            pass

    def _update_history(self, data):
        """Отображение истории в текстовом поле."""
        with self._lock:  # потокобезопасная запись данных
            self.history_data = data
        self.history_list.configure(state="normal")
        self.history_list.delete("1.0", "end")
        for item in data:
            self.history_list.insert("end", f"#{item['id']}  {item['text']}\n")
        self.history_list.configure(state="disabled")
