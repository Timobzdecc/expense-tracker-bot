"""AI-категоризатор расходов на базе Google Gemini.

Архитектура:
1. Regex извлекает сумму и описание из сообщения (надёжно, без AI)
2. AI определяет только категорию (если доступен)
3. Если AI заблокирован/недоступен — ставим категорию «Прочее»
→ Трата записывается ВСЕГДА, если в сообщении есть число.
"""

import asyncio
import json
import logging
import re
import traceback
from typing import Optional

import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_MODEL, CATEGORIES

logger = logging.getLogger(__name__)

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY, transport="rest")

# Список категорий для промпта
_CATEGORY_LIST = "\n".join(
    f"- {slug}" for slug in CATEGORIES.values()
)

_SYSTEM_INSTRUCTION = f"""Определи категорию расхода. Ответь ОДНИМ СЛОВОМ — slug категории.

Доступные категории:
{_CATEGORY_LIST}

Если не можешь определить — ответь: other
Ответь ТОЛЬКО slug, без пояснений."""

# Создаём модель
model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    system_instruction=_SYSTEM_INSTRUCTION,
    generation_config={
        "temperature": 0.0,
        "max_output_tokens": 20,
    },
)

API_TIMEOUT = 10


# ── Regex-парсер (основной) ──────────────────────────────────────────────

def _parse_message(text: str) -> Optional[dict]:
    """Извлечь сумму и описание из сообщения через regex.

    Поддерживаемые форматы:
        бензин роснефть 300
        300 бензин роснефть
        кофе 350.50
        2500 аренда квартира
        такси 1 500
    """
    text = text.strip()
    if not text:
        return None

    # Паттерн числа: 300 | 1500 | 1 500 | 350.50 | 350,50
    num_pattern = r"(\d[\d\s]*[\d](?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?)"

    # Попытка 1: число в конце — "бензин роснефть 300"
    match = re.match(rf"^(.+?)\s+{num_pattern}\s*$", text)
    if match:
        description = match.group(1).strip()
        amount_str = match.group(2)
        amount = _parse_amount(amount_str)
        if amount and amount > 0 and description:
            return {"amount": amount, "description": _capitalize(description)}

    # Попытка 2: число в начале — "300 бензин роснефть"
    match = re.match(rf"^{num_pattern}\s+(.+)$", text)
    if match:
        amount_str = match.group(1)
        description = match.group(2).strip()
        amount = _parse_amount(amount_str)
        if amount and amount > 0 and description:
            return {"amount": amount, "description": _capitalize(description)}

    return None


def _parse_amount(s: str) -> Optional[float]:
    """Парсинг суммы: убрать пробелы, заменить запятую."""
    try:
        s = s.replace(" ", "").replace(",", ".")
        return float(s)
    except (ValueError, TypeError):
        return None


def _capitalize(s: str) -> str:
    """Первая буква заглавная, остальные без изменений."""
    return s[0].upper() + s[1:] if s else s


# ── AI-категоризатор ─────────────────────────────────────────────────────

async def _get_category_from_ai(description: str) -> str:
    """Спросить AI только категорию. Возвращает slug или 'other'."""
    try:
        response = await asyncio.wait_for(
            model.generate_content_async(
                description,
                safety_settings={
                    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
                },
            ),
            timeout=API_TIMEOUT,
        )

        # Проверяем блокировку
        if not response.candidates:
            logger.warning("AI: ответ заблокирован (нет candidates)")
            return "other"

        candidate = response.candidates[0]
        if candidate.finish_reason and candidate.finish_reason.name == "SAFETY":
            logger.warning("AI: ответ заблокирован (SAFETY)")
            return "other"

        raw = response.text.strip().lower()
        logger.info(f"AI категория: {raw!r}")

        # Проверяем что это валидный slug
        valid_slugs = set(CATEGORIES.values())
        if raw in valid_slugs:
            return raw

        # Может вернул с пробелами или лишними символами
        for slug in valid_slugs:
            if slug in raw:
                return slug

        return "other"

    except asyncio.TimeoutError:
        logger.warning(f"AI: таймаут {API_TIMEOUT}с")
        return "other"
    except Exception as e:
        logger.warning(f"AI: ошибка категоризации: {e}")
        return "other"


