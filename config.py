"""Конфигурация бота."""

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Белый список пользователей (Telegram ID через запятую)
# Если пусто — бот доступен всем. Рекомендуется указать свой ID.
# Узнать свой ID: напиши @userinfobot в Telegram
_raw_users = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS: set[int] = (
    {int(uid.strip()) for uid in _raw_users.split(",") if uid.strip()}
    if _raw_users else set()
)

# Google Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Database
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.db")

# Категории расходов
CATEGORIES = {
    "🍔 Еда": "food",
    "⛽ Транспорт": "transport",
    "🏠 Жильё": "housing",
    "👕 Одежда": "clothing",
    "💊 Здоровье": "health",
    "🎭 Развлечения": "entertainment",
    "📱 Связь": "communication",
    "🎓 Образование": "education",
    "🛒 Покупки": "shopping",
    "💰 Финансы": "finance",
    "🐾 Питомцы": "pets",
    "🔧 Прочее": "other",
}

# Обратный маппинг: slug → emoji-название
CATEGORY_BY_SLUG = {v: k for k, v in CATEGORIES.items()}

# Валюта
CURRENCY = "₽"
