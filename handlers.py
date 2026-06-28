"""Обработчики команд и сообщений бота."""

import logging
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import CATEGORY_BY_SLUG, CURRENCY, CATEGORIES, ADMIN_USERS
from database import (
    ensure_user,
    add_expense,
    delete_expense,
    get_last_expenses,
    get_stats_for_period,
    get_daily_breakdown,
    set_budget,
    get_budgets,
    get_monthly_spent,
    get_all_users,
    set_user_blacklist_status,
    is_user_blacklisted,
)
from ai_categorizer import parse_expense, parse_expense_from_image, chat_reply, clear_chat_history
from charts import generate_pie_chart, generate_bar_chart
from keyboards import (
    main_menu_keyboard,
    chat_mode_keyboard,
    stats_period_keyboard,
    chart_keyboard,
    confirm_expense_keyboard,
    category_select_keyboard,
    history_keyboard,
    budget_categories_keyboard,
    delete_confirm_keyboard,
    admin_panel_keyboard,
    admin_user_action_keyboard,
    admin_users_list_keyboard,
)

logger = logging.getLogger(__name__)

router = Router()

ITEMS_PER_PAGE = 5


# ── FSM States ───────────────────────────────────────────────────────────

class BudgetStates(StatesGroup):
    waiting_for_amount = State()

class ChatStates(StatesGroup):
    chatting = State()

class AdminStates(StatesGroup):
    waiting_for_ban_id = State()
    waiting_for_unban_id = State()


# ── Утилиты форматирования ───────────────────────────────────────────────

def fmt_amount(amount: float) -> str:
    """Форматировать сумму."""
    if amount == int(amount):
        return f"{int(amount):,}{CURRENCY}".replace(",", " ")
    return f"{amount:,.2f}{CURRENCY}".replace(",", " ")


def fmt_date(date_str: str) -> str:
    """Форматировать дату."""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%d.%m.%Y %H:%M")
    except (ValueError, TypeError):
        return date_str


def progress_bar(current: float, limit: float, width: int = 10) -> str:
    """Прогресс-бар для бюджета."""
    ratio = min(current / limit, 1.0) if limit > 0 else 0
    filled = int(ratio * width)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    percent = int(ratio * 100)
    if ratio >= 1.0:
        return f"🔴 {bar} {percent}%"
    elif ratio >= 0.75:
        return f"🟡 {bar} {percent}%"
    else:
        return f"🟢 {bar} {percent}%"


# ── Команды ──────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик /start."""
    ensure_user(message.from_user.id, message.from_user.username,
                message.from_user.first_name)

    name = message.from_user.first_name or "друг"
    await message.answer(
        f"👋 Привет, <b>{name}</b>!\n\n"
        "Я твой личный бот для учёта расходов 💸\n\n"
        "📝 <b>Как записать трату:</b>\n"
        "Просто напиши, что и сколько потратил:\n"
        "<code>кофе старбакс 350</code>\n"
        "<code>такси до работы 500</code>\n"
        "<code>продукты пятёрочка 2300</code>\n\n"
        "🤖 Я автоматически определю категорию с помощью ИИ\n"
        "и запишу трату в базу.\n\n"
        "👇 Используй меню внизу для навигации:",
        reply_markup=main_menu_keyboard(message.from_user.id),
        parse_mode="HTML",
    )


@router.message(Command("help"))
@router.message(F.text == "❓ Помощь")
async def cmd_help(message: Message):
    """Обработчик /help."""
    await message.answer(
        "📖 <b>Справка по боту</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📝 <b>Запись трат</b>\n"
        "Просто напиши сообщение с описанием и суммой:\n"
        "• <code>бензин лукойл 2000</code>\n"
        "• <code>обед в кафе 650</code>\n"
        "• <code>подписка youtube 400</code>\n\n"
        "🤖 ИИ автоматически определит категорию!\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📊 <b>Статистика</b> — общая сводка трат\n"
        "📋 <b>История</b> — последние записи\n"
        "📈 <b>По дням</b> — траты за каждый день\n"
        "💰 <b>Бюджеты</b> — лимиты по категориям\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "После записи траты можно:\n"
        "• ✏️ Изменить категорию\n"
        "• 🗑 Удалить запись",
        parse_mode="HTML",
    )


# ── Статистика ───────────────────────────────────────────────────────────

