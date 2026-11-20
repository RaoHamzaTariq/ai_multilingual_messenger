import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_final_report():
    doc = docx.Document()

    # Page Margins: 1 inch standard academic/industry
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Color Palette: Clean Professional Teal & Slate
    PRIMARY = RGBColor(0, 122, 135)       # Primary Teal #007A87
    SECONDARY = RGBColor(70, 80, 95)      # Slate Gray #46505F
    DARK_TEXT = RGBColor(33, 37, 41)      # Charcoal #212529
    ACCENT_BLUE = RGBColor(24, 119, 242)  # Bright Blue #1877F2
    BG_LIGHT = "F8FAFC"                   # Light Slate Box
    BORDER_LIGHT = "CBD5E1"               # Subtle Border

    def style_heading(p, text, size_pt, color=PRIMARY, bold=True, space_before=14, space_after=6):
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(text)
        run.bold = bold
        run.font.size = Pt(size_pt)
        run.font.color.rgb = color
        run.font.name = "Calibri"
        return run

    def add_para(text, bold_prefix="", space_after=5, italic=False):
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
        r_text.font.italic = italic
        r_text.font.color.rgb = DARK_TEXT
        return p

    def add_callout(title, text):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)

        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{BG_LIGHT}"/>')
        tcPr.append(shd)

        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="6" w:space="0" w:color="{BORDER_LIGHT}"/>
                <w:left w:val="single" w:sz="24" w:space="0" w:color="007A87"/>
                <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{BORDER_LIGHT}"/>
                <w:right w:val="single" w:sz="6" w:space="0" w:color="{BORDER_LIGHT}"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        r_t = p.add_run(f"📌 {title}\n")
        r_t.bold = True
        r_t.font.size = Pt(11)
        r_t.font.color.rgb = PRIMARY
        r_t.font.name = "Calibri"

        r_b = p.add_run(text)
        r_b.font.size = Pt(10)
        r_b.font.color.rgb = DARK_TEXT
        r_b.font.name = "Calibri"

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def add_screenshot_box(placeholder_id, title, description, instructions):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)

        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F1F5F9"/>')
        tcPr.append(shd)

        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="6" w:space="0" w:color="{BORDER_LIGHT}"/>
                <w:left w:val="single" w:sz="20" w:space="0" w:color="007A87"/>
                <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{BORDER_LIGHT}"/>
                <w:right w:val="single" w:sz="6" w:space="0" w:color="{BORDER_LIGHT}"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        r_id = p.add_run(f"📷 [ SCREENSHOT {placeholder_id} ]: {title}\n")
        r_id.bold = True
        r_id.font.size = Pt(11)
        r_id.font.color.rgb = PRIMARY
        r_id.font.name = "Calibri"

        r_desc = p.add_run(f"Demonstrates: {description}\n")
        r_desc.font.size = Pt(10)
        r_desc.font.name = "Calibri"
        r_desc.font.color.rgb = DARK_TEXT

        r_inst = p.add_run(f"Capture Instructions: {instructions}\n\n")
        r_inst.font.size = Pt(9.5)
        r_inst.font.italic = True
        r_inst.font.name = "Calibri"
        r_inst.font.color.rgb = SECONDARY

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
                        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{BORDER_LIGHT}"/>
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
    # COVER / HEADER
    # ==========================
    p_title = doc.add_paragraph()
    style_heading(p_title, "AI Multilingual Messenger", 26, PRIMARY, bold=True, space_before=10, space_after=4)

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Comprehensive Final Project Report & Technical Documentation")
    r_sub.font.size = Pt(16)
    r_sub.font.bold = True
    r_sub.font.color.rgb = SECONDARY
    p_sub.paragraph_format.space_after = Pt(14)

    # Metadata Table
    meta_headers = ["Project Attribute", "Specification & Details"]
    meta_rows = [
        ["Project Title", "AI Multilingual Messenger (Real-Time Cross-Language Chat)"],
        ["Application Category", "Real-Time Mobile/Web Messaging & Artificial Intelligence"],
        ["Frontend Tech Stack", "Flutter 3 (Dart 3) • Material Design 3 • Provider (ChangeNotifier)"],
        ["Backend Tech Stack", "FastAPI (Python 3.12) • Uvicorn • Asynchronous HTTPX Client"],
        ["Database & Security", "Supabase (PostgreSQL 15) • Row Level Security (RLS) • JWT Auth"],
        ["Real-Time Engine", "Supabase Realtime Channels (PostgreSQL WAL Replication)"],
        ["AI Text Engine", "Groq Cloud API (`openai/gpt-oss-120b` & `llama-3.3-70b-versatile`)"],
        ["AI Voice Engine", "Google Gemini Multimodal Audio (`gemini-3.1-flash-lite`)"],
        ["Cloud Storage", "Supabase Storage: `chat-images` (<= 1MB) & `chat-voice` (<= 60s)"],
        ["Delivery Status", "100% Complete (Phase 1, Phase 2, Phase 3 fully verified & passing)"]
    ]
    add_styled_table(meta_headers, meta_rows)

    # ==========================
    # SECTION 1: PROJECT ABSTRACT & PROBLEM STATEMENT
    # ==========================
    p_s1 = doc.add_paragraph()
    style_heading(p_s1, "1. Project Abstract & Problem Statement", 16)

    add_para(
        "Global digital communication continues to grow exponentially, yet language remains one of the greatest "
        "barriers to natural cross-border collaboration and interpersonal connection. Most mainstream messaging "
        "applications force users to manually copy foreign-language messages, switch to separate translation apps, "
        "and paste translations back into chat. This process is clunky, breaks conversation flow, and fails completely "
        "for voice notes or regional colloquial dialects such as Roman Urdu."
    )

    add_para(
        "The AI Multilingual Messenger solves this fundamental problem by embedding high-speed, contextual AI "
        "translation directly into the messaging core. Users type or speak in their native tongue, and their recipient "
        "instantly receives the message translated into their own preferred language in real time.",
        bold_prefix="The Solution: "
    )

    add_callout(
        "Core Philosophy: Non-Blocking Delivery",
        "Translation failure must NEVER block message delivery. If the AI model, backend, or network fails, "
        "the message is still delivered immediately in its original language. Users can always tap 'Show original' "
        "to verify verbatim phrasing."
    )

    # ==========================
    # SECTION 2: SYSTEM ARCHITECTURE & DATA FLOW
    # ==========================
    p_s2 = doc.add_paragraph()
    style_heading(p_s2, "2. System Architecture & Technical Flow", 16)

    add_para(
        "The project follows a secure, scalable 3-tier architecture with clean separation of concerns:"
    )

    arch_headers = ["Layer", "Technologies", "Responsibilities"]
    arch_rows = [
        ["Presentation Layer", "Flutter 3, Provider, Material 3", "Cross-platform UI (Web/Android), reactive state management, audio recording/playback, search filtering."],
        ["API & AI Gateway", "FastAPI (Python), Uvicorn, HTTPX", "Secure JWT validation, rate limiting, Groq text translation, Gemini multimodal audio processing."],
        ["Data & Realtime Layer", "Supabase, PostgreSQL, Storage Buckets", "User identity (Auth), relational data, Row Level Security, private media buckets, WebSocket realtime push."]
    ]
    add_styled_table(arch_headers, arch_rows)

    add_para(
        "1. Outgoing Message: User A types a message or speaks a voice note. Flutter uploads media (if any) to Supabase Storage and inserts the message row into the `messages` table.\n"
        "2. Real-Time Broadcast: Supabase Realtime immediately pushes the new row over WebSocket to User B's active client.\n"
        "3. Automated Translation: User B's client inspects the sender's language. If different from User B's preferred language, it calls FastAPI (`/translate/text` or `/translate/voice`).\n"
        "4. AI Translation & Caching: FastAPI invokes Groq (for text) or Google Gemini Flash-Lite (for voice). Results are returned to User B and cached in the Supabase `translations` table so future loads cost zero AI tokens.\n"
        "5. Read Receipts: When User B opens the chat, an update query sets `is_read = true`, triggering a real-time event back to User A to update their double checkmarks from gray to blue.",
        bold_prefix="End-to-End Operational Pipeline: "
    )

    # ==========================
    # SECTION 3: DATABASE SCHEMA & SECURITY DESIGN
    # ==========================
    p_s3 = doc.add_paragraph()
    style_heading(p_s3, "3. Database Schema & Row-Level Security (RLS)", 16)

    add_para(
        "The database is designed with strict relational constraints and PostgreSQL Row-Level Security (RLS) "
        "to guarantee total privacy between users."
    )

    db_headers = ["Table Name", "Key Columns", "Security & RLS Rule"]
    db_rows = [
        ["profiles", "id (PK, FK auth.users), username, display_name, preferred_language, created_at", "Any authenticated user can read profiles (for friend search); only owner can edit."],
        ["friendships", "id, requester_id, addressee_id, status ('pending','accepted','rejected'), created_at", "Users can only read friendships they belong to; addressee alone can update status."],
        ["messages", "id, sender_id, receiver_id, type ('text','image','voice'), content, media_url, duration_seconds, is_read, created_at", "Read only by sender or receiver; insert allowed only between accepted friends; receiver can update `is_read`."],
        ["translations", "id, message_id (FK messages), target_language, detected_language, transcript, translated_text, created_at", "Unique (message_id, target_language). Readable by chat participants; inserts performed by backend service role."]
    ]
    add_styled_table(db_headers, db_rows)

    # ==========================
    # SECTION 4: AI PROMPT ENGINEERING & TRANSLATION ENGINE
    # ==========================
    p_s4 = doc.add_paragraph()
    style_heading(p_s4, "4. AI Models & Prompt Engineering", 16)

    add_para(
        "To achieve professional, accurate translations without unwanted conversational fluff, the backend "
        "enforces strict JSON schemas on both Groq and Gemini."
    )

    add_callout(
        "Text Translation Prompt (Groq / LLaMA / GPT-OSS)",
        "Prompt Instruction:\n"
        "'You are a precise translator for a messaging app. Translate the following text into {target_language}.\n"
        "Detect the source language. Roman Urdu must count as Urdu.\n"
        "Preserve emojis, names, slang, and emotional tone.\n"
        "If already in the target language, return it unchanged.\n"
        "Reply with JSON only: {\"detected_language\": \"<code>\", \"translated_text\": \"<text>\"}'"
    )

    add_callout(
        "Voice Multimodal Audio Prompt (Google Gemini 3.1 Flash-Lite)",
        "Prompt Instruction:\n"
        "'Listen to this audio voice note carefully.\n"
        "1. Transcribe verbatim what was spoken.\n"
        "2. Detect the spoken language (Roman Urdu counts as Urdu).\n"
        "3. Translate the transcript into {target_language}.\n"
        "Reply with JSON only: {\"transcript\": \"<text>\", \"detected_language\": \"<code>\", \"translated_text\": \"<text>\"}'"
    )

    # ==========================
    # SECTION 5: PHASE-BY-PHASE IMPLEMENTATION BREAKDOWN
    # ==========================
    p_s5 = doc.add_paragraph()
    style_heading(p_s5, "5. Implementation Breakdown Across Phases", 16)

    add_para(
        "The project was executed in three disciplined phases to ensure stability, modularity, and zero bloat."
    )

    phases_headers = ["Phase", "Milestone Focus", "Delivered Features & Technical Achievements"]
    phases_rows = [
        ["Phase 1", "Foundational Architecture & Text Translation", "• Supabase Auth (Sign up, login, auto session restore).\n• User onboarding with preferred language selection.\n• Material 3 ThemeProvider (Light & Dark theme).\n• FastAPI text translation service via Groq Cloud.\n• Non-blocking message fallback."],
        ["Phase 2", "Social Graph, Real-Time Chat & Rich Media", "• Username search (`@username`) and friendship state machine.\n• 3-Tab Navigation (Chats, Friends, Profile).\n• Realtime 1-on-1 messaging channel.\n• Image sharing with strict client-side <=1 MB validation.\n• Voice note recording & in-bubble audio playback with Web/Mobile codec adaptation."],
        ["Phase 3", "AI Voice Translation, Search & System Polish", "• Multimodal voice translation via Gemini Flash-Lite.\n• Voice bubble transcript display with 'Show original' toggle.\n• In-Chat instant message search with smooth auto-scroll.\n• In-app animated notification banner for incoming background messages.\n• Real-time delivery & seen status double-ticks (gray to blue)."]
    ]
    add_styled_table(phases_headers, phases_rows)

    # ==========================
    # SECTION 6: KEY CHALLENGES & ENGINEERING SOLUTIONS
    # ==========================
    p_s6 = doc.add_paragraph()
    style_heading(p_s6, "6. Key Challenges Encountered & Engineering Solutions", 16)

    add_para(
        "During development, several real-world technical hurdles were encountered and resolved with senior-level engineering practices:"
    )

    add_para(
        "Web browsers (Chrome MediaRecorder) require `AudioEncoder.opus` (`audio/webm`), whereas native mobile devices use `AudioEncoder.aacLc` (`audio/m4a`). Defaulting to mobile codecs caused the browser mic to fail silently. "
        "Solution: Implemented platform branching with `kIsWeb`, generating `webm` on browsers and `m4a` on mobile, while reading bytes via `cross_file` `XFile.readAsBytes()` without brittle `dart:io` imports.",
        bold_prefix="1. Web vs Mobile Audio Codec Incompatibility: "
    )

    add_para(
        "Legacy Gemini endpoints (such as `gemini-2.5-flash`) were deprecated for new API keys, returning 404. "
        "Solution: Integrated the latest production-grade `gemini-3.1-flash-lite` model, which provides ultra-fast audio transcription and translation with strict JSON outputs.",
        bold_prefix="2. Deprecated AI Model Handshake: "
    )

    add_para(
        "Translations cannot be triggered repeatedly every time a conversation is opened, as this would exhaust API limits and cause lag. "
        "Solution: Implemented database-level translation caching in Supabase with a unique compound index on `(message_id, target_language)`. Once translated, messages load instantly with 0 external API calls.",
        bold_prefix="3. AI Cost & Latency Optimization: "
    )

    add_para(
        "Users in different chat tabs or browsing friends would miss incoming messages. "
        "Solution: Created an animated top-level Overlay banner wired to a global Supabase channel that alerts the user and enables 1-tap navigation directly into that conversation.",
        bold_prefix="4. Background Message Awareness: "
    )

    # ==========================
    # SECTION 7: VISUAL SCREENSHOT EVIDENCE
    # ==========================
    p_s7 = doc.add_paragraph()
    style_heading(p_s7, "7. Visual Verification & Screenshot Guide", 16)

    add_para(
        "Paste your captured application screenshots into the designated boxes below for submission to the instructor:"
    )

    add_screenshot_box(
        "1.1",
        "User Onboarding & Language Selection Screen",
        "Shows the onboarding screen where a newly registered user selects their preferred language (English, Urdu, Arabic, Spanish, etc.).",
        "Sign up a new account or view onboarding to capture the language picker interface."
    )

    add_screenshot_box(
        "1.2",
        "Friend Management & Tab Navigation",
        "Shows the Friends screen with accepted friends and the option to search other users by @username.",
        "Navigate to the Friends tab, perform a search for a friend username, and capture the friend list."
    )

    add_screenshot_box(
        "2.1",
        "Real-Time Chat with Text & Image Sharing",
        "Shows the active conversation with translated text messages, 'Translated' badge, and full-screen image attachment viewer.",
        "Send a message in a foreign language (e.g. Urdu) to an English user. Capture the translated text bubble with 'Show original' toggle and photo attachment."
    )

    add_screenshot_box(
        "3.1",
        "AI Voice Translation Bubble & 'Show Original' Toggle",
        "Shows an incoming voice message with the translated transcript displayed underneath the playback bar and status ticks.",
        "Record and send a voice note. Capture the recipient bubble showing the player, transcript, and toggle button."
    )

    add_screenshot_box(
        "3.2",
        "In-Chat Message Search Screen",
        "Shows the SearchScreen opened from the chat AppBar with matching text, voice transcripts, and photos filtered in real time.",
        "Tap the magnifying glass icon in chat, type a keyword, and capture the filtered results."
    )

    add_screenshot_box(
        "3.3",
        "In-App Notification Banner & Delivery Ticks",
        "Demonstrates the top overlay notification banner appearing when an incoming message arrives, as well as the blue double-ticks (seen status).",
        "Leave one user on the Friends screen and send a message from the other account to capture the banner sliding down."
    )

    add_screenshot_box(
        "3.4",
        "Material 3 Dark Theme Polish",
        "Demonstrates high-contrast, clean dark mode aesthetic across the Chat and Search screens.",
        "Go to Profile, switch theme to Dark Mode, and capture the chat conversation."
    )

    # ==========================
    # SECTION 8: CONCLUSION & PRESENTATION GUIDE
    # ==========================
    p_s8 = doc.add_paragraph()
    style_heading(p_s8, "8. Conclusion & Instructor Presentation Guide", 16)

    add_para(
        "The AI Multilingual Messenger is a complete, production-ready prototype that proves the feasibility "
        "of seamless, non-blocking real-time translation across text, image, and voice communication. "
        "By leveraging Flutter's lightweight Provider state management, FastAPI's async backend, and Supabase's "
        "managed PostgreSQL engine, the system delivers sub-second message delivery with enterprise-grade security."
    )

    add_para(
        "1. Slide 1 (Introduction): State the problem — language barrier in messaging and the awkwardness of manual translation.\n"
        "2. Slide 2 (Architecture): Show the Flutter -> FastAPI -> Supabase -> Gemini/Groq 3-tier diagram.\n"
        "3. Live Demo 1 (Text Translation): Send an Urdu message ('Aap kaise hain?') from User A to User B (English). Show it automatically appear as 'How are you?' and demonstrate the 'Show original' toggle.\n"
        "4. Live Demo 2 (Voice Note AI): Speak a voice note in Urdu. Play the audio on User B, showing the audio player and the automatically generated English transcript underneath.\n"
        "5. Live Demo 3 (In-Chat Search): Tap the search icon, type words from the voice transcript, and tap a result to jump directly to it.\n"
        "6. Live Demo 4 (Notification Banner & Seen Ticks): Switch User B to the Profile screen. Send a message from User A to trigger the top banner. Open it to show the double ticks turn blue.",
        bold_prefix="Recommended Presentation Script for Instructor: "
    )

    # Save document
    filename = "Final_Project_Report_AI_Multilingual_Messenger.docx"
    doc.save(filename)
    print(f"Final Project Report successfully created: {filename}")

if __name__ == "__main__":
    create_final_report()
