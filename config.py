"""Конфигурация бота."""

import os
import sys
from dotenv import load_dotenv

# Определяем рабочую директорию (рядом с .exe или .py)
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.getcwd()

env_path = os.path.join(base_dir, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

def get_or_prompt(key: str, prompt_text: str, default: str = "") -> str:
    val = os.getenv(key, "").strip()
    if not val:
        print()
        if default:
            val = input(f"{prompt_text} [Нажми Enter для {default}]: ").strip()
            if not val:
                val = default
        else:
            while not val:
                val = input(f"{prompt_text}: ").strip()
        
        # Сохраняем в .env файл
        with open(env_path, "a", encoding="utf-8") as f:
            f.write(f"{key}={val}\n")
        
        os.environ[key] = val
        print(f"✅ {key} сохранён в .env (в папке {base_dir})")
    
    return val

print("🌟 Expense Tracker Bot инициализируется...")

# Telegram Bot
BOT_TOKEN = get_or_prompt("BOT_TOKEN", "🔑 Введите токен Telegram-бота (можно получить у @BotFather в ТГ)")

# Белый список пользователей (Telegram ID через запятую)
_raw_users = get_or_prompt("ALLOWED_USERS", "🛡 Введите ваш Telegram ID, чтобы никто чужой не мог использовать бота (узнать ID можно у @userinfobot)")
ALLOWED_USERS: set[int] = (
    {int(uid.strip()) for uid in _raw_users.split(",") if uid.strip()}
    if _raw_users else set()
)

# Google Gemini AI
GEMINI_API_KEY = get_or_prompt("GEMINI_API_KEY", "🔑 Введите API-ключ Google Gemini (получить на aistudio.google.com)")
GEMINI_MODEL = get_or_prompt("GEMINI_MODEL", "🧠 Введите название модели Gemini (или впишите свою кастомную)", "gemini-1.5-flash")

# Database (сохраняем рядом с exe/py, а не во временной папке PyInstaller)
DB_PATH = os.path.join(base_dir, "expenses.db")

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
