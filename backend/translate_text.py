import os
import json
import re
import httpx
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are a translation engine for a chat app.
Detect the language of the user's message, then translate it into the target language.
The message may be in Roman Urdu (Urdu written with English letters). Treat it as Urdu, label it "ur-roman".
Keep the tone, emojis, names, and slang. Do not add explanations.
If the message is already in the target language, return it unchanged.

Roman Urdu translation examples:
- "mera naam Ali hai" -> "My name is Ali"
- "tum kal kahan the?" -> "Where were you yesterday?"
- "main theek hoon, shukriya" -> "I am fine, thank you"

Reply with JSON only, in this exact shape:
{"detected_language": "<code>", "translated_text": "<text>"}"""

def _clean_json_response(raw_text: str) -> str:
    """Strips markdown code fences (```json ... ```) or extra whitespace."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()

async def call_groq_translation(text: str, target_language: str) -> Dict[str, str]:
    """
    Calls the Groq API to translate text into target_language.
    Returns dict: {'detected_language': '...', 'translated_text': '...'}
    """
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable is not set")

    # If message is empty or only whitespace/emojis
    stripped = text.strip()
    if not stripped:
        return {"detected_language": target_language, "translated_text": text}

    user_prompt = f"Target language: {target_language}\nMessage: {text}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    choices = data.get("choices", [])
    if not choices:
        raise ValueError("Empty completion returned from Groq API")

    content = choices[0].get("message", {}).get("content", "")
    cleaned = _clean_json_response(content)

    parsed = json.loads(cleaned)
    detected_language = parsed.get("detected_language", "unknown")
    translated_text = parsed.get("translated_text", text)

    return {
        "detected_language": detected_language,
        "translated_text": translated_text,
    }
