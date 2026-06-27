"""Генерация диаграмм расходов."""

import io
import logging
from datetime import datetime, timedelta
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Без GUI, рендер в буфер
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

from config import CATEGORY_BY_SLUG, CURRENCY
from database import get_stats_for_period, get_daily_breakdown

logger = logging.getLogger(__name__)

# ── Стиль диаграмм ──────────────────────────────────────────────────────

# Тёмная тема
BG_COLOR = "#1a1a2e"
CARD_COLOR = "#16213e"
TEXT_COLOR = "#e0e0e0"
GRID_COLOR = "#2a2a4a"
ACCENT_COLORS = [
    "#e94560", "#0f3460", "#533483", "#48c9b0",
    "#f39c12", "#3498db", "#e74c3c", "#2ecc71",
    "#9b59b6", "#1abc9c", "#e67e22", "#95a5a6",
]

plt.rcParams.update({
    "figure.facecolor": BG_COLOR,
    "axes.facecolor": CARD_COLOR,
    "axes.edgecolor": GRID_COLOR,
    "axes.labelcolor": TEXT_COLOR,
    "text.color": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
    "grid.color": GRID_COLOR,
    "grid.alpha": 0.3,
    "font.size": 12,
})


def _fig_to_bytes(fig: plt.Figure) -> bytes:
    """Конвертировать matplotlib Figure в PNG bytes."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor(), edgecolor="none")
    buf.seek(0)
    data = buf.read()
    plt.close(fig)
    return data


# ── Круговая диаграмма по категориям ─────────────────────────────────────

def generate_pie_chart(user_id: int, days: Optional[int] = None) -> Optional[bytes]:
    """Круговая диаграмма трат по категориям.

    Returns:
        PNG-байты или None если нет данных.
    """
    stats = get_stats_for_period(user_id, days)
    if stats["count"] == 0:
        return None

    categories = stats["by_category"]

    labels = []
    sizes = []
    colors = []

    for i, cat in enumerate(categories):
        cat_name = CATEGORY_BY_SLUG.get(cat["slug"], cat["slug"])
        # Убираем эмодзи для диаграммы (matplotlib не рендерит)
        clean_name = cat_name.split(" ", 1)[-1] if " " in cat_name else cat_name
        labels.append(f'{clean_name}\n{cat["total"]:,.0f}{CURRENCY}')
        sizes.append(cat["total"])
        colors.append(ACCENT_COLORS[i % len(ACCENT_COLORS)])

    fig, ax = plt.subplots(figsize=(9, 6))

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None, # Убираем подписи с самих долек, чтобы они не слипались
        colors=colors,
        autopct=lambda pct: f"{pct:.0f}%" if pct > 3 else "", # Показываем проценты только для долей > 3%
        startangle=90,
        pctdistance=0.7,
        wedgeprops={"linewidth": 2, "edgecolor": BG_COLOR},
    )

    # Добавляем красивую легенду справа от диаграммы
    ax.legend(
        wedges,
        labels,
        title="Категории",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        frameon=True,
        facecolor=CARD_COLOR,
        edgecolor=GRID_COLOR,
    )

    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight("bold")
        autotext.set_color("white")

    # Заголовок
    period_names = {None: "всё время", 1: "сегодня", 7: "неделю", 30: "месяц"}
    period = period_names.get(days, f"{days} дн.")
    ax.set_title(
        f"Расходы за {period}: {stats['total']:,.0f}{CURRENCY}",
        fontsize=16, fontweight="bold", pad=20, color=TEXT_COLOR,
    )

    return _fig_to_bytes(fig)


# ── Столбчатая диаграмма по дням ─────────────────────────────────────────

def generate_bar_chart(user_id: int, days: int = 14) -> Optional[bytes]:
    """Столбчатая диаграмма трат по дням.

    Returns:
        PNG-байты или None если нет данных.
    """
    breakdown = get_daily_breakdown(user_id, days=days)
    if not breakdown:
        return None

    # Парсим даты и суммы
    dates = []
    amounts = []
    for row in reversed(breakdown):  # от старых к новым
        try:
            dt = datetime.strptime(row["day"], "%Y-%m-%d")
            dates.append(dt)
            amounts.append(row["total"])
        except ValueError:
            continue

    if not dates:
        return None

    fig, ax = plt.subplots(figsize=(10, 5))

    # Градиент цвета столбцов по высоте
    max_amount = max(amounts) if amounts else 1
    bar_colors = []
    for a in amounts:
        ratio = a / max_amount
        if ratio > 0.75:
            bar_colors.append("#e94560")
        elif ratio > 0.5:
            bar_colors.append("#f39c12")
        elif ratio > 0.25:
            bar_colors.append("#48c9b0")
        else:
            bar_colors.append("#3498db")

    bars = ax.bar(dates, amounts, color=bar_colors, width=0.7,
                  edgecolor=BG_COLOR, linewidth=1.5, zorder=3)

    # Подписи сумм над столбцами
    for bar, amount in zip(bars, amounts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max_amount * 0.02,
            f"{amount:,.0f}",
            ha="center", va="bottom", fontsize=8,
            color=TEXT_COLOR, fontweight="bold",
        )

    # Оформление осей
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates) // 10)))
    plt.xticks(rotation=45, ha="right")

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(
        lambda x, _: f"{x:,.0f}"
    ))

    ax.grid(axis="y", linestyle="--", alpha=0.3, zorder=0)
    ax.set_axisbelow(True)

    # Средняя линия
    avg = sum(amounts) / len(amounts) if amounts else 0
    ax.axhline(y=avg, color="#e94560", linestyle="--", alpha=0.6, linewidth=1.5)
    ax.text(
        dates[-1], avg + max_amount * 0.03,
        f"Среднее: {avg:,.0f}{CURRENCY}",
        color="#e94560", fontsize=9, ha="right", fontweight="bold",
    )

    total = sum(amounts)
    ax.set_title(
        f"Траты по дням — итого {total:,.0f}{CURRENCY}",
        fontsize=14, fontweight="bold", pad=15, color=TEXT_COLOR,
    )
    ax.set_xlabel("")
    ax.set_ylabel(f"Сумма, {CURRENCY}", fontsize=11)

    fig.tight_layout()
    return _fig_to_bytes(fig)
