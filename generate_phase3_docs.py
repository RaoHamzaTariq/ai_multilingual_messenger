import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_phase3_document():
    doc = docx.Document()

    # Page Margins: 1 inch all around
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Color definitions (matching Phase 1 & 2 style)
    PRIMARY_COLOR = RGBColor(0, 122, 135)      # Teal #007A87
    SECONDARY_COLOR = RGBColor(70, 80, 95)    # Slate #46505F
    DARK_TEXT = RGBColor(33, 37, 41)          # Charcoal #212529
    BOX_BG = "F1F5F9"                         # Slate-100
    BORDER_COLOR = "CBD5E1"                   # Slate-300

    def style_heading(p, text, size_pt, color=PRIMARY_COLOR, bold=True, space_before=12, space_after=6):
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(text)
        run.bold = bold
        run.font.size = Pt(size_pt)
        run.font.color.rgb = color
        run.font.name = "Calibri"
        return run

    def add_body_paragraph(text, bold_prefix="", space_after=4):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.bold = True
            r_bold.font.size = Pt(11)
            r_bold.font.name = "Calibri"
            r_bold.font.color.rgb = DARK_TEXT
        r_text = p.add_run(text)
        r_text.font.size = Pt(11)
        r_text.font.name = "Calibri"
        r_text.font.color.rgb = DARK_TEXT
        return p

    def add_screenshot_box(placeholder_id, title, description, instructions):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)

        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{BOX_BG}"/>')
        tcPr.append(shd)

        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="6" w:space="0" w:color="{BORDER_COLOR}"/>
                <w:left w:val="single" w:sz="18" w:space="0" w:color="007A87"/>
                <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{BORDER_COLOR}"/>
                <w:right w:val="single" w:sz="6" w:space="0" w:color="{BORDER_COLOR}"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        r_id = p.add_run(f"📷 [ SCREENSHOT {placeholder_id} ]: {title}\n")
        r_id.bold = True
        r_id.font.size = Pt(11)
        r_id.font.color.rgb = PRIMARY_COLOR
        r_id.font.name = "Calibri"

        r_desc = p.add_run(f"Description: {description}\n")
        r_desc.font.size = Pt(10)
        r_desc.font.name = "Calibri"
        r_desc.font.color.rgb = DARK_TEXT

        r_inst = p.add_run(f"How to capture: {instructions}\n\n")
        r_inst.font.size = Pt(9.5)
        r_inst.font.italic = True
        r_inst.font.name = "Calibri"
        r_inst.font.color.rgb = SECONDARY_COLOR

        r_paste = p.add_run("👉 [ PASTE YOUR SCREENSHOT IMAGE HERE ]\n")
        r_paste.bold = True
        r_paste.font.size = Pt(10)
        r_paste.font.color.rgb = RGBColor(180, 80, 0)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def add_styled_table(headers, rows):
        table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        hdr_cells = table.rows[0].cells
        for i, header_text in enumerate(headers):
            cell = hdr_cells[i]
            tcPr = cell._tc.get_or_add_tcPr()
            shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="007A87"/>')
            tcPr.append(shd)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run(header_text)
            run.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.name = "Calibri"

        for r_idx, row_data in enumerate(rows):
            row_cells = table.rows[r_idx + 1].cells
            bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, cell_value in enumerate(row_data):
                cell = row_cells[c_idx]
                tcPr = cell._tc.get_or_add_tcPr()
                shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_color}"/>')
                tcPr.append(shd)

                borders = parse_xml(f'''
                    <w:tcBorders {nsdecls("w")}>
                        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{BORDER_COLOR}"/>
                        <w:top w:val="none"/>
                        <w:left w:val="none"/>
                        <w:right w:val="none"/>
                    </w:tcBorders>
                ''')
                tcPr.append(borders)

                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(5)
                p.paragraph_format.space_after = Pt(5)
                run = p.add_run(str(cell_value))
                run.font.size = Pt(9.5)
                run.font.name = "Calibri"
                run.font.color.rgb = DARK_TEXT

        doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ==========================
    # TITLE & HEADER
    # ==========================
    p_title = doc.add_paragraph()
    style_heading(p_title, "AI Multilingual Messenger", 24, PRIMARY_COLOR, bold=True, space_before=0, space_after=4)

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Phase 3 Implementation & Final Project Documentation")
    r_sub.font.size = Pt(15)
    r_sub.font.bold = True
    r_sub.font.color.rgb = SECONDARY_COLOR
    p_sub.paragraph_format.space_after = Pt(12)

    # Metadata Table
    meta_headers = ["Project Detail", "Specification"]
    meta_rows = [
        ["Phase", "Phase 3: AI Voice Translation, Search, Notifications & Theme Polish"],
        ["Target Platforms", "Flutter Web & Android Mobile (Cross-platform)"],
        ["Backend", "FastAPI (Python) with Google Gemini AI (`gemini-3.1-flash-lite`) & Groq"],
        ["Database & Realtime", "Supabase PostgreSQL with Row Level Security & Realtime Channels"],
        ["Storage Buckets", "`chat-images` (Private, <=1 MB) and `chat-voice` (Private, <=60s)"],
        ["State Management", "Provider with ChangeNotifier (zero code-generation, clean M3)"],
        ["Verification Status", "Zero Lint Errors (`flutter analyze`), 100% Passing Integration Tests"]
    ]
    add_styled_table(meta_headers, meta_rows)

    # ==========================
    # SECTION 1: EXECUTIVE SUMMARY
    # ==========================
    p_s1 = doc.add_paragraph()
    style_heading(p_s1, "1. Executive Summary & Phase 3 Scope", 16)

    add_body_paragraph(
        "Phase 3 represents the completion and polish of the AI Multilingual Messenger application. "
        "Building upon the foundational authentication in Phase 1 and the real-time social chatting, "
        "image sharing, and voice recording established in Phase 2, Phase 3 delivers complete end-to-end "
        "multilingual intelligence and rich conversational UX."
    )

    add_body_paragraph(
        "The primary focus of Phase 3 was empowering users with real-time AI voice translation, instant "
        "conversation search, seamless in-app notification banners for background incoming messages, "
        "and comprehensive Material 3 light/dark mode UI polish.",
        bold_prefix="Core Mission: "
    )

    add_body_paragraph(
        "All features have been engineered in strict adherence to the project specifications: zero external "
        "bloat, no complex architectures (Bloc/Riverpod), no closed-app push notification over-engineering, "
        "and guaranteed message delivery even during network or translation API failures.",
        bold_prefix="Architectural Compliance: "
    )

    # Scope checklist table
    scope_headers = ["Phase 3 Feature", "Implementation Status", "Verification Method"]
    scope_rows = [
        ["AI Voice Translation Backend", "COMPLETED", "FastAPI `POST /translate/voice` with Gemini Flash-Lite & Supabase DB caching"],
        ["Voice Bubble Transcript & Translation", "COMPLETED", "In-bubble playback with translated text, badge, and 'Show original' toggle"],
        ["In-Chat Search Screen", "COMPLETED", "Instant client-side indexing across text, translation, transcripts & photos"],
        ["Auto-Scroll to Search Hit", "COMPLETED", "Tapping search match returns to chat and scrolls directly to targeted bubble"],
        ["In-App Notification Banner", "COMPLETED", "Top overlay banner for incoming messages with sender preview & 1-tap chat jump"],
        ["Message Delivered / Seen Status", "COMPLETED", "Realtime double-tick icons (gray for delivered/unseen, bright blue for seen)"],
        ["Dark / Light Mode Theme Polish", "COMPLETED", "Material 3 dynamic theming across search, banners, bubbles, and dialogs"],
        ["Audio Codec Web/Mobile Compatibility", "COMPLETED", "Opus webm for Chrome/Safari browser MediaRecorder, AAC m4a for mobile"]
    ]
    add_styled_table(scope_headers, scope_rows)

    # ==========================
    # SECTION 2: AI VOICE TRANSLATION ARCHITECTURE
    # ==========================
    p_s2 = doc.add_paragraph()
    style_heading(p_s2, "2. AI Voice Translation Engine", 16)

    add_body_paragraph(
        "Voice messages require a multimodal pipeline capable of ingesting raw audio, performing speech-to-text "
        "transcription in the speaker's language, identifying the language (including non-standard forms such as "
        "Roman Urdu), and translating the transcript accurately into the recipient's preferred language."
    )

    add_body_paragraph(
        "1. Audio Capture: Recorded via Flutter `record` package using Opus WebM on browsers and AAC m4a on native devices.\n"
        "2. Supabase Storage Upload: Audio bytes are stored securely in the private `chat-voice` storage bucket.\n"
        "3. Database Record Insertion: A message row is inserted into `messages` with `type='voice'`, `duration_seconds`, and storage path.\n"
        "4. FastAPI Translation Request: The recipient client calls `POST /translate/voice` passing `message_id`, `audio_path`, and `target_language`.\n"
        "5. Gemini Multimodal Inference: The FastAPI backend downloads the audio bytes and passes them to `gemini-3.1-flash-lite` with a strict JSON system prompt.\n"
        "6. Transcript & Translation Caching: Results are persisted in the Supabase `translations` table for instant retrieval on future loads.\n"
        "7. Flutter UI Display: The voice bubble updates reactively to show the translated transcript with a 'Translated' badge and toggle button.",
        bold_prefix="Pipeline Workflow: "
    )

    add_body_paragraph(
        "You are an expert voice translator for a multilingual messaging app. "
        "Listen to this audio carefully and output STRICT JSON format with keys: "
        "'transcript' (verbatim transcription in spoken language), "
        "'detected_language' (detected language code), and "
        "'translated_text' (accurate translation into the requested target language). "
        "Support English, Urdu, Arabic, Spanish, French, and Roman Urdu.",
        bold_prefix="Gemini System Prompt Design: "
    )

    # ==========================
    # SECTION 3: IN-CHAT SEARCH & IN-APP NOTIFICATIONS
    # ==========================
    p_s3 = doc.add_paragraph()
    style_heading(p_s3, "3. In-Chat Search & In-App Notifications", 16)

    add_body_paragraph(
        "A dedicated SearchScreen was built to allow users to search within any conversation effortlessly. "
        "The search bar supports real-time text matching against original message content, translated text, "
        "voice message speech transcripts, and photo attachment queries. Selecting any result immediately pops "
        "the search screen and smoothly scrolls the chat list directly to that specific message.",
        bold_prefix="In-Chat Search: "
    )

    add_body_paragraph(
        "When an incoming message arrives via Supabase Realtime from a friend whose chat is not currently open, "
        "a high-priority, animated overlay banner slides down from the top of the screen. "
        "The banner displays the sender's avatar, name, and a concise message preview (text, photo badge, or voice duration). "
        "Tapping the banner immediately opens the active chat with that friend. It automatically auto-dismisses after 3.5 seconds.",
        bold_prefix="In-App Notification Banner: "
    )

    add_body_paragraph(
        "To provide users with clear feedback on message receipt, sent bubbles display dynamic status ticks. "
        "When a message is delivered to the recipient but not seen yet, a double checkmark (✓✓) appears in subtle gray beside the timestamp. "
        "As soon as the recipient opens the conversation, the messages are marked as read in Supabase, and Realtime "
        "Postgres changes trigger an immediate update on the sender's screen, turning the double checkmark bright cyan-blue.",
        bold_prefix="Message Delivery & Seen Status Indicators: "
    )

    # ==========================
    # SECTION 4: CODEBASE ARTIFACTS
    # ==========================
    p_s4 = doc.add_paragraph()
    style_heading(p_s4, "4. Summary of Phase 3 Code Changes", 16)

    files_headers = ["File Path", "Layer", "Purpose & Key Changes"]
    files_rows = [
        ["backend/translate_voice.py", "Backend Engine", "Gemini 3.1 Flash-Lite multimodal audio transcription & translation service"],
        ["backend/main.py", "Backend API", "Registered `POST /translate/voice` with rate limiting, JWT auth, and cache check"],
        ["backend/supabase_client.py", "Backend Data", "Added `get_message_duration` and `download_voice_file` from `chat-voice` bucket"],
        ["lib/models/message.dart", "Data Model", "Added `is_read` boolean field with backward-compatible safe parsing"],
        ["lib/widgets/message_bubble.dart", "Flutter UI", "Added dynamic delivered (gray ✓✓) and seen (blue ✓✓) indicators"],
        ["lib/widgets/voice_message_bubble.dart", "Flutter UI", "Integrated translated transcript display, 'Translated' badge & toggle action"],
        ["lib/services/translation_service.dart", "Flutter Client", "Added `translateVoice` calling FastAPI `/translate/voice` with JWT auth"],
        ["lib/screens/search_screen.dart", "Flutter UI", "Built instant in-chat search across text, translation, transcripts, and photos"],
        ["lib/screens/chat_screen.dart", "Flutter UI", "Wired search action in AppBar, smart auto-scroll, and chat state cleanup"],
        ["lib/widgets/notification_banner.dart", "Flutter Widget", "Animated top overlay banner with sender preview and 1-tap navigation"],
        ["lib/screens/home_screen.dart", "Flutter UI", "Global Realtime listener for incoming messages triggering notification banner"],
        ["lib/services/supabase_service.dart", "Flutter Service", "Added `subscribeToAllUserMessages`, `markMessagesAsRead`, and update events"]
    ]
    add_styled_table(files_headers, files_rows)

    # ==========================
    # SECTION 5: SCREENSHOT EVIDENCE PLACEHOLDERS
    # ==========================
    p_s5 = doc.add_paragraph()
    style_heading(p_s5, "5. Visual Verification & Screenshot Guide", 16)

    add_body_paragraph(
        "The following placeholders provide designated locations to paste visual screenshots verifying each "
        "Phase 3 feature in action. Follow the capture instructions provided in each box."
    )

    add_screenshot_box(
        "3.1",
        "AI Voice Translation Bubble & 'Show Original' Toggle",
        "Shows an incoming voice note from a foreign-language friend with the translated transcript displayed underneath the audio player, the 'Translated' chip, and the toggle button.",
        "Record a voice note in Urdu or Spanish on Account A. On Account B (English), view the incoming voice bubble with the English transcript and tap 'Show original'."
    )

    add_screenshot_box(
        "3.2",
        "In-Chat Message Search with Real-Time Filtering",
        "Shows the SearchScreen opened from the chat AppBar, displaying matching messages across text, voice transcript, and photo attachments with highlighted previews.",
        "In a conversation with messages, tap the Search icon in the top AppBar. Type a keyword (e.g. 'hello', 'voice', or 'photo') and observe the filtered search results."
    )

    add_screenshot_box(
        "3.3",
        "In-App Notification Banner on Incoming Message",
        "Shows the sleek top notification banner appearing while on the Chats tab or Friends tab when an incoming message arrives from another user.",
        "Keep Account B on the main Chats tab. On Account A, send a message to Account B. Capture the top banner displaying the sender's avatar, name, and message preview."
    )

    add_screenshot_box(
        "3.4",
        "Material 3 Dark Mode View",
        "Demonstrates complete visual consistency in Dark Mode across the Chat screen, Voice Bubbles, Search screen, and Notification Banner.",
        "Open Profile tab, toggle Dark Mode ON, then navigate into a Chat screen and Search screen to capture the polished dark theme aesthetic."
    )

    # ==========================
    # SECTION 6: COMPLETE TEST INSTRUCTIONS
    # ==========================
    p_s6 = doc.add_paragraph()
    style_heading(p_s6, "6. Complete Verification & Testing Flow", 16)

    add_body_paragraph(
        "1. Backend Health Check: Run `uvicorn main:app --reload --port 8000` inside `backend/`. Verify `GET http://localhost:8000/health` returns status `ok`.\n"
        "2. Run Flutter App: In terminal, run `flutter run -d chrome --web-port 5000` (or Android emulator).\n"
        "3. Multi-User Session: Open two separate browser profiles (or Chrome Incognito) representing User A (Urdu speaker) and User B (English speaker).\n"
        "4. Test Voice Note AI Translation:\n"
        "   - User A records a voice note speaking Urdu (e.g., 'Aap kaise hain?') and sends it.\n"
        "   - User B receives the voice note via Realtime. The audio player appears.\n"
        "   - Translation service triggers Gemini 3.1 Flash-Lite, generating English transcript: 'How are you?'.\n"
        "   - User B taps 'Show original' to see Urdu verbatim transcript, and 'Show translated' to toggle back.\n"
        "5. Test In-Chat Search:\n"
        "   - Tap the Search icon in the top AppBar.\n"
        "   - Search for words spoken in the voice note or typed in chat.\n"
        "   - Tap a search result; the app immediately returns to chat and scrolls to the message.\n"
        "6. Test In-App Notification Banner:\n"
        "   - Leave User B on the Friends tab or Home screen.\n"
        "   - Send a message from User A.\n"
        "   - Observe the top banner appear with User A's name and message preview. Tap it to directly open the chat.\n"
        "7. Test Light/Dark Mode:\n"
        "   - Go to Profile -> Toggle Theme. Ensure high contrast, readable text, and correct bubble styling in both modes.",
        bold_prefix="Step-by-Step Test Walkthrough: "
    )

    # Save document
    output_filename = "Phase_3_Documentation_AI_Multilingual_Messenger.docx"
    doc.save(output_filename)
    print(f"Phase 3 Documentation successfully saved to {output_filename}")

if __name__ == "__main__":
    create_phase3_document()
