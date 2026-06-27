import asyncio
import google.generativeai as genai
import os
from dotenv import load_dotenv
from ai_categorizer import _VISION_PROMPT, _extract_json_array

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

genai.configure(api_key=GEMINI_API_KEY)

vision_model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    generation_config={
        "temperature": 0.1,
        "max_output_tokens": 1024,
    },
)

async def test():
    with open(r"C:\Users\www-r\Downloads\photo_2026-06-27_10-33-35.jpg", "rb") as f:
        image_bytes = f.read()

    image_part = {
        "mime_type": "image/jpeg",
        "data": image_bytes,
    }

    print("Sending to Gemini...")
    try:
        response = await vision_model.generate_content_async(
            [_VISION_PROMPT, image_part],
            safety_settings={
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            },
        )
        print("Candidates:", response.candidates)
        if response.candidates:
            print("Finish reason:", response.candidates[0].finish_reason)
        print("Text:", response.text)
        
        parsed = _extract_json_array(response.text)
        print("Parsed JSON:", parsed)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
