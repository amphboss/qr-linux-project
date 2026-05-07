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
        def check():
            if APIClient.check_server():
                self.after(0, lambda: self.status_label.configure(
                    text="● Сервер доступен", text_color="#22c55e"))
            else:
                self.after(0, lambda: self.status_label.configure(
                    text="● Сервер недоступен", text_color="#ef4444"))

        threading.Thread(target=check, daemon=True).start()
        self.after(5000, self.check_server)

    # ================= GENERATE =================
    def generate(self):
        threading.Thread(target=self._generate_thread).start()

    def _show_error(self, title, message):
        self.after(0, lambda: messagebox.showerror(title, message))

    def _show_warning(self, title, message):
        self.after(0, lambda: messagebox.showwarning(title, message))

    def _generate_thread(self):
        text = self.textbox.get("1.0", "end").strip()

        if not text:
            self._show_warning("Пустой ввод", "Введите текст или URL для генерации QR-кода.")
            return

        error_code = self.error_level.get()[0]

        try:
            box_size = int(self.size_entry.get() or 10)
            border = int(self.border_entry.get() or 4)
        except ValueError:
            self._show_error("Ошибка параметров", "Размер модуля и рамка должны быть числами.")
            return

        data = {
            "text": text,
            "fill_color": self.qr_color,
            "back_color": self.bg_color,
            "box_size": box_size,
            "border": border,
            "error": error_code,
        }

        try:
            r = APIClient.generate(data)

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
        with self._lock:
            self.qr_path = path
        img = ctk.CTkImage(Image.open(path), size=(280, 280))
        self.image_label.configure(image=img, text="")
        self.image_label.image = img
        self.preview_title.pack_forget()
        self.preview_sub.pack_forget()
        self.load_history()

    # ================= SAVE =================
    def save_file(self):
        with self._lock:
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
        threading.Thread(target=self._history_thread, daemon=True).start()

    def _history_thread(self):
        try:
            data = APIClient.get_history()
            self.after(0, lambda: self._update_history(data))
        except:
            pass

    def _update_history(self, data):
        with self._lock:
            self.history_data = data
        self.history_list.configure(state="normal")
        self.history_list.delete("1.0", "end")
        for item in data:
            self.history_list.insert("end", f"#{item['id']}  {item['text']}\n")
        self.history_list.configure(state="disabled")
