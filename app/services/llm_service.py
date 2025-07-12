# app/services/llm_service.py

from openai import OpenAI
from app.config import OPENAI_API_KEY

# ✅ Create OpenAI client using the NEW SDK format
client = OpenAI(api_key=OPENAI_API_KEY)

def get_gpt_response(message: str) -> str:
    try:
        # ✅ NEW chat.completions.create method
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"
