# AGENTS.md

Project: **AI Multilingual Messenger** (Flutter app + FastAPI backend + Supabase + Groq/Gemini translation).

## Before you do anything
Read all the files in the `instructions/` folder first:

1. `instructions/PROJECT_OVERVIEW.md` - what we are building, scope, features, edge cases
2. `instructions/TECH_AND_ARCHITECTURE.md` - tech stack, architecture, folder structure
3. `instructions/DATABASE_AND_API.md` - tables, RLS rules, API endpoints, AI prompts
4. `instructions/UI_DESIGN.md` - screens, navigation, theme
5. `instructions/PHASES_AND_RULES.md` - phase checklists, agent rules, coding guidelines

## How to work
- Build **one phase at a time**. Only work on the phase I say is current. Start with Phase 1.
- At the start of a phase, list your planned tasks and wait for my approval.
- After each task, tell me which files you created or changed and how to test it.
- Do not move to the next phase until I confirm the current one works.

## Hard rules
- Stay inside the project scope. Do not build anything listed under "Not included" in `PROJECT_OVERVIEW.md`.
- Do not change the database schema without asking me first.
- Never put API keys in Flutter code or commit real keys. Backend keys live only in environment variables.
- Translation failure must never block message delivery. Fall back to the original text.
- Do not add packages unless really needed. Tell me which one and why.
- If the docs are unclear, or a provider's API differs from what the docs say, ask me instead of guessing.

## Code style
- Simple, human-readable code. Short functions, clear names, minimal comments.
- Plain Provider with `ChangeNotifier`. No Riverpod, Bloc, GetIt, or code generation.
- No extra abstraction layers.
- Follow the folder structure in `instructions/TECH_AND_ARCHITECTURE.md`.

The full coding guidelines are in `instructions/PHASES_AND_RULES.md`.
