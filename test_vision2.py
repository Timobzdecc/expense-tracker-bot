import asyncio
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
vision_model = genai.GenerativeModel(model_name="gemini-2.0-flash", generation_config={"temperature": 0.1})

_VISION_PROMPT = """Проанализируй изображение. Это чек.
Извлеки ВСЕ траты из изображения. Для каждой траты определи:
- amount: сумма (число)
- description: краткое описание на русском
- category: одна из категорий

Ответь JSON-массивом:
[{"amount": 350, "description": "Кофе латте", "category": "food"}]
"""

async def test():
    with open(r"C:\Users\www-r\Downloads\photo_2026-06-27_10-33-35.jpg", "rb") as f:
        image_bytes = f.read()

    print("Sending to Gemini...")
    try:
        response = await vision_model.generate_content_async(
            [_VISION_PROMPT, {"mime_type": "image/jpeg", "data": image_bytes}],
            safety_settings={
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            },
        )
        print("Candidates:", response.candidates)
        print("Text:", response.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
