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

def get_or_prompt(key: str, prompt_text: str, default: str = "", allow_empty: bool = False) -> str:
    # Проверяем, есть ли переменная (даже если она пустая, но задана)
    if key in os.environ:
        return os.environ[key].strip()
    
    val = os.getenv(key, "")
    if not val and key not in os.environ:
        print()
        if default:
            val = input(f"{prompt_text} [Нажми Enter для {default}]: ").strip()
            if not val:
                val = default
        elif allow_empty:
            val = input(f"{prompt_text} [Нажми Enter, чтобы пропустить]: ").strip()
        else:
            while not val:
                val = input(f"{prompt_text}: ").strip()
        
        # Сохраняем в .env файл
        with open(env_path, "a", encoding="utf-8") as f:
            f.write(f"{key}={val}\n")
        
        os.environ[key] = val
        if val:
            print(f"✅ {key} сохранён в .env (в папке {base_dir})")
        else:
            print(f"✅ {key} пропущен (оставлен пустым)")
    
    return val

print("🌟 Expense Tracker Bot инициализируется...")

# Telegram Bot
BOT_TOKEN = get_or_prompt("BOT_TOKEN", "🔑 Введите токен Telegram-бота (можно получить у @BotFather в ТГ)")

# Белый список пользователей (Telegram ID через запятую)
_raw_users = get_or_prompt("ALLOWED_USERS", "🛡 Введите ваш Telegram ID, чтобы никто чужой не мог использовать бота", allow_empty=True)
ALLOWED_USERS: set[int] = (
    {int(uid.strip()) for uid in _raw_users.split(",") if uid.strip()}
    if _raw_users else set()
)

# Список администраторов (имеют доступ к админке)
_raw_admins = get_or_prompt("ADMIN_USERS", "🔑 Введите Telegram ID администраторов через запятую (для доступа к админке)", allow_empty=True)
ADMIN_USERS: set[int] = (
    {int(uid.strip()) for uid in _raw_admins.split(",") if uid.strip()}
    if _raw_admins else set()
)
# Если ADMIN_USERS не заданы, но задан ALLOWED_USERS, считаем первого из списка админом
if not ADMIN_USERS and ALLOWED_USERS:
    ADMIN_USERS = {list(ALLOWED_USERS)[0]}

# Google Gemini AI
GEMINI_API_KEY = get_or_prompt("GEMINI_API_KEY", "🔑 Введите API-ключ Google Gemini (получить на aistudio.google.com)")
GEMINI_MODEL = get_or_prompt("GEMINI_MODEL", "🧠 Введите название модели Gemini (или впишите свою кастомную)", "gemini-1.5-flash")

# Proxy support
PROXY_URL = os.getenv("PROXY_URL", "").strip()
if PROXY_URL:
    os.environ["HTTP_PROXY"] = PROXY_URL
    os.environ["HTTPS_PROXY"] = PROXY_URL
    os.environ["http_proxy"] = PROXY_URL
    os.environ["https_proxy"] = PROXY_URL
else:
    PROXY_URL = None

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
