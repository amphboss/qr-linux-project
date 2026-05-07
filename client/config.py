# URL-адреса серверного API
API_GENERATE = "http://127.0.0.1:8000/generate"  # генерация QR-кода
API_HISTORY = "http://127.0.0.1:8000/history"    # получение истории
API_HEALTH = "http://127.0.0.1:8000/docs"       # проверка доступности сервера

# Заголовки для аутентификации запросов
HEADERS = {"x-api-key": "mysecretkey"}

# Цветовые схемы интерфейса (светлая и тёмная тема)
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
