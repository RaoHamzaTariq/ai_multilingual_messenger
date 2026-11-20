# Phases and Rules for Antigravity

## Read this first
Before writing any code, read all the other `.md` files in this folder:
`PROJECT_OVERVIEW.md`, `TECH_AND_ARCHITECTURE.md`, `DATABASE_AND_API.md`, `UI_DESIGN.md`.

## Agent rules
1. Build **one phase at a time**. Only work on the phase I tell you is current.
2. At the start of each phase, list the tasks you will do and wait for my "go".
3. After each task, tell me what files you created or changed and how to run or test it.
4. Do not add features outside the project scope (see "Not included" in `PROJECT_OVERVIEW.md`).
5. Do not change the database schema without asking me first.
6. Never put API keys in Flutter code or commit real keys. Use `.env.example` with names only.
7. Translation failure must never block message delivery.
8. Do not add packages unless really needed. Tell me which package and why.
9. If something in the docs is unclear or the AI provider's API differs from the docs, ask me instead of guessing.
10. Do not move on to the next phase until I confirm the current one works.

## Coding guidelines (human-like code)
- Write simple, readable code. Short functions, clear names.
- Use plain Provider with `ChangeNotifier`. No Riverpod, Bloc, GetIt, freezed, or code generation.
- No extra abstraction layers. No repository, use-case, or interface classes.
- Keep files small and follow the folder structure in `TECH_AND_ARCHITECTURE.md`.
- Comments only where the reason is not obvious. No comment on every line, no banner comments.
- Naming: `snake_case` files, `PascalCase` classes, `camelCase` variables.
- Prefer simple `if` and `try/catch` over clever one-liners.
- Handle errors with a SnackBar or a fallback, not silent failure.
- Hard-code nothing secret. Put limits (1 MB, 60 s, language list) in `constants.dart`.
- A few small `// TODO:` notes are fine.
- Same style in the backend: plain functions, type hints, no heavy frameworks beyond FastAPI.

---

## Phase 1: 12 Oct - 25 Oct 2026
Requirements, auth, profile, and translation backend.

- [ ] Create Flutter project and the folder structure
- [ ] Set up Supabase project (Auth, tables, RLS) from `DATABASE_AND_API.md`
- [ ] Create light and dark theme
- [ ] Splash screen with login-state check
- [ ] Sign up and login screens connected to Supabase Auth
- [ ] Onboarding screen: choose preferred language
- [ ] Profile screen: edit name, language, dark mode, logout
- [ ] FastAPI backend skeleton with `/health`
- [ ] JWT verification and per-user rate limit
- [ ] `POST /translate/text` working with Groq
- [ ] Deploy backend to Vercel and test with a real token

**Done when:** a user can sign up, pick a language, log in again after restart, and the deployed backend translates a test sentence (including Roman Urdu).

## Phase 2: 26 Oct - 8 Nov 2026
Friends, realtime chat, images, text translation, voice recording.

- [ ] Friends screen: send request by username, accept, reject
- [ ] Friends list on Home
- [ ] Chat screen UI with message bubbles
- [ ] Send and receive text in realtime (Supabase Realtime)
- [ ] Image sending with 1 MB limit (Supabase Storage)
- [ ] `translation_service.dart` calling the backend
- [ ] Show translated text with "Show original" toggle
- [ ] Cache check in `translations` before calling the AI
- [ ] Fallback to original text when translation fails
- [ ] Voice note recording (max 60 s), upload, and playback

**Done when:** two phones with different languages can chat in realtime, see translated text, toggle the original, and exchange images and voice notes (voice not translated yet).

## Phase 3: 9 Nov - 22 Nov 2026
Voice translation, extras, testing, and delivery.

- [ ] `POST /translate/voice` with Gemini (transcribe + detect + translate in one request)
- [ ] Show translated transcript under voice bubbles
- [ ] Message search inside a chat
- [ ] In-app notification banner
- [ ] Dark mode polish and UI cleanup
- [ ] Test on real Android phones with English, Urdu, Arabic, Spanish, and Roman Urdu (text and voice)
- [ ] Fix bugs from testing
- [ ] Check the Supabase project is active before the demo
- [ ] Final report, demo video, and presentation (22 Nov 2026)

**Done when:** all features in `PROJECT_OVERVIEW.md` meet their acceptance criteria and the app is demo-ready.

---

## First prompt to give Antigravity
> Read all `.md` files in this folder. Then start Phase 1 only. List the tasks you plan to do, wait for my approval, then build them one by one following the rules in `PHASES_AND_RULES.md`.
