# Tech Stack and Architecture

## Tech stack

| Part | Technology |
|---|---|
| Mobile app | Flutter + Dart |
| State management | Provider (plain, nothing fancier) |
| Auth, DB, realtime, storage | Supabase (Auth, PostgreSQL, Realtime, Storage, Row Level Security) |
| Backend | FastAPI (Python) deployed on Vercel |
| Text translation | Groq API, model `openai/gpt-oss-120b` |
| Voice transcribe + detect + translate | Gemini API, model `gemini-3.1-flash-lite` |
| Version control | Git + GitHub |

Use the model names exactly as written above. Before coding the AI calls, check each provider's current docs for the exact request format.

## Architecture

```
Flutter app
  |-- Supabase Auth / DB / Realtime / Storage   (direct, protected by RLS)
  |-- FastAPI backend (Vercel)                  (only for translation)
          |-- verifies Supabase JWT
          |-- rate limits per user
          |-- Groq API   (text)
          |-- Gemini API (voice)
          |-- saves result in Supabase `translations` table
```

Rules:
- The app talks to Supabase directly for login, chats, and files.
- The app talks to the backend ONLY for translation.
- AI keys exist only as backend environment variables. Never put them in Flutter code.

## Message flow (text)
1. Sender app inserts a row into `messages`. Delivery does not wait for translation.
2. Receiver app gets the new message through Supabase Realtime.
3. Receiver app checks `translations` for (message_id, receiver's language).
4. If found, show it. If not, call `POST /translate/text` on the backend.
5. Backend verifies the token, applies rate limit, calls Groq, saves the result, returns JSON.
6. App shows the translated text. If anything fails, app shows the original.

## Message flow (voice)
1. Sender records up to 60 s, uploads audio to Supabase Storage, inserts a `messages` row of type `voice`.
2. Receiver app calls `POST /translate/voice` with the message id and target language.
3. Backend downloads the audio, sends it to Gemini in ONE request (transcribe + detect + translate), saves the result, returns JSON.
4. App shows the translated transcript under the voice player. Failure means just the player is shown.

## Flutter folder structure

```
lib/
  main.dart
  app.dart                  # MaterialApp, theme, routes
  core/
    constants.dart          # supported languages, limits (1 MB, 60 s)
    theme.dart              # light and dark themes
  models/
    profile.dart
    friendship.dart
    message.dart
    translation.dart
  providers/
    auth_provider.dart
    friends_provider.dart
    chat_provider.dart
    theme_provider.dart
  services/
    supabase_service.dart   # DB, realtime, storage calls
    translation_service.dart# calls our FastAPI backend
    audio_service.dart      # record and play voice notes
  screens/
    splash_screen.dart
    login_screen.dart
    signup_screen.dart
    onboarding_screen.dart  # pick preferred language
    home_screen.dart        # chats list + friends tabs
    friends_screen.dart
    chat_screen.dart
    search_screen.dart
    profile_screen.dart
  widgets/
    message_bubble.dart
    voice_message_bubble.dart
    chat_input_bar.dart
    language_picker.dart
    notification_banner.dart
```

## Backend folder structure

```
backend/
  main.py                   # FastAPI app and routes
  auth.py                   # verify Supabase JWT
  rate_limit.py             # simple per-user limit
  translate_text.py         # Groq call
  translate_voice.py        # Gemini call
  supabase_client.py        # save/read translations
  requirements.txt
  vercel.json
  .env.example              # names only, no real keys
```

## Environment variables (backend only)
`GROQ_API_KEY`, `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_JWT_SECRET`

Flutter app only gets `SUPABASE_URL` and the Supabase anon key, plus the backend URL.
