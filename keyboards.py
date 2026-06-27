"""Клавиатуры для Telegram-бота."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from config import CATEGORIES, CATEGORY_BY_SLUG


# ── Reply-клавиатура (главное меню) ──────────────────────────────────────

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню бота (постоянная клавиатура)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📋 История")],
            [KeyboardButton(text="📈 По дням"), KeyboardButton(text="💰 Бюджеты")],
            [KeyboardButton(text="📉 Диаграммы"), KeyboardButton(text="💬 Чат с ИИ")],
            [KeyboardButton(text="❓ Помощь")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Введите трату: кофе старбакс 350",
    )


def chat_mode_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура в режиме чата."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚪 Выйти из чата")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Спроси что угодно...",
    )


# ── Inline-клавиатуры ────────────────────────────────────────────────────

def stats_period_keyboard() -> InlineKeyboardMarkup:
    """Выбор периода статистики."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 Сегодня", callback_data="stats:1"),
            InlineKeyboardButton(text="📅 Неделя", callback_data="stats:7"),
        ],
        [
            InlineKeyboardButton(text="📅 Месяц", callback_data="stats:30"),
            InlineKeyboardButton(text="📅 Всё время", callback_data="stats:all"),
        ],
    ])


def chart_keyboard() -> InlineKeyboardMarkup:
    """Выбор типа диаграммы."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🥧 По категориям (неделя)", callback_data="chart:pie:7"),
            InlineKeyboardButton(text="🥧 По категориям (месяц)", callback_data="chart:pie:30"),
        ],
        [
            InlineKeyboardButton(text="📊 По дням (2 недели)", callback_data="chart:bar:14"),
            InlineKeyboardButton(text="📊 По дням (месяц)", callback_data="chart:bar:30"),
        ],
        [
            InlineKeyboardButton(text="🥧 За всё время", callback_data="chart:pie:all"),
        ],
    ])


def confirm_expense_keyboard(expense_id: int) -> InlineKeyboardMarkup:
    """Кнопки после добавления траты."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Изменить категорию", callback_data=f"chcat:{expense_id}"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"del:{expense_id}"),
        ],
    ])


def category_select_keyboard(expense_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора категории для изменения."""
    buttons = []
    row = []
    for emoji_name, slug in CATEGORIES.items():
        row.append(
            InlineKeyboardButton(
                text=emoji_name,
                callback_data=f"setcat:{expense_id}:{slug}",
            )
        )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def history_keyboard(page: int, has_next: bool) -> InlineKeyboardMarkup:
    """Пагинация истории."""
    buttons = []
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"history:{page - 1}"))
    if has_next:
        nav_row.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"history:{page + 1}"))
    if nav_row:
        buttons.append(nav_row)
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None


def budget_categories_keyboard() -> InlineKeyboardMarkup:
    """Выбор категории для установки бюджета."""
    buttons = []
    row = []
    for emoji_name, slug in CATEGORIES.items():
        row.append(
            InlineKeyboardButton(
                text=emoji_name,
                callback_data=f"budget:{slug}",
            )
        )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def delete_confirm_keyboard(expense_id: int) -> InlineKeyboardMarkup:
    """Подтверждение удаления."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_del:{expense_id}"),
            InlineKeyboardButton(text="❌ Нет", callback_data="cancel"),
        ],
    ])
