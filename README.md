# 🌐 AI Multilingual Messenger

A real-time, cross-platform 1-on-1 messaging application with automated non-blocking text and voice translation (including Roman Urdu support), built with **Flutter 3**, **FastAPI**, **Supabase**, **Groq Cloud AI**, and **Google Gemini 3.1 Flash-Lite**.

---

## 👥 Project Team & Group Members

| # | Name | Roll Number | Major Role |
|---|---|---|---|
| 1 | **Rao Hamza Tariq** | `CSC-24F-042` | Full-Stack Lead (Architecture, FastAPI, Gemini Voice, CI/CD) |
| 2 | **Imtiaz Maqbool** | `SCS-24F-003` | Frontend Lead (Real-Time Chat, Bubbles, Audio Codecs) |
| 3 | **Fahad Yaseen** | `CSC-25S-201` | UI/UX & Navigation (3-Tab Home Shell, Material 3 Themes) |
| 4 | **Muhammad Saad** | `CSC-24F-025` | Social Graph & Search (Friendships, In-Chat Search, Media Viewer) |
| 5 | **Shahmeer Baqai** | `CSC-24F-027` | Notification & Status Systems (Notification Banner, Delivery/Seen Ticks) |

**Course / Project**: Mobile Application Development & Applied AI Capstone Project  
**Date**: November 2026 — *Completed, Verified & Demo-Ready*

---

## 🚀 Key Features

### 1. Real-Time Multilingual Chat
- **1-on-1 Realtime Messaging**: Sub-second message delivery powered by Supabase PostgreSQL WebSocket channels.
- **Automated AI Text Translation**: Foreign language text is automatically translated into the recipient's preferred language via Groq Cloud (`openai/gpt-oss-120b`).
- **Roman Urdu & Dialect Support**: Detects and translates colloquial Roman Urdu into English and other target languages.
- **"Show Original" Transparency**: Tapping a toggle switch lets recipients view the sender's verbatim text or return to the translated version.
- **Non-Blocking Delivery**: Translation failures never block message delivery — messages always deliver in their original text.

### 2. Multimodal AI Voice Notes
- **Platform-Adaptive Recording**: Web Opus (`.webm`) on browsers and Mobile AAC (`.m4a`) on Android/iOS.
- **60-Second Cap**: Live recording counter with an automatic stop-and-send cap at 60 seconds.
- **Gemini Flash-Lite Translation**: Audio files are transcribed and translated in one inference pass using Google's `gemini-3.1-flash-lite`.
- **In-Bubble Player & Transcript**: Voice notes render interactive audio play/pause controls, duration counters, and a verbatim/translated transcript toggle.

### 3. Rich Media Sharing & In-Chat Search
- **Client-Side Image Validation**: Strict $\le 1\text{ MB}$ file size enforcement before upload to private Supabase storage.
- **Interactive Full-Screen ImageViewer**: Tap any photo attachment to pan and pinch-to-zoom.
- **In-Chat Message Search**: Search messages within any chat thread across text, translations, voice transcripts, and photos, with auto-scroll jumping directly to the match.

### 4. In-App Notifications & Seen Status Indicators
- **In-App Top Notification Banner**: An animated slide-down overlay alerts users when incoming messages arrive from other chats with 1-tap navigation.
- **Real-Time Delivery & Seen Ticks**:
  - `✓✓` *(Subtle Gray)*: Message delivered to the recipient, but **unseen**.
  - `✓✓` *(Bright Cyan-Blue)*: Recipient has opened the chat and **seen** the message.

### 5. Social Graph & Material 3 Theming
- **Username Search (`@username`)**: Search and connect with friends; manage incoming and outgoing requests.
- **3-Tab Home Navigation**: Clean Material 3 `NavigationBar` hosting **Chats**, **Friends**, and **Profile**.
- **Light & Dark Mode**: Consistent Material 3 theming (Teal `#007A87` primary) with persistent user preference.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flutter Presentation Layer                │
│    (Web & Mobile, Material Design 3, Provider State Mgt)   │
└──────────────┬───────────────────────────────┬──────────────┘
               │ 1. Upload Media / Insert Msg  │ 3. Fetch / Sync Realtime
               ▼                               ▼
┌───────────────────────────────┐ ┌───────────────────────────┐
│       FastAPI Gateway         │ │     Supabase Cloud        │
│ • JWT Validation              │ │ • Auth (GoTrue)           │
│ • Rate Limiting               │ │ • Postgres 15 + RLS       │
│ • Duration / Size validation  │ │ • Realtime Channels (WAL) │
└───────┬───────────────┬───────┘ │ • Storage Buckets         │
        │               │         └─────────────▲─────────────┘
        │ (Text)        │ (Audio)               │ Cache
        ▼               ▼                       │ Translations