# ── Основная функция ─────────────────────────────────────────────────────

async def parse_expense(text: str) -> Optional[dict]:
    """Распарсить сообщение пользователя и извлечь трату.

    1. Regex извлекает сумму и описание
    2. AI определяет категорию (с фоллбэком на «Прочее»)

    Returns:
        dict с ключами amount, description, category или None.
    """
    # Шаг 1: regex-парсинг (сумма + описание)
    parsed = _parse_message(text)
    if parsed is None:
        logger.info(f"Regex не распознал трату: {text!r}")
        return None

    logger.info(f"Regex: сумма={parsed['amount']}, описание={parsed['description']!r}")

    # Шаг 2: AI определяет категорию
    category = await _get_category_from_ai(parsed["description"])

    return {
        "amount": parsed["amount"],
        "description": parsed["description"],
        "category": category,
    }


# ── Распознавание фото (Vision) ─────────────────────────────────────────

_VISION_CATEGORIES = "\n".join(
    f"- {slug}" for slug in CATEGORIES.values()
)

_VISION_PROMPT = f"""Проанализируй изображение. Это чек, скриншот перевода или фото траты.

Извлеки ВСЕ траты из изображения. Для каждой траты определи:
- amount: сумма (число)
- description: краткое описание на русском
- category: одна из категорий ({_VISION_CATEGORIES})

Ответь JSON-массивом:
[{{"amount": 350, "description": "Кофе латте", "category": "food"}}]

Если на фото только итоговая сумма (например, банковский перевод), верни одну запись.
Если не можешь распознать траты — верни пустой массив: []

ТОЛЬКО JSON. Без markdown, без пояснений."""

# Модель для анализа изображений
vision_model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    generation_config={
        "temperature": 0.1,
        "max_output_tokens": 1024,
    },
)


def _extract_json_array(text: str) -> Optional[list]:
    """Извлечь JSON-массив из ответа модели."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    text = text.strip()

    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
    except json.JSONDecodeError:
        pass

    # Фоллбек: ищем массив
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            return data if isinstance(data, list) else [data]
        except json.JSONDecodeError:
            pass

    # Фоллбек: ищем объект
    match = re.search(r"\{[^{}]*\}", text)
    if match:
        try:
            return [json.loads(match.group())]
        except json.JSONDecodeError:
            pass

    return None


async def parse_expense_from_image(image_bytes: bytes) -> Optional[list[dict]]:
    """Распознать траты из фото (чек, перевод, скриншот).

    Returns:
        Список dict с ключами amount, description, category или None.
    """
    try:
        image_part = {
            "mime_type": "image/jpeg",
            "data": image_bytes,
        }

        response = await asyncio.wait_for(
            vision_model.generate_content_async(
                [_VISION_PROMPT, image_part],
                safety_settings={
                    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
                },
            ),
            timeout=20,
        )

        if not response.candidates:
            logger.warning("Vision: ответ заблокирован")
            return None

        candidate = response.candidates[0]
        if candidate.finish_reason and candidate.finish_reason.name == "SAFETY":
            logger.warning("Vision: заблокирован (SAFETY)")
            return None

        raw = response.text
        logger.info(f"Vision ответ: {raw!r}")

        items = _extract_json_array(raw)
        if not items:
            logger.warning("Vision: не удалось извлечь JSON")
            return None

        valid_slugs = set(CATEGORIES.values())
        results = []

        for item in items:
            try:
                amount = float(item.get("amount", 0))
                if amount <= 0:
                    continue

                category = item.get("category", "other")
                if category not in valid_slugs:
                    category = "other"

                results.append({
                    "amount": amount,
                    "description": item.get("description", "Покупка"),
                    "category": category,
                })
            except (ValueError, TypeError, KeyError):
                continue

        return results if results else None

    except asyncio.TimeoutError:
        logger.error("Vision: таймаут 20с")
        return None
    except Exception as e:
        logger.error(f"Vision ошибка: {e}\n{traceback.format_exc()}")
        return None


# ── Режим чата ───────────────────────────────────────────────────────────

_CHAT_INSTRUCTION = """Ты — дружелюбный и умный AI-ассистент. Отвечай на русском языке.
Будь полезным, кратким и по делу. Используй эмодзи для выразительности.
Ты встроен в Telegram-бота для учёта расходов, но в режиме чата ты — универсальный помощник.

