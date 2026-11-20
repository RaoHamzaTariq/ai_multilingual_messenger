# Project Overview: AI Multilingual Messenger

## What it is
A Flutter mobile chat app for people who speak different languages. Users sign up, add friends, and chat in realtime using text, images, or voice notes. Each user picks a preferred language. Every incoming message is language-detected (including Roman Urdu like "mera naam Ali hai") and shown in the receiver's language. The receiver can tap **Show original** to see what was actually sent.

## Objective
Build a Flutter messaging app that automatically detects the language of each text or voice message and translates it into the receiver's preferred language using AI models.

## Problem
People who don't share a language copy messages into a separate translator and paste the result back. It is slow and breaks the conversation. It is worse for Roman Urdu and for voice notes.

## Requirements the system must meet
- Translation is fast (a few seconds)
- Conversations stay private (users only see their own chats)
- AI keys never live inside the app
- Translation failure never blocks message delivery
- The same message is never translated twice for the same language

## Scope

### Included
- Sign up, login, profile with preferred language
- Supported languages: English, Urdu, Arabic, Spanish, Hindi, French, German, Chinese, Turkish, Russian
- Friend requests by username (send, accept, reject)
- One-to-one realtime chat
- Images (max 1 MB) and voice notes (max 60 seconds)
- Automatic detection and translation with "Show original"
- In-app notification banner, message search, dark mode

### Not included (do NOT build)
- Group chats
- Voice or video calls
- Push notifications when app is closed
- Spoken audio output of translations
- End-to-end encryption
- Training our own AI model
- iOS release

## Assumptions
- Users have internet access
- Android is the main platform
- Chat is only between friends
- Free cloud plans are enough
- Translation quality depends on third-party AI models

## Features and acceptance criteria

| Feature | Done when |
|---|---|
| Auth | User can sign up, log in, log out, and stay logged in after restart |
| Profile | User can set username, display name, and preferred language |
| Friends | User can search by exact username, send a request, accept or reject it |
| Realtime chat | A message sent by one user appears on the other phone without refresh |
| Images | User can send an image up to 1 MB; larger images are rejected with a clear message |
| Voice notes | User can record up to 60 s, send, and play back; recording auto-stops at 60 s |
| Text translation | Received text shows in receiver's language with a small "translated" label |
| Voice translation | Received voice note shows transcript translated into receiver's language |
| Show original | Tapping toggles between translated and original text |
| Search | User can search messages inside a chat |
| Notification banner | A banner shows in-app when a new message arrives in another chat |
| Dark mode | User can switch light/dark and the choice is remembered |

## Edge cases
- **AI fails or times out:** show the original text, message is still delivered, no crash.
- **Caching:** one translation per message per target language. Check the `translations` table before calling the AI.
- **Same language:** if the detected language equals the receiver's language, skip translation and show the message as is.
- **Rate limit hit:** show the original text and a small "translation unavailable" note.
- **Free-tier limits:** reduced by caching, per-user rate limits, and the 60 s voice cap.
- **Empty or emoji-only messages:** do not call the AI.
- **No internet:** show a simple offline message; do not crash.
- **Database paused (free tier):** the team checks it before the demo.

## Known limitations (state honestly in the report)
- Voice notes are sent to a third-party AI service (privacy).
- Roman Urdu quality depends on the model and prompt.
