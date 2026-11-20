# UI Design

Keep the design basic and clean. Use standard Material widgets. No custom animations or fancy effects.

## Theme
- Material 3, one seed color (a calm blue or teal)
- Light and dark themes defined in `lib/core/theme.dart`
- Dark mode toggle in Profile screen; choice saved with `shared_preferences`
- Font: default Material font
- Rounded message bubbles; sent messages on the right (primary color), received on the left (surface color)

## Screens and navigation

```
Splash -> (not logged in) Login <-> Sign up -> Onboarding (pick language) -> Home
       -> (logged in) Home

Home (bottom nav: Chats | Friends | Profile)
  Chats tab   -> Chat screen -> Search screen
  Friends tab -> requests + add friend by username
  Profile tab -> edit name, language, dark mode, logout
```

## Screen descriptions

**Splash:** app name and a loader while checking login state.

**Login:** email, password, Login button, link to Sign up.

**Sign up:** username, email, password, Sign up button.

**Onboarding:** "Choose your language" list of the 10 supported languages, Continue button. Saved to `profiles.preferred_language`.

**Home - Chats tab:** list of friends with last message preview and time. Tap opens the chat.

**Home - Friends tab:** a text field to send a request by username; below it, pending requests (Accept / Reject) and the accepted friends list.

**Home - Profile tab:** display name, preferred language dropdown, dark mode switch, Logout.

**Chat screen:**
- App bar: friend name, search icon
- Message list (newest at bottom)
- Each text bubble shows the translated text, a small "Translated" label, and a **Show original** link that toggles
- Voice bubble: play/pause, duration, and the translated transcript below
- Image bubble: tap to open full screen
- Input bar: text field, image button, mic button (hold or tap to record, shows timer, stops at 60 s), send button

**Search screen:** search field, list of matching messages in that chat; tapping a result goes back to the chat.

**Notification banner:** a small banner at the top of the screen showing sender name and a short preview when a message arrives for a chat that is not open. Auto-hides after about 3 seconds. Tap opens the chat.

## UI states to handle
- Loading: simple circular progress indicator
- Empty: short text such as "No chats yet. Add a friend to start."
- Error: a SnackBar with a plain message
- Translation loading: show the original text with a tiny spinner until the translation arrives