┌──────────────┐ ┌──────────────┐               │
│  Groq Cloud  │ │Google Gemini │───────────────┘
│  (LLaMA/GPT) │ │ (Flash-Lite) │
└──────────────┘ └──────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | Flutter 3 (Dart 3) | Material 3, Provider (`ChangeNotifier`), cross-platform (Android, Web) |
| **Backend API** | FastAPI (Python 3.12) | Asynchronous ASGI server, Uvicorn, HTTPX client |
| **Database & Auth** | Supabase (PostgreSQL 15) | Row-Level Security (RLS), GoTrue Auth, Realtime WebSocket replication |
| **Cloud Storage** | Supabase Storage | Private buckets: `chat-images` (max 1 MB) & `chat-voice` (max 60s) |
| **AI Translation (Text)** | Groq Cloud API | `openai/gpt-oss-120b` (sub-second multilingual inference) |
| **AI Translation (Voice)** | Google Gemini API | `gemini-3.1-flash-lite` (multimodal audio transcription & translation) |
| **CI / CD** | GitHub Actions | Automated Android Release APK builder workflow (`.github/workflows/build_apk.yml`) |

---

## 📁 Project Directory Structure

```
ai_multilingual_messenger/
├── .github/workflows/
│   └── build_apk.yml              # On-demand Android APK builder workflow
├── backend/
│   ├── .env.example               # Backend environment variables template
│   ├── Procfile                   # Cloud deployment entrypoint (Render/Railway)
│   ├── auth.py                    # Supabase JWT token verification
│   ├── main.py                    # FastAPI endpoints (/health, /translate/text, /translate/voice)
│   ├── rate_limit.py              # In-memory per-user rate limiting
│   ├── requirements.txt           # Python dependencies
│   ├── supabase_client.py         # Supabase client, storage downloader & translation caching
│   ├── translate_text.py          # Groq text translation service
│   └── translate_voice.py         # Gemini multimodal voice translation service
├── lib/
│   ├── core/                      # Constants, AppConfig, and Material 3 theme definitions
│   ├── models/                    # Profile, Friendship, Message, and Translation data models
│   ├── providers/                 # AuthProvider, FriendsProvider, ChatProvider, ThemeProvider
│   ├── screens/                   # Login, Signup, Onboarding, Home, Chat, Search, Profile screens
│   ├── services/                  # SupabaseService, TranslationService, AudioService
│   ├── widgets/                   # MessageBubble, VoiceMessageBubble, ChatInputBar, NotificationBanner
│   └── main.dart                  # Application entry point
├── AI_Multilingual_Messenger_Final_Report.docx # Complete final project report
├── pubspec.yaml                   # Flutter dependencies
└── README.md                      # Project documentation
```

---

## ⚙️ Setup & Running Locally

### Prerequisites
- [Flutter SDK](https://flutter.dev/docs/get-started/install) (3.24+ recommended)
- [Python 3.12](https://www.python.org/downloads/)
- A free [Supabase](https://supabase.com) account
- A free [Groq Cloud](https://console.groq.com) API key
- A free [Google AI Studio (Gemini)](https://aistudio.google.com) API key

---

### 1. Database Setup (Supabase)
1. Create a new Supabase project.
2. In the **SQL Editor**, run the schema and RLS policies from `database/schema.sql` (or `supabase_schema.sql`).
3. Create two private storage buckets:
   - `chat-images` (Max size: 1 MB, allowed MIME types: `image/jpeg`, `image/png`, `image/webp`)
   - `chat-voice` (Max size: 5 MB, allowed MIME types: `audio/webm`, `audio/mp4`, `audio/aac`, `audio/m4a`)

---

### 2. Backend Setup (FastAPI)
1. Open a terminal in `backend/`:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate      # On Windows: .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. Create `backend/.env` with your real keys (copy from `.env.example`):
   ```env
   GROQ_API_KEY=your_groq_api_key
   GEMINI_API_KEY=your_gemini_api_key
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=your_supabase_service_role_key
   SUPABASE_JWT_SECRET=your_supabase_jwt_secret
   ```
3. Start the backend:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   Verify at `http://localhost:8000/health` (returns `{"status": "ok"}`).

---

### 3. Frontend Setup (Flutter)
1. Install dependencies:
   ```bash
   flutter pub get
   ```
2. Verify code health:
   ```bash
   flutter analyze
   ```
3. Run on Chrome Web:
   ```bash
   flutter run -d chrome --web-port 5000
   ```
4. Run on an Android device or emulator:
   ```bash
   flutter run
   ```

---

## 📱 Building the Android APK (CI/CD)

A GitHub Actions workflow is provided at `.github/workflows/build_apk.yml`:
1. Push this repository to GitHub.
2. Go to the **Actions** tab on your GitHub repo.
3. Select **"Build Android APK"** from the left sidebar.
4. Click **"Run workflow"** ▾.
5. Once the run finishes, download `app-release.apk` directly from the **Artifacts** section!

---

## 📄 License & Academic Attribution
This project was designed and built as a Capstone Academic Project in **Mobile Application Development & Applied Artificial Intelligence**. All rights reserved by the project team.
