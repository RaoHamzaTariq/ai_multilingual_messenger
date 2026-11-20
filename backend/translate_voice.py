import os
import json
import base64
import httpx
from dotenv import load_dotenv

load_dotenv()

async def call_gemini_voice_translation(
    audio_bytes: bytes,
    mime_type: str,
    target_language: str
) -> dict:
    """
    Transcribes audio, detects spoken language (including Roman Urdu as Urdu),
    and translates into target_language using Gemini model gemini-3.1-flash-lite in ONE prompt.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY is not configured in backend environment.")

    encoded_audio = base64.b64encode(audio_bytes).decode("utf-8")

    # Prompt specified in DATABASE_AND_API.md
    prompt = (
        f"Listen to this voice message.\n"
        f"1. Transcribe exactly what was said.\n"
        f"2. Detect the spoken language (Roman Urdu speech counts as Urdu).\n"
        f"3. Translate the transcript into {target_language}.\n"
        f"Reply with JSON only, in this exact shape:\n"
        f'{{"transcript": "<text>", "detected_language": "<code>", "translated_text": "<text>"}}'
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={gemini_key}"

    # Normalize MIME type
    clean_mime = mime_type.lower()
    if "webm" in clean_mime:
        clean_mime = "audio/webm"
    elif "m4a" in clean_mime or "mp4" in clean_mime:
        clean_mime = "audio/mp4"
    elif "aac" in clean_mime:
        clean_mime = "audio/aac"
    elif "wav" in clean_mime:
        clean_mime = "audio/wav"
    elif "ogg" in clean_mime:
        clean_mime = "audio/ogg"
    else:
        clean_mime = "audio/mp4"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": clean_mime,
                            "data": encoded_audio
                        }
                    },
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.2
        }
    }

    async with httpx.AsyncClient(timeout=35.0) as client:
        response = await client.post(url, json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Gemini API returned status {response.status_code}: {response.text}")

    data = response.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"No response candidate from Gemini: {data}")

    raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()

    # Strip any markdown code fences before parsing
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    elif raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    raw_text = raw_text.strip()

    result = json.loads(raw_text)
    return {
        "transcript": result.get("transcript", ""),
        "detected_language": result.get("detected_language", "unknown"),
        "translated_text": result.get("translated_text", "")
    }
