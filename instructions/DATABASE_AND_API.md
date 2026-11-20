# Database, API, and AI Prompts

## Database (Supabase PostgreSQL)

### `profiles`
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | same as `auth.users.id` |
| username | text, unique | lowercase, used to find friends |
| display_name | text | |
| preferred_language | text | language code, e.g. `en`, `ur` |
| created_at | timestamptz | default now() |

### `friendships`
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| requester_id | uuid, FK profiles | |
| addressee_id | uuid, FK profiles | |
| status | text | `pending`, `accepted`, `rejected` |
| created_at | timestamptz | |

Unique pair: one row per two users.

### `messages`
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| sender_id | uuid, FK profiles | |
| receiver_id | uuid, FK profiles | |
| type | text | `text`, `image`, `voice` |
| content | text | text body, null for image/voice |
| media_url | text | storage path for image/voice |
| duration_seconds | int | voice only, max 60 |
| created_at | timestamptz | |

### `translations`
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| message_id | uuid, FK messages | on delete cascade |
| target_language | text | |
| detected_language | text | |
| transcript | text | voice only, original speech text |
| translated_text | text | |
| created_at | timestamptz | |

**Unique (message_id, target_language)**. This is the caching rule.

### Storage buckets
- `chat-images` (max 1 MB per file)
- `chat-voice` (max 60 s audio)
Both private. Only the two users in the chat can read a file.

### Row Level Security (turn on for every table)
- `profiles`: any logged-in user can read (needed for username search); only the owner can update their own row.
- `friendships`: users can read rows where they are requester or addressee; only the requester can insert; only the addressee can update status.
- `messages`: users can read rows where they are sender or receiver; insert only if `sender_id = auth.uid()` AND the two users are accepted friends.
- `translations`: users can read translations of messages they are part of; inserts happen from the backend (service key).
- Storage: access only for the sender and receiver of the related message.

Ask before changing this schema once it is created.

## Backend API (FastAPI)

All routes except `/health` need header `Authorization: Bearer <supabase access token>`.

### `GET /health`
Returns `{"status": "ok"}`.

### `POST /translate/text`
Request:
```json
{ "message_id": "uuid", "text": "mera naam Ali hai", "target_language": "en" }
```
Response:
```json
{ "detected_language": "ur-roman", "translated_text": "My name is Ali" }
```

### `POST /translate/voice`
Request:
```json
{ "message_id": "uuid", "audio_path": "chat-voice/abc.m4a", "target_language": "en" }
```
Response:
```json
{ "transcript": "...", "detected_language": "ur", "translated_text": "..." }
```

### Behavior for both routes
1. Verify the token. Invalid gives 401.
2. Check the user is part of the message. Otherwise 403.
3. Rate limit per user. Over the limit gives 429.
4. Check `translations` cache first and return it if found.
5. Call the AI, parse JSON, save to `translations`, return.
6. On any AI error return 502 with a short message. The app falls back to the original text.

Voice notes longer than 60 seconds are rejected with 400.

## AI prompts

### Text translation (Groq, `openai/gpt-oss-120b`)
System prompt:
```
You are a translation engine for a chat app.
Detect the language of the user's message, then translate it into the target language.
The message may be in Roman Urdu (Urdu written with English letters). Treat it as Urdu, label it "ur-roman".
Keep the tone, emojis, names, and slang. Do not add explanations.
If the message is already in the target language, return it unchanged.
Reply with JSON only, in this exact shape:
{"detected_language": "<code>", "translated_text": "<text>"}
```
User message:
```
Target language: {target_language}
Message: {text}
```

Roman Urdu examples to include in the prompt:
- "mera naam Ali hai" -> "My name is Ali"
- "tum kal kahan the?" -> "Where were you yesterday?"
- "main theek hoon, shukriya" -> "I am fine, thank you"

### Voice (Gemini, `gemini-3.1-flash-lite`)
Send the audio file plus this instruction in ONE request:
```
Listen to this voice message.
1. Transcribe exactly what was said.
2. Detect the spoken language (Roman Urdu speech counts as Urdu).
3. Translate the transcript into {target_language}.
Reply with JSON only, in this exact shape:
{"transcript": "<text>", "detected_language": "<code>", "translated_text": "<text>"}
```

### JSON handling
- Ask for JSON only, but still strip any code fences before parsing.
- If parsing fails, treat it as an AI failure (fallback to original).
