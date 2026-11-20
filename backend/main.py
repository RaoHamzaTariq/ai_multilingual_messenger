import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

from auth import verify_jwt_token
from rate_limit import rate_limiter
from supabase_client import (
    is_user_in_message,
    get_cached_translation,
    save_translation,
    get_message_duration,
    download_voice_file,
)
from translate_text import call_groq_translation
from translate_voice import call_gemini_voice_translation

app = FastAPI(
    title="AI Multilingual Messenger Translation API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

# Enable CORS for Flutter web / mobile clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextTranslationRequest(BaseModel):
    message_id: str = Field(..., description="UUID of the message")
    text: str = Field(..., description="Message text content")
    target_language: str = Field(..., description="Target language code, e.g. en, ur")

class TextTranslationResponse(BaseModel):
    detected_language: str
    translated_text: str

class VoiceTranslationRequest(BaseModel):
    message_id: str = Field(..., description="UUID of the message")
    audio_path: str = Field(..., description="Storage path of audio in chat-voice bucket")
    target_language: str = Field(..., description="Target language code, e.g. en, ur")

class VoiceTranslationResponse(BaseModel):
    transcript: str
    detected_language: str
    translated_text: str

@app.get("/", summary="welcome endpoint")
def welcome():
    return {"Welcome to AI Multilingual Messenger API"}

@app.get("/health", summary="Health check endpoint")
def health_check():
    return {"status": "ok"}

@app.post(
    "/translate/text",
    response_model=TextTranslationResponse,
    summary="Translate text message"
)
async def translate_text(
    payload: TextTranslationRequest,
    user_id: str = Depends(verify_jwt_token)
):
    # 1. Verify user rate limit (30 requests/minute)
    if not rate_limiter.is_allowed(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a moment before requesting more translations."
        )

    # 2. Check user is sender or receiver of the message (if Supabase configured)
    if os.getenv("SUPABASE_SERVICE_KEY"):
        if not is_user_in_message(payload.message_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: You are not a participant in this message conversation."
            )

    # 3. Check translation cache
    cached = get_cached_translation(payload.message_id, payload.target_language)
    if cached:
        return TextTranslationResponse(
            detected_language=cached.get("detected_language", "unknown"),
            translated_text=cached.get("translated_text", payload.text)
        )

    # 4. Call Groq translation
    try:
        result = await call_groq_translation(
            text=payload.text,
            target_language=payload.target_language
        )
    except Exception as e:
        # Per requirements: On AI error return 502 with short message
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Translation AI service error: {str(e)}"
        )

    # 5. Save to translations table for caching
    save_translation(
        message_id=payload.message_id,
        target_language=payload.target_language,
        detected_language=result["detected_language"],
        translated_text=result["translated_text"]
    )

    return TextTranslationResponse(
        detected_language=result["detected_language"],
        translated_text=result["translated_text"]
    )

@app.post(
    "/translate/voice",
    response_model=VoiceTranslationResponse,
    summary="Transcribe, detect language, and translate voice message using Gemini in one request"
)
async def translate_voice(
    payload: VoiceTranslationRequest,
    user_id: str = Depends(verify_jwt_token)
):
    # 1. Verify user rate limit
    if not rate_limiter.is_allowed(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a moment before requesting more translations."
        )

    # 2. Check user is sender or receiver of the message
    if os.getenv("SUPABASE_SERVICE_KEY"):
        if not is_user_in_message(payload.message_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: You are not a participant in this message conversation."
            )

    # 3. Reject voice notes longer than 60 seconds (HTTP 400 per DATABASE_AND_API.md)
    duration = get_message_duration(payload.message_id)
    if duration is not None and duration > 60:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voice notes longer than 60 seconds are rejected."
        )

    # 4. Check translations cache first
    cached = get_cached_translation(payload.message_id, payload.target_language)
    if cached and cached.get("transcript"):
        return VoiceTranslationResponse(
            transcript=cached.get("transcript", ""),
            detected_language=cached.get("detected_language", "unknown"),
            translated_text=cached.get("translated_text", "")
        )

    # 5. Download audio bytes from Supabase Storage 'chat-voice'
    try:
        audio_bytes = download_voice_file(payload.audio_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file could not be downloaded from storage: {str(e)}"
        )

    # Determine MIME type from file extension
    path_lower = payload.audio_path.lower()
    if path_lower.endswith(".webm"):
        mime_type = "audio/webm"
    elif path_lower.endswith(".m4a") or path_lower.endswith(".mp4"):
        mime_type = "audio/mp4"
    elif path_lower.endswith(".aac"):
        mime_type = "audio/aac"
    elif path_lower.endswith(".wav"):
        mime_type = "audio/wav"
    elif path_lower.endswith(".ogg"):
        mime_type = "audio/ogg"
    else:
        mime_type = "audio/mp4"

    # 6. Call Gemini voice translation (transcribe + detect + translate in ONE prompt request)
    try:
        result = await call_gemini_voice_translation(
            audio_bytes=audio_bytes,
            mime_type=mime_type,
            target_language=payload.target_language
        )
    except Exception as e:
        # Per requirements: On AI error return 502 with short message
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Voice translation AI service error: {str(e)}"
        )

    # 7. Save to translations table for caching
    save_translation(
        message_id=payload.message_id,
        target_language=payload.target_language,
        detected_language=result["detected_language"],
        translated_text=result["translated_text"],
        transcript=result["transcript"]
    )

    return VoiceTranslationResponse(
        transcript=result["transcript"],
        detected_language=result["detected_language"],
        translated_text=result["translated_text"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