ВАЖНО: Твой ответ ВСЕГДА должен состоять из двух частей, разделённых строкой "FINAL_ANSWER:".
Всё, что до "FINAL_ANSWER:" — это твои размышления, черновики и планирование.
Всё, что после "FINAL_ANSWER:" — это финальный красивый ответ, который увидит пользователь."""

chat_model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    system_instruction=_CHAT_INSTRUCTION,
    generation_config={
        "temperature": 0.8,
        "max_output_tokens": 2048,
    },
)

# История чатов: {user_id: [{"role": ..., "parts": ...}, ...]}
_chat_histories: dict[int, list[dict]] = {}
MAX_HISTORY = 20  # макс. сообщений в контексте


def clear_chat_history(user_id: int) -> None:
    """Очистить историю чата пользователя."""
    _chat_histories.pop(user_id, None)


async def chat_reply(user_id: int, text: str) -> str:
    """Отправить сообщение в режиме чата и получить ответ.

    Поддерживает историю диалога (до MAX_HISTORY сообщений).
    """
    # Получаем или создаём историю
    history = _chat_histories.setdefault(user_id, [])

    # Добавляем сообщение пользователя
    history.append({"role": "user", "parts": [{"text": text}]})

    # Обрезаем историю если слишком длинная
    if len(history) > MAX_HISTORY:
        history[:] = history[-MAX_HISTORY:]

    try:
        response = await asyncio.wait_for(
            chat_model.generate_content_async(
                contents=history,
                safety_settings={
                    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
                },
            ),
            timeout=45,
        )

        if not response.candidates:
            return "🤖 Не удалось получить ответ. Попробуй переформулировать."

        candidate = response.candidates[0]
        if candidate.finish_reason and candidate.finish_reason.name == "SAFETY":
            return "🤖 Не могу ответить на это. Попробуй другой вопрос."

        reply = response.text.strip()

        # Разделяем мысли и ответ по маркеру
        if "FINAL_ANSWER:" in reply:
            reply = reply.split("FINAL_ANSWER:")[-1].strip()
        else:
            # Если модель всё же забыла маркер, применяем жёсткий фоллбэк:
            # удаляем все строки до первой пустой строки, если они похожи на "мысли"
            lines = reply.split('\n')
            cleaned = []
            in_thought = True
            for line in lines:
                stripped = line.strip()
                if in_thought and (stripped == "" or stripped.startswith("*") or stripped.startswith("The user said") or stripped.startswith("Friendly, smart AI") or stripped.startswith("Universal assistant")):
                    continue
                if in_thought and not stripped.startswith("*") and not stripped == "":
                    # Возможно это начало нормального ответа
                    in_thought = False
                cleaned.append(line)
            
            if cleaned:
                reply = '\n'.join(cleaned).strip()

        # Добавляем ответ в историю
        history.append({"role": "model", "parts": [{"text": reply}]})

        return reply

    except asyncio.TimeoutError:
        logger.error("Chat: таймаут")
        return "⏱ Таймаут. Попробуй ещё раз."
    except Exception as e:
        logger.error(f"Chat ошибка: {e}\n{traceback.format_exc()}")
        return "❌ Произошла ошибка. Попробуй ещё раз."
