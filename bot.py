"""Точка входа бота для учёта расходов."""

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import TelegramObject, Update

from config import BOT_TOKEN, ALLOWED_USERS, ADMIN_USERS, PROXY_URL
from database import init_db, is_user_blacklisted
from handlers import router

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class AccessMiddleware(BaseMiddleware):
    """Middleware для ограничения доступа по белому списку и проверки ЧС."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Определяем user_id из любого типа события
        user_id = None
        if hasattr(event, "from_user") and event.from_user:
            user_id = event.from_user.id
        elif hasattr(event, "message") and event.message and event.message.from_user:
            user_id = event.message.from_user.id

        if not user_id:
            return await handler(event, data)

        # 1. Проверка на черный список в БД
        if is_user_blacklisted(user_id):
            logger.warning(f"🚫 Пользователь {user_id} в черном списке. Игнорирую.")
            return None

        # 2. Если белый список пуст — пускаем всех (кроме ЧС)
        if not ALLOWED_USERS:
            return await handler(event, data)

        # 3. Проверка на белый список
        if user_id in ALLOWED_USERS or user_id in ADMIN_USERS:
            return await handler(event, data)

        # Чужой пользователь — молча игнорируем
        logger.warning(f"⛔ Доступ запрещён для user_id={user_id}")
        return None


async def on_startup(bot: Bot):
    """Действия при запуске бота."""
    init_db()
    me = await bot.get_me()
    logger.info(f"✅ Бот @{me.username} запущен!")
    if ALLOWED_USERS:
        logger.info(f"🔒 Доступ ограничен: {ALLOWED_USERS}")
    else:
        logger.warning("⚠️ ALLOWED_USERS не задан — бот открыт для всех!")

    # Установка команд меню
    from aiogram.types import BotCommand
    await bot.set_my_commands([
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="help", description="❓ Справка"),
    ])


async def main():
    """Запуск бота."""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не задан! Создай файл .env с токеном.")
        return

    from aiogram.client.session.aiohttp import AiohttpSession
    session = AiohttpSession(proxy=PROXY_URL) if PROXY_URL else None

    bot = Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middleware доступа — регистрируем на все типы событий
    dp.message.middleware(AccessMiddleware())
    dp.callback_query.middleware(AccessMiddleware())

    dp.include_router(router)
    dp.startup.register(on_startup)

    logger.info("🔄 Запуск polling...")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
