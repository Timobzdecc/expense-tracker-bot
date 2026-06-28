"""Модуль работы с базой данных SQLite."""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional

from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """Получить соединение с БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Инициализация таблиц БД."""
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            is_blacklisted INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            category_slug TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id)
        );

        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_slug TEXT NOT NULL,
            monthly_limit REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id),
            UNIQUE(user_id, category_slug)
        );

        CREATE INDEX IF NOT EXISTS idx_expenses_user ON expenses(user_id);
        CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(created_at);
        CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category_slug);
    """)
    # Миграция: добавляем колонку is_blacklisted, если её нет (для старых БД)
    try:
        conn.execute("ALTER TABLE users ADD COLUMN is_blacklisted INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Колонка уже существует

    conn.commit()
    conn.close()


def ensure_user(telegram_id: int, username: Optional[str] = None,
                first_name: Optional[str] = None) -> None:
    """Создать пользователя, если не существует."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO users (telegram_id, username, first_name)
           VALUES (?, ?, ?)
           ON CONFLICT(telegram_id) DO UPDATE SET
               username = excluded.username,
               first_name = excluded.first_name""",
        (telegram_id, username, first_name),
    )
    conn.commit()
    conn.close()


def is_user_blacklisted(telegram_id: int) -> bool:
    """Проверить, находится ли пользователь в ЧС."""
    conn = get_connection()
    row = conn.execute(
        "SELECT is_blacklisted FROM users WHERE telegram_id = ?",
        (telegram_id,)
    ).fetchone()
    conn.close()
    return bool(row["is_blacklisted"]) if row else False


def set_user_blacklist_status(telegram_id: int, status: bool) -> None:
    """Добавить или удалить пользователя из ЧС."""
    conn = get_connection()
    conn.execute(
        "UPDATE users SET is_blacklisted = ? WHERE telegram_id = ?",
        (int(status), telegram_id)
    )
    conn.commit()
    conn.close()


def get_all_users() -> list[dict]:
    """Получить список всех пользователей."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_expense(user_id: int, amount: float, description: str,
                category_slug: str) -> int:
    """Добавить трату. Возвращает ID записи."""
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO expenses (user_id, amount, description, category_slug)
           VALUES (?, ?, ?, ?)""",
        (user_id, amount, description, category_slug),
    )
    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return expense_id


def delete_expense(expense_id: int, user_id: int) -> bool:
    """Удалить трату по ID. Возвращает True если удалена."""
    conn = get_connection()
    cursor = conn.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, user_id),
    )
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def get_last_expenses(user_id: int, limit: int = 10) -> list[dict]:
    """Получить последние N трат."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, amount, description, category_slug, created_at
           FROM expenses WHERE user_id = ?
           ORDER BY created_at DESC LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats_for_period(user_id: int, days: Optional[int] = None) -> dict:
    """Получить статистику трат за период.

    Args:
        user_id: ID пользователя в Telegram.
        days: Количество дней (None = за всё время).

    Returns:
        dict с total, count, by_category.
    """
    conn = get_connection()

    if days is not None:
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d 00:00:00")
        where = "WHERE user_id = ? AND created_at >= ?"
        params: tuple = (user_id, since)
    else:
        where = "WHERE user_id = ?"
        params = (user_id,)

    # Общая сумма и количество
    row = conn.execute(
        f"SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count FROM expenses {where}",
        params,
    ).fetchone()
    total = row["total"]
    count = row["count"]

    # По категориям
    cat_rows = conn.execute(
        f"""SELECT category_slug, SUM(amount) as total, COUNT(*) as count
            FROM expenses {where}
            GROUP BY category_slug
            ORDER BY total DESC""",
        params,
    ).fetchall()

    by_category = [
        {"slug": r["category_slug"], "total": r["total"], "count": r["count"]}
        for r in cat_rows
    ]

    conn.close()
    return {"total": total, "count": count, "by_category": by_category}


def get_daily_breakdown(user_id: int, days: int = 7) -> list[dict]:
    """Получить разбивку трат по дням."""
    conn = get_connection()
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d 00:00:00")
    rows = conn.execute(
        """SELECT DATE(created_at) as day, SUM(amount) as total, COUNT(*) as count
           FROM expenses
           WHERE user_id = ? AND created_at >= ?
           GROUP BY DATE(created_at)
           ORDER BY day DESC""",
        (user_id, since),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_budget(user_id: int, category_slug: str, limit: float) -> None:
    """Установить бюджет на категорию."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO budgets (user_id, category_slug, monthly_limit)
           VALUES (?, ?, ?)
           ON CONFLICT(user_id, category_slug) DO UPDATE SET
               monthly_limit = excluded.monthly_limit""",
        (user_id, category_slug, limit),
    )
    conn.commit()
    conn.close()


def get_budgets(user_id: int) -> list[dict]:
    """Получить все бюджеты пользователя."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT category_slug, monthly_limit FROM budgets WHERE user_id = ?",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_monthly_spent(user_id: int, category_slug: str) -> float:
    """Получить сумму трат за текущий месяц по категории."""
    conn = get_connection()
    now = datetime.now()
    first_day = now.replace(day=1).strftime("%Y-%m-%d 00:00:00")
    row = conn.execute(
        """SELECT COALESCE(SUM(amount), 0) as total
           FROM expenses
           WHERE user_id = ? AND category_slug = ? AND created_at >= ?""",
        (user_id, category_slug, first_day),
    ).fetchone()
    conn.close()
    return row["total"]