@router.message(F.text == "📊 Статистика")
async def menu_stats(message: Message):
    """Меню статистики."""
    await message.answer(
        "📊 <b>Статистика расходов</b>\n\nВыбери период:",
        reply_markup=stats_period_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("stats:"))
async def cb_stats(callback: CallbackQuery):
    """Показать статистику за выбранный период."""
    period = callback.data.split(":")[1]
    days = None if period == "all" else int(period)

    period_names = {"1": "сегодня", "7": "неделю", "30": "месяц", "all": "всё время"}
    period_name = period_names.get(period, period)

    stats = get_stats_for_period(callback.from_user.id, days)

    if stats["count"] == 0:
        await callback.message.edit_text(
            f"📊 <b>Статистика за {period_name}</b>\n\n"
            "🤷 Записей нет. Начни записывать траты!",
            parse_mode="HTML",
        )
        await callback.answer()
        return

    # Формируем текст
    lines = [
        f"📊 <b>Статистика за {period_name}</b>\n",
        f"💵 Всего потрачено: <b>{fmt_amount(stats['total'])}</b>",
        f"📝 Записей: <b>{stats['count']}</b>",
        f"📐 Средний чек: <b>{fmt_amount(stats['total'] / stats['count'])}</b>\n",
        "━━━━━━━━━━━━━━━━━━",
        "📂 <b>По категориям:</b>\n",
    ]

    for cat in stats["by_category"]:
        cat_name = CATEGORY_BY_SLUG.get(cat["slug"], f"❓ {cat['slug']}")
        percent = (cat["total"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        bar_len = int(percent / 10)
        bar = "▓" * bar_len + "░" * (10 - bar_len)
        lines.append(
            f"{cat_name}\n"
            f"  {bar} {percent:.0f}%\n"
            f"  {fmt_amount(cat['total'])} ({cat['count']} шт.)\n"
        )

    await callback.message.edit_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=stats_period_keyboard(),
    )
    await callback.answer()


# ── История ──────────────────────────────────────────────────────────────

@router.message(F.text == "📋 История")
async def menu_history(message: Message):
    """Показать историю трат."""
    await show_history(message, page=0, is_new=True)


@router.callback_query(F.data.startswith("history:"))
async def cb_history(callback: CallbackQuery):
    """Пагинация истории."""
    page = int(callback.data.split(":")[1])
    await show_history(callback.message, page=page, is_new=False,
                       user_id=callback.from_user.id)
    await callback.answer()


async def show_history(message: Message, page: int, is_new: bool,
                       user_id: int = None):
    """Отобразить страницу истории."""
    uid = user_id or message.from_user.id
    offset = page * ITEMS_PER_PAGE
    expenses = get_last_expenses(uid, limit=100)

    if not expenses:
        text = "📋 <b>История трат</b>\n\n🤷 Пока ничего нет!"
        if is_new:
            await message.answer(text, parse_mode="HTML")
        else:
            await message.edit_text(text, parse_mode="HTML")
        return

    page_items = expenses[offset:offset + ITEMS_PER_PAGE]
    has_next = len(expenses) > offset + ITEMS_PER_PAGE
    total_pages = (len(expenses) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    lines = [f"📋 <b>История трат</b> (стр. {page + 1}/{total_pages})\n"]

    for exp in page_items:
        cat_name = CATEGORY_BY_SLUG.get(exp["category_slug"], "❓")
        lines.append(
            f"├ {cat_name} — <b>{fmt_amount(exp['amount'])}</b>\n"
            f"│  {exp['description']}\n"
            f"│  🕐 {fmt_date(exp['created_at'])}  •  ID: {exp['id']}\n"
        )

    keyboard = history_keyboard(page, has_next)

    if is_new:
        await message.answer("\n".join(lines), parse_mode="HTML",
                             reply_markup=keyboard)
    else:
        await message.edit_text("\n".join(lines), parse_mode="HTML",
                                reply_markup=keyboard)


# ── По дням ──────────────────────────────────────────────────────────────

@router.message(F.text == "📈 По дням")
async def menu_daily(message: Message):
    """Статистика по дням."""
    breakdown = get_daily_breakdown(message.from_user.id, days=7)

    if not breakdown:
        await message.answer(
            "📈 <b>Траты по дням</b>\n\n🤷 Данных пока нет!",
            parse_mode="HTML",
        )
        return

    max_total = max(d["total"] for d in breakdown) if breakdown else 1
    lines = ["📈 <b>Траты по дням (7 дней)</b>\n"]

    for day in breakdown:
        bar_len = int((day["total"] / max_total) * 12) if max_total > 0 else 0
        bar = "▓" * bar_len + "░" * (12 - bar_len)

        try:
            dt = datetime.strptime(day["day"], "%Y-%m-%d")
            day_str = dt.strftime("%d.%m %a")
            day_str = day_str.replace("Mon", "Пн").replace("Tue", "Вт")
            day_str = day_str.replace("Wed", "Ср").replace("Thu", "Чт")
            day_str = day_str.replace("Fri", "Пт").replace("Sat", "Сб")
            day_str = day_str.replace("Sun", "Вс")
        except ValueError:
            day_str = day["day"]

        lines.append(
            f"<code>{day_str}</code> {bar}\n"
            f"           <b>{fmt_amount(day['total'])}</b> • {day['count']} зап.\n"
        )

    await message.answer("\n".join(lines), parse_mode="HTML")


# ── Диаграммы ────────────────────────────────────────────────────────────

@router.message(F.text == "📉 Диаграммы")
async def menu_charts(message: Message):
    """Меню диаграмм."""
    await message.answer(
        "📉 <b>Диаграммы расходов</b>\n\nВыбери тип и период:",
        reply_markup=chart_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("chart:"))
async def cb_chart(callback: CallbackQuery):
    """Генерация и отправка диаграммы."""
    parts = callback.data.split(":")
    chart_type = parts[1]  # pie или bar
    period = parts[2]      # число дней или 'all'
    days = None if period == "all" else int(period)

    await callback.answer("📊 Генерирую диаграмму...")

    try:
        if chart_type == "pie":
            image_bytes = generate_pie_chart(callback.from_user.id, days)
        else:
            image_bytes = generate_bar_chart(callback.from_user.id, days or 14)

        if image_bytes is None:
            await callback.message.answer(
                "🤷 Недостаточно данных для построения диаграммы.",
            )
            return

        photo = BufferedInputFile(image_bytes, filename="chart.png")
        await callback.message.answer_photo(
            photo=photo,
            caption="📊 Диаграмма расходов",
        )

    except Exception as e:
        logger.error(f"Ошибка генерации диаграммы: {e}")
        await callback.message.answer("❌ Не удалось построить диаграмму.")


# ── Бюджеты ──────────────────────────────────────────────────────────────

@router.message(F.text == "💰 Бюджеты")
async def menu_budgets(message: Message):
    """Показать бюджеты и предложить установить."""
    budgets = get_budgets(message.from_user.id)

    if not budgets:
        await message.answer(
            "💰 <b>Бюджеты</b>\n\n"
            "У тебя пока нет установленных бюджетов.\n"
            "Выбери категорию, чтобы установить лимит:",
            reply_markup=budget_categories_keyboard(),
            parse_mode="HTML",
        )
        return

    lines = ["💰 <b>Бюджеты на месяц</b>\n"]

    for b in budgets:
        cat_name = CATEGORY_BY_SLUG.get(b["category_slug"], "❓")
        spent = get_monthly_spent(message.from_user.id, b["category_slug"])
        remaining = b["monthly_limit"] - spent
        bar = progress_bar(spent, b["monthly_limit"])

        lines.append(
            f"{cat_name}\n"
            f"  {bar}\n"
            f"  {fmt_amount(spent)} / {fmt_amount(b['monthly_limit'])}\n"
            f"  {'⚠️ Превышен!' if remaining < 0 else f'Осталось: {fmt_amount(max(0, remaining))}'}\n"
        )

    lines.append("\n📎 Установить новый лимит ↓")

    await message.answer(
        "\n".join(lines),
        reply_markup=budget_categories_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("budget:"))
async def cb_budget_select(callback: CallbackQuery, state: FSMContext):
    """Выбор категории для бюджета."""
    slug = callback.data.split(":")[1]
    cat_name = CATEGORY_BY_SLUG.get(slug, slug)

    await state.set_state(BudgetStates.waiting_for_amount)
    await state.update_data(budget_category=slug)

    await callback.message.edit_text(
        f"💰 <b>Бюджет для {cat_name}</b>\n\n"
        "Введи месячный лимит (число):",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(BudgetStates.waiting_for_amount)
async def process_budget_amount(message: Message, state: FSMContext):
    """Обработка ввода суммы бюджета."""
    try:
        amount = float(message.text.replace(" ", "").replace(",", "."))
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        await message.answer("❌ Введи корректную сумму (положительное число).")
        return

    data = await state.get_data()
    slug = data["budget_category"]
    cat_name = CATEGORY_BY_SLUG.get(slug, slug)

    set_budget(message.from_user.id, slug, amount)
    await state.clear()

    await message.answer(
        f"✅ Бюджет установлен!\n\n"
        f"📂 Категория: {cat_name}\n"
        f"💰 Лимит: <b>{fmt_amount(amount)}</b> в месяц",
        parse_mode="HTML",
    )


# ── Обработка фото (Vision AI) ───────────────────────────────────────────

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Обработчик фото — распознавание чеков и скриншотов."""
    current_state = await state.get_state()
    if current_state is not None:
        return

    ensure_user(message.from_user.id, message.from_user.username,
                message.from_user.first_name)

    processing = await message.answer(
        "🔍 <i>Распознаю фото...</i>", parse_mode="HTML",
    )

    try:
        # Скачиваем фото (берём самое большое разрешение)
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        image_data = file_bytes.read()

        # Распознаём через Vision AI
        results = await parse_expense_from_image(image_data)
    except Exception as e:
        logger.error(f"Ошибка обработки фото: {e}")
        results = None

    if not results:
        await processing.edit_text(
            "🤔 Не удалось распознать траты на фото.\n\n"
            "💡 Попробуй прислать:\n"
            "• 📸 Фото чека\n"
            "• 📱 Скриншот перевода\n"
            "• 🏦 Скриншот из банковского приложения",
            parse_mode="HTML",
        )
        return

    # Записываем все найденные траты
    total = 0
    lines = [f"📸 <b>Распознано трат: {len(results)}</b>\n"]

    for item in results:
        expense_id = add_expense(
            user_id=message.from_user.id,
            amount=item["amount"],
            description=item["description"],
            category_slug=item["category"],
        )
        cat_name = CATEGORY_BY_SLUG.get(item["category"], "❓ Прочее")
        total += item["amount"]
        lines.append(
            f"├ {cat_name} — <b>{fmt_amount(item['amount'])}</b>\n"
            f"│  {item['description']}  •  ID: {expense_id}\n"
        )

    lines.append(f"\n💵 Итого: <b>{fmt_amount(total)}</b>")

    await processing.edit_text(
        "\n".join(lines),
        parse_mode="HTML",
    )


# ── Режим чата с ИИ ─────────────────────────────────────────────────────

@router.message(F.text == "💬 Чат с ИИ")
async def enter_chat_mode(message: Message, state: FSMContext):
    """Вход в режим чата."""
    await state.set_state(ChatStates.chatting)
    clear_chat_history(message.from_user.id)

    await message.answer(
        "💬 <b>Режим чата с ИИ</b>\n\n"
        "Теперь я — твой личный AI-ассистент. "
        "Спрашивай что угодно!\n\n"
        "💡 История диалога сохраняется — я помню контекст.\n"
        'Нажми <b>«🚪 Выйти из чата»</b> для возврата к учёту трат.',
        reply_markup=chat_mode_keyboard(),
        parse_mode="HTML",
    )


@router.message(ChatStates.chatting, F.text == "🚪 Выйти из чата")
async def exit_chat_mode(message: Message, state: FSMContext):
    """Выход из режима чата."""
    clear_chat_history(message.from_user.id)
    await state.clear()
    await message.answer(
        "✅ Вернулись в режим учёта трат.\n"
        "Пиши траты как обычно!",
        reply_markup=main_menu_keyboard(message.from_user.id),
        parse_mode="HTML",
    )


@router.message(ChatStates.chatting, F.text)
async def handle_chat_message(message: Message):
    """Обработка сообщения в режиме чата."""
    typing = await message.answer("✒️ <i>Пишу...</i>", parse_mode="HTML")

    reply = await chat_reply(message.from_user.id, message.text)

    # Telegram ограничивает сообщения 4096 символами
    if len(reply) > 4000:
        reply = reply[:4000] + "\n\n… <i>(ответ обрезан)</i>"

    try:
        await typing.edit_text(reply, parse_mode="HTML")
    except Exception:
        # Если HTML-разметка сломана — отправляем без неё
        await typing.edit_text(reply, parse_mode=None)


# ── Админка ──────────────────────────────────────────────────────────────

@router.message(Command("admin"))
@router.message(F.text == "⚙️ Админка")
async def cmd_admin(message: Message):
    """Вход в админку."""
    # Строгая проверка на один ID
    if message.from_user.id != 1936852161:
        return

    await message.answer(
        "⚙️ <b>Панель администратора</b>\n\n"
        "Здесь вы можете управлять пользователями бота.",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "admin:back")
async def cb_admin_back(callback: CallbackQuery):
    """Возврат в главное меню админки."""
    if callback.from_user.id != 1936852161:
        return

    await callback.message.edit_text(
        "⚙️ <b>Панель администратора</b>\n\n"
        "Здесь вы можете управлять пользователями бота.",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "admin:users")
async def cb_admin_users(callback: CallbackQuery):
    """Список всех пользователей."""
    if callback.from_user.id != 1936852161:
        return

    users = get_all_users()
    if not users:
        await callback.message.edit_text("🤷 Пользователей пока нет.")
        return

    lines = ["👥 <b>Список пользователей:</b>\n"]
    for u in users:
        status = "🚫 ЧС" if u["is_blacklisted"] else "✅ Активен"
        username = f"@{u['username']}" if u['username'] else "нет username"
        lines.append(
            f"👤 {u['first_name']} ({username})\n"
            f"🆔 <code>{u['telegram_id']}</code> | {status}\n"
        )

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "admin:list_to_ban")
async def cb_admin_list_to_ban(callback: CallbackQuery):
    """Список активных пользователей для бана."""
    if callback.from_user.id != 1936852161:
        return

    users = [u for u in get_all_users() if not u["is_blacklisted"]]
    # Исключаем самого админа из списка на бан
    users = [u for u in users if u["telegram_id"] != 1936852161]

    if not users:
        await callback.answer("Нет активных пользователей для бана", show_alert=True)
        return

    await callback.message.edit_text(
        "🚫 <b>Выберите пользователя для бана:</b>",
        reply_markup=admin_users_list_keyboard(users, "ban"),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin:list_to_unban")
async def cb_admin_list_to_unban(callback: CallbackQuery):
    """Список забаненных пользователей для разбана."""
    if callback.from_user.id != 1936852161:
        return

    users = [u for u in get_all_users() if u["is_blacklisted"]]

    if not users:
        await callback.answer("Черный список пуст", show_alert=True)
        return

    await callback.message.edit_text(
        "✅ <b>Выберите пользователя для разбана:</b>",
        reply_markup=admin_users_list_keyboard(users, "unban"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("admin_act:"))
async def cb_admin_action(callback: CallbackQuery):
    """Выполнение действия над пользователем из списка."""
    if callback.from_user.id != 1936852161:
        return

    parts = callback.data.split(":")
    action = parts[1]
    target_id = int(parts[2])

    status = True if action == "ban" else False
    set_user_blacklist_status(target_id, status)

    msg = "заблокирован 🚫" if status else "разблокирован ✅"
    await callback.answer(f"Пользователь {msg}")

    # После действия возвращаемся к соответствующему списку
    if action == "ban":
        await cb_admin_list_to_ban(callback)
    else:
        await cb_admin_list_to_unban(callback)


# ── Обработка трат (текст) ───────────────────────────────────────────────

# ПЕРЕНЕСЕНО В КОНЕЦ ФАЙЛА ДЛЯ ПРАВИЛЬНОГО ПРИОРИТЕТА ХЕНДЛЕРОВ


# ── Callback: изменение категории ────────────────────────────────────────

@router.callback_query(F.data.startswith("chcat:"))
async def cb_change_category(callback: CallbackQuery):
    """Показать выбор категории."""
    expense_id = int(callback.data.split(":")[1])
    await callback.message.edit_reply_markup(
        reply_markup=category_select_keyboard(expense_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("setcat:"))
async def cb_set_category(callback: CallbackQuery):
    """Установить новую категорию."""
    parts = callback.data.split(":")
    expense_id = int(parts[1])
    new_slug = parts[2]

    from database import get_connection
    conn = get_connection()
    conn.execute(
        "UPDATE expenses SET category_slug = ? WHERE id = ? AND user_id = ?",
        (new_slug, expense_id, callback.from_user.id),
    )
    conn.commit()

    # Получаем обновлённую запись
    row = conn.execute(
        "SELECT amount, description, category_slug FROM expenses WHERE id = ?",
        (expense_id,),
    ).fetchone()
    conn.close()

    if row:
        cat_name = CATEGORY_BY_SLUG.get(row["category_slug"], "❓")
        await callback.message.edit_text(
            f"✅ <b>Категория изменена!</b>\n\n"
            f"📂 Категория: {cat_name}\n"
            f"📝 Описание: {row['description']}\n"
            f"💵 Сумма: <b>{fmt_amount(row['amount'])}</b>",
            reply_markup=confirm_expense_keyboard(expense_id),
            parse_mode="HTML",
        )
    await callback.answer("Категория обновлена ✅")


# ── Callback: удаление ───────────────────────────────────────────────────

@router.callback_query(F.data.startswith("del:"))
async def cb_delete_prompt(callback: CallbackQuery):
    """Запрос подтверждения удаления."""
    expense_id = int(callback.data.split(":")[1])
    await callback.message.edit_reply_markup(
        reply_markup=delete_confirm_keyboard(expense_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_del:"))
async def cb_confirm_delete(callback: CallbackQuery):
    """Подтверждение удаления."""
    expense_id = int(callback.data.split(":")[1])
    deleted = delete_expense(expense_id, callback.from_user.id)

    if deleted:
        await callback.message.edit_text(
            "🗑 <b>Трата удалена</b>",
            parse_mode="HTML",
        )
        await callback.answer("Удалено ✅")
    else:
        await callback.answer("Запись не найдена ❌")


@router.callback_query(F.data == "cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext = None):
    """Отмена действия."""
    if state:
        await state.clear()
    await callback.message.delete()
    await callback.answer("Отменено")


# ── Обработка трат (текст) ───────────────────────────────────────────────

@router.message(F.text)
async def handle_expense(message: Message, state: FSMContext):
    """Основной обработчик — парсинг траты через AI."""
    # Пропускаем, если это состояние FSM
    current_state = await state.get_state()
    if current_state is not None:
        return

    ensure_user(message.from_user.id, message.from_user.username,
                message.from_user.first_name)

    # Отправляем индикатор обработки
    processing = await message.answer("🤖 <i>Анализирую...</i>", parse_mode="HTML")

    try:
        # Парсим через AI
        result = await parse_expense(message.text)
    except Exception as e:
        logger.error(f"Необработанная ошибка в parse_expense: {e}")
        result = None

    if result is None:
        await processing.edit_text(
            "🤔 Не могу распознать трату.\n\n"
            "💡 Попробуй написать в формате:\n"
            "<code>описание сумма</code>\n\n"
            "Например: <code>кофе старбакс 350</code>",
            parse_mode="HTML",
        )
        return

    # Записываем в БД
    expense_id = add_expense(
        user_id=message.from_user.id,
        amount=result["amount"],
        description=result["description"],
        category_slug=result["category"],
    )

    cat_name = CATEGORY_BY_SLUG.get(result["category"], "❓ Прочее")

    # Проверяем бюджет
    budget_warning = ""
    budgets = get_budgets(message.from_user.id)
    for b in budgets:
        if b["category_slug"] == result["category"]:
            spent = get_monthly_spent(message.from_user.id, result["category"])
            if spent > b["monthly_limit"]:
                over = spent - b["monthly_limit"]
                budget_warning = (
                    f"\n\n⚠️ <b>Бюджет превышен!</b>\n"
                    f"Лимит: {fmt_amount(b['monthly_limit'])}\n"
                    f"Потрачено: {fmt_amount(spent)}\n"
                    f"Перерасход: {fmt_amount(over)}"
                )
            elif spent > b["monthly_limit"] * 0.8:
                remaining = b["monthly_limit"] - spent
                budget_warning = (
                    f"\n\n🟡 Осталось {fmt_amount(remaining)} "
                    f"из {fmt_amount(b['monthly_limit'])} бюджета"
                )
            break

    await processing.edit_text(
        f"✅ <b>Трата записана!</b>\n\n"
        f"📂 Категория: {cat_name}\n"
        f"📝 Описание: {result['description']}\n"
        f"💵 Сумма: <b>{fmt_amount(result['amount'])}</b>"
        f"{budget_warning}",
        reply_markup=confirm_expense_keyboard(expense_id),
        parse_mode="HTML",
    )
