import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_supabase: Optional[Client] = None

def get_supabase_client() -> Client:
    global _supabase
    if _supabase is None:
        url = os.getenv("SUPABASE_URL", "")
        service_key = os.getenv("SUPABASE_SERVICE_KEY", "")
        if not url or not service_key:
            raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_KEY is not configured in backend environment.")
        _supabase = create_client(url, service_key)
    return _supabase

def is_user_in_message(message_id: str, user_id: str) -> bool:
    """
    Verifies that the requesting user is either the sender or receiver of the message.
    If the message does not exist yet (e.g. standalone API testing), allows translation.
    """
    try:
        client = get_supabase_client()
        res = client.from_("messages").select("sender_id, receiver_id").eq("id", message_id).maybe_single().execute()
        if not res or not res.data:
            return True
        data = res.data
        return data.get("sender_id") == user_id or data.get("receiver_id") == user_id
    except Exception:
        return True

def get_message_duration(message_id: str) -> Optional[int]:
    """Returns the recorded duration in seconds for a voice message."""
    try:
        client = get_supabase_client()
        res = client.from_("messages").select("duration_seconds").eq("id", message_id).maybe_single().execute()
        if res and res.data:
            return res.data.get("duration_seconds")
        return None
    except Exception:
        return None

def download_voice_file(file_path: str) -> bytes:
    """Downloads audio file bytes from the chat-voice private storage bucket."""
    client = get_supabase_client()
    path = file_path
    if path.startswith("chat-voice/"):
        path = path.replace("chat-voice/", "", 1)
    elif path.startswith("/chat-voice/"):
        path = path.replace("/chat-voice/", "", 1)

    return client.storage.from_("chat-voice").download(path)

def get_cached_translation(message_id: str, target_language: str) -> Optional[Dict[str, Any]]:
    """Checks the translations table for an existing translation."""
    try:
        client = get_supabase_client()
        res = client.from_("translations")\
            .select("detected_language, translated_text, transcript")\
            .eq("message_id", message_id)\
            .eq("target_language", target_language)\
            .maybe_single()\
            .execute()
        if res and res.data:
            return res.data
        return None
    except Exception:
        return None

def save_translation(
    message_id: str,
    target_language: str,
    detected_language: str,
    translated_text: str,
    transcript: Optional[str] = None
) -> None:
    """Saves translation to the translations table."""
    try:
        client = get_supabase_client()
        payload = {
            "message_id": message_id,
            "target_language": target_language,
            "detected_language": detected_language,
            "translated_text": translated_text,
        }
        if transcript:
            payload["transcript"] = transcript

        client.from_("translations").upsert(
            payload,
            on_conflict="message_id,target_language"
        ).execute()
    except Exception as e:
        print(f"Failed to cache translation: {e}")
