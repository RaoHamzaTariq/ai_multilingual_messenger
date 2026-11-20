import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_final_report():
    doc = docx.Document()

    # Page Margins: 1 inch all around (matching Phase 2 doc)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Color Palette matching Phase 2 design
    PRIMARY_COLOR = RGBColor(0, 122, 135)      # Primary Teal #007A87
    SECONDARY_COLOR = RGBColor(70, 80, 95)    # Slate #46505F
    DARK_TEXT = RGBColor(33, 37, 41)          # Charcoal #212529
    BOX_BG = "F1F5F9"                         # Slate-100
    BORDER_COLOR = "CBD5E1"                   # Slate-300

    def style_heading(p, text, size_pt, color=PRIMARY_COLOR, bold=True, space_before=14, space_after=6):
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

    def add_callout_box(title, text):
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
                <w:left w:val="single" w:sz="20" w:space="0" w:color="007A87"/>
                <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{BORDER_COLOR}"/>
                <w:right w:val="single" w:sz="6" w:space="0" w:color="{BORDER_COLOR}"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        r_t = p.add_run(f"📌 {title}\n")
        r_t.bold = True
        r_t.font.size = Pt(11)
        r_t.font.color.rgb = PRIMARY_COLOR
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
    # COVER / HEADER (Phase 2 Theme)
    # ==========================
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(20)
    title_p.paragraph_format.space_after = Pt(4)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = title_p.add_run("AI Multilingual Messenger")
    r_title.bold = True
    r_title.font.size = Pt(26)
    r_title.font.name = "Calibri"
    r_title.font.color.rgb = PRIMARY_COLOR

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(16)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = sub_p.add_run("Complete Final Project Report & Technical Documentation")
    r_sub.font.size = Pt(14)
    r_sub.font.name = "Calibri"
    r_sub.font.bold = True
    r_sub.font.color.rgb = SECONDARY_COLOR

    # Metadata & Group Members Table
    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Project Name:", "AI Multilingual Messenger"),
        ("Group Members:", 
         "1. Rao Hamza Tariq (CSC-24F-042)\n"
         "2. Imtiaz Maqbool (SCS-24F-003)\n"
         "3. Fahad Yaseen (CSC-25S-201)\n"
         "4. Muhammad Saad (CSC-24F-025)\n"
         "5. Shahmeer Baqai (CSC-24F-027)"),
        ("Course / Project:", "Mobile Application Development & AI Capstone Project"),
        ("Date & Status:", "November 2026 — Final Project Completed, Verified & Approved"),
        ("Technology Stack:", "Flutter 3 (Dart 3), FastAPI (Python 3.12), Supabase (PostgreSQL 15 / RLS / Realtime / Storage), Groq AI (Text), Google Gemini 3.1 Flash-Lite (Voice)"),
    ]
    for i, (k, v) in enumerate(meta_data):
        cell_k, cell_v = meta_table.cell(i, 0), meta_table.cell(i, 1)
        cell_k.width = Inches(2.2)
        cell_v.width = Inches(4.3)
        pk = cell_k.paragraphs[0]
        pk.paragraph_format.space_after = Pt(2)
        rk = pk.add_run(k)
        rk.bold = True
        rk.font.size = Pt(10)
        rk.font.name = "Calibri"
        rk.font.color.rgb = PRIMARY_COLOR

        pv = cell_v.paragraphs[0]
        pv.paragraph_format.space_after = Pt(2)
        rv = pv.add_run(v)
        rv.font.size = Pt(9.5)
        rv.font.name = "Calibri"
        rv.font.color.rgb = DARK_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ==========================
    # SECTION 1: EXECUTIVE SUMMARY & PROBLEM STATEMENT
    # ==========================
    style_heading(doc.add_paragraph(), "1. Executive Summary & Problem Statement", 16)
    add_body_paragraph(
        "Global digital communication continues to grow exponentially, yet language remains one of the primary "
        "barriers to natural interpersonal connection and cross-border collaboration. Most mainstream messaging "
        "applications force users to manually copy foreign-language messages, switch out of the app to external translation "
        "tools, and paste translations back into chat. This creates high friction, breaks conversation flow, and fails completely "
        "for voice notes or regional colloquial dialects such as Roman Urdu."
    )
    add_body_paragraph(
        "The AI Multilingual Messenger solves this problem by embedding high-speed, contextual AI translation directly "
        "into the messaging core. Users type or speak in their native tongue, and their recipient instantly receives the message "
        "translated into their own preferred language in real time.",
        bold_prefix="The Solution: "
    )
    add_callout_box(
        "Core Philosophy: Non-Blocking Delivery",
        "Translation failure must NEVER block message delivery. If the AI model, backend, or network encounters an issue, "
        "the message is still delivered immediately in its original language. Users can always tap 'Show original' to verify verbatim phrasing."
    )

    # ==========================
    # SECTION 2: SYSTEM ARCHITECTURE & LIFECYCLES
    # ==========================
    style_heading(doc.add_paragraph(), "2. System Architecture & Message Lifecycles", 16)
    add_body_paragraph(
        "The application follows a secure 3-tier architecture separating user data management from AI translation workloads:"
    )

    arch_headers = ["Tier", "Technologies", "Responsibilities"]
    arch_rows = [
        ["Presentation Tier", "Flutter 3, Provider, Material 3", "Cross-platform UI (Web/Android), reactive state management, audio recording/playback, search filtering, and delivery status indicators."],
        ["API & AI Gateway", "FastAPI (Python 3.12), Uvicorn, HTTPX", "Secure JWT validation, rate limiting, Groq text translation, Gemini multimodal audio processing, and database caching."],
        ["Data & Realtime Tier", "Supabase, PostgreSQL 15, Storage", "User identity (Auth), relational tables, Row Level Security (RLS), private media storage buckets, and WebSocket realtime replication."]
    ]
    add_styled_table(arch_headers, arch_rows)

    add_body_paragraph(
        "Sender inserts a record into the 'messages' table directly in Supabase. Supabase Realtime emits "
        "the new row event to the active recipient's channel. The recipient's client inspects the local 'translations' "
        "table. If uncached, it sends an authenticated HTTP request (with Supabase JWT) to the FastAPI backend. Groq "
        "(openai/gpt-oss-120b) translates the text into the recipient's preferred language, stores the result in "
        "the database for future instant retrieval, and returns JSON. If translation fails, the client gracefully "
        "displays the original text without crashing.",
        bold_prefix="• Realtime Text Message Flow: "
    )
    add_body_paragraph(
        "Sender selects an image via image_picker. The app validates the byte length against AppConstants.maxImageSizeBytes (1 MB). "
        "Oversized files are immediately rejected with an explanatory SnackBar. Valid images are uploaded to the private 'chat-images' "
        "Supabase Storage bucket, and a message of type 'image' containing the file path is inserted. Recipients generate a secure "
        "signed URL to render the image in the bubble, with tap-to-expand full-screen zoom.",
        bold_prefix="• Image Sharing Pipeline: "
    )
    add_body_paragraph(
        "Sender taps the microphone icon to begin audio recording (Opus WebM on web browsers, AAC M4A on mobile). "
        "A live timer counts up to 60 seconds (AppConstants.maxVoiceDurationSeconds) with auto-stop cap. The audio is uploaded to "
        "the private 'chat-voice' bucket, and the recipient client invokes FastAPI `POST /translate/voice`. Google Gemini 3.1 Flash-Lite "
        "transcribes the spoken audio, detects the language, and translates the transcript into the recipient's language in a single step.",
        bold_prefix="• AI Voice Note Pipeline: "
    )

    # ==========================
    # SECTION 3: DELIVERABLES CHECKLIST
    # ==========================
    style_heading(doc.add_paragraph(), "3. Complete Project Deliverables Checklist", 16)
    checklist_items = [
        ("Supabase Auth & Session Management", "Completed", "Sign up, login, auto-restore session across restarts, and sign out"),
        ("User Onboarding & Language Selection", "Completed", "Selection of primary language (10 supported languages) saved to profiles table"),
        ("Friend Search by Username", "Completed", "Exact @username lookup in Supabase with self-add and duplicate request prevention"),
        ("Friend Requests (Send, Accept, Reject)", "Completed", "Friendship state machine in FriendsProvider with incoming/outgoing tabs"),
        ("3-Tab Navigation Bar", "Completed", "Material 3 NavigationBar hosting Chats, Friends, and Profile tabs"),
        ("Realtime 1-on-1 Chat Screen", "Completed", "Active chat UI with auto-scrolling ListView and Supabase Realtime channel listener"),
        ("AI Text Translation Engine", "Completed", "FastAPI /translate/text using Groq (openai/gpt-oss-120b) with Roman Urdu support"),
        ("Show Original / Translated Toggle", "Completed", "message_bubble.dart displays 'Translated' badge and interactive toggle button"),
        ("Image Sharing (max 1 MB)", "Completed", "Client-side byte validation, upload to chat-images bucket, full-screen viewer"),
        ("Voice Recording & Playback (max 60s)", "Completed", "audio_service.dart using record 7.x, live timer bar, 60-second auto-stop cap"),
        ("AI Voice Translation & Transcript", "Completed", "Gemini 3.1 Flash-Lite multimodal translation displaying transcript in bubble"),
        ("In-Chat Message Search Screen", "Completed", "Instant search filtering across text, translation, voice transcripts, and photos"),
        ("In-App Notification Banner", "Completed", "Top overlay banner for incoming messages with sender preview and 1-tap navigation"),
        ("Message Delivery & Seen Ticks", "Completed", "Realtime double-ticks: subtle gray for delivered/unseen, bright blue for seen"),
        ("Material 3 Light / Dark Theme", "Completed", "Dynamic theme toggle with persisted user preference across sessions"),
        ("GitHub Actions Android APK Builder", "Completed", "Automated CI/CD workflow compiling release APK downloadable from GitHub Actions"),
    ]

    t_check = doc.add_table(rows=len(checklist_items) + 1, cols=3)
    t_check.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Deliverable / Milestone", "Status", "Verification Details"]
    for j, h in enumerate(headers):
        cell = t_check.cell(0, j)
        tcPr = cell._tc.get_or_add_tcPr()
        tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="007A87"/>'))
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.name = "Calibri"

    for i, (item, stat, det) in enumerate(checklist_items):
        r_cells = t_check.rows[i + 1].cells
        r_cells[0].width = Inches(2.2)
        r_cells[1].width = Inches(1.1)
        r_cells[2].width = Inches(3.2)
        r_cells[0].paragraphs[0].add_run(item).font.size = Pt(9.5)
        r_stat = r_cells[1].paragraphs[0].add_run(stat)
        r_stat.bold = True
        r_stat.font.size = Pt(9.5)
        r_stat.font.color.rgb = RGBColor(0, 140, 70)
        r_cells[2].paragraphs[0].add_run(det).font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ==========================
    # SECTION 4: DATABASE SCHEMA & SECURITY DESIGN
    # ==========================
    style_heading(doc.add_paragraph(), "4. Database Schema & Security Design", 16)
    add_body_paragraph(
        "The relational database schema is deployed on Supabase (PostgreSQL 15) with strict Row-Level Security (RLS) policies:"
    )

    db_headers = ["Table Name", "Key Columns", "Security & Access Control (RLS)"]
    db_rows = [
        ["profiles", "id (PK, FK auth.users), username, display_name, preferred_language, created_at", "Authenticated users can read (for username search); only the row owner can update their own profile."],
        ["friendships", "id, requester_id, addressee_id, status ('pending','accepted','rejected'), created_at", "Users can only read rows where they are requester or addressee; only addressee can update status."],
        ["messages", "id, sender_id, receiver_id, type ('text','image','voice'), content, media_url, duration_seconds, is_read, created_at", "Users can only read messages they sent or received. Inserts permitted only between accepted friends. Recipient can update `is_read`."],
        ["translations", "id, message_id (FK messages), target_language, detected_language, transcript, translated_text, created_at", "Compound UNIQUE(message_id, target_language). Chat participants can read translations; inserts performed by backend service role."]
    ]
    add_styled_table(db_headers, db_rows)

    # ==========================
    # SECTION 5: TECHNICAL CHALLENGES OVERCOME
    # ==========================
    style_heading(doc.add_paragraph(), "5. Technical Challenges & Engineering Solutions", 16)
    add_body_paragraph(
        "Web browsers require `AudioEncoder.opus` (`audio/webm`), while mobile devices default to `AudioEncoder.aacLc` (`audio/m4a`). Using mobile defaults caused the browser mic to fail silently. "
        "Solution: Implemented platform branching with `kIsWeb`, recording `.webm` on browsers and `.m4a` on mobile, while reading audio bytes via `cross_file` `XFile.readAsBytes()` without brittle `dart:io` imports.",
        bold_prefix="1. Web vs Mobile Audio Codec Adaptation: "
    )
    add_body_paragraph(
        "Older Gemini model endpoints (such as `gemini-2.5-flash`) were retired for new API keys, returning 404 errors. "
        "Solution: Migrated to Google's production `gemini-3.1-flash-lite` model, which natively supports multimodal audio transcription and translation in a single fast inference pass.",
        bold_prefix="2. Deprecated AI Model Handshake: "
    )
    add_body_paragraph(
        "Calling AI translation models repeatedly every time a conversation is opened causes API rate limits, slow UI rendering, and excessive token costs. "
        "Solution: Implemented a persistent caching layer in Supabase (`translations` table). Uncached messages are translated once and stored permanently, resulting in 0 API tokens and instant loading on subsequent reads.",
        bold_prefix="3. AI Cost & Latency Optimization: "
    )

    # ==========================
    # SECTION 6: VISUAL SCREENSHOT EVIDENCE
    # ==========================
    style_heading(doc.add_paragraph(), "6. Visual Verification & Screenshot Guide", 16)
    add_body_paragraph(
        "Paste your captured application screenshots into the designated placeholder boxes below:"
    )

    add_screenshot_box(
        "1.1",
        "User Onboarding & Language Selection",
        "Shows the language picker screen where a newly registered user chooses their preferred language.",
        "Sign up a new account or open onboarding to capture the language picker interface."
    )
    add_screenshot_box(
        "1.2",
        "Friends Management & 3-Tab Shell",
        "Shows the Friends screen with accepted friends and the option to search other users by @username.",
        "Navigate to the Friends tab, perform a search, and capture the friend list."
    )
    add_screenshot_box(
        "2.1",
        "Real-Time Chat & 'Show Original' Toggle",
        "Shows a conversation with translated text messages, the 'Translated' badge, and the interactive toggle button.",
        "Send an Urdu message to an English account. Capture the translated bubble with 'Show original' toggle."
    )
    add_screenshot_box(
        "2.2",
        "Image Sharing & Full-Screen Viewer",
        "Demonstrates photo attachment sharing with thumbnail rendering and interactive full-screen viewer.",
        "Pick and send an image (under 1 MB). Tap on the image in the chat to open the full-screen view."
    )
    add_screenshot_box(
        "3.1",
        "AI Voice Translation Bubble & Transcript",
        "Shows an incoming voice note with playback controls, the translated transcript underneath, and the 'Translated' chip.",
        "Record and send a voice note. Capture the recipient bubble showing audio playback and English transcript."
    )
    add_screenshot_box(
        "3.2",
        "In-Chat Message Search Screen",
        "Shows the SearchScreen opened from the chat AppBar with matching text, voice transcripts, and photos filtered in real time.",
        "Tap the magnifying glass icon in chat, type a search keyword, and capture the filtered results."
    )
    add_screenshot_box(
        "3.3",
        "In-App Notification Banner & Delivery Ticks",
        "Shows the top animated overlay banner appearing when an incoming message arrives, as well as the blue double-ticks (seen status).",
        "Leave one user on the Friends screen and send a message from the other account to capture the banner."
    )
    add_screenshot_box(
        "3.4",
        "Material 3 Dark Theme Polish",
        "Demonstrates high-contrast, clean dark mode aesthetic across the Chat and Search screens.",
        "Go to Profile, switch theme to Dark Mode, and capture the chat conversation."
    )

    # ==========================
    # SECTION 7: GROUP CONTRIBUTIONS & INSTRUCTOR PRESENTATION
    # ==========================
    style_heading(doc.add_paragraph(), "7. Group Contributions & Presentation Guide", 16)
    add_body_paragraph(
        "The project was successfully executed through collaborative teamwork across the frontend, backend, database, and AI pipelines:"
    )

    contrib_headers = ["Group Member", "Roll Number", "Key Contributions & Ownership"]
    contrib_rows = [
        ["Rao Hamza Tariq", "CSC-24F-042", "Full-Stack Lead: Supabase Architecture, FastAPI AI Gateway, Gemini Voice Engine & GitHub Actions CI/CD."],
        ["Imtiaz Maqbool", "SCS-24F-003", "Frontend Lead: Real-Time Chat Screen, Message Bubbles, In-Bubble Audio Player & Codec Adaptation."],
        ["Fahad Yaseen", "CSC-25S-201", "UI/UX & Navigation: 3-Tab Home Shell, Material 3 Light/Dark ThemeProvider & Onboarding Flows."],
        ["Muhammad Saad", "CSC-24F-025", "Social Graph & Search: Friendship State Machine, SearchScreen Filtering & Media Viewer."],
        ["Shahmeer Baqai", "CSC-24F-027", "Notification & Status Systems: In-App Top Notification Banner, Delivery & Seen Ticks, and QA Testing."]
    ]
    add_styled_table(contrib_headers, contrib_rows)

    add_body_paragraph(
        "1. Slide 1 (Title & Problem): Introduce the group members and articulate the problem — manual translation in chat is slow and breaks for voice.\n"
        "2. Slide 2 (Architecture): Walk through the 3-tier architecture (Flutter + FastAPI + Supabase + Gemini/Groq).\n"
        "3. Live Demo 1 (Text AI): User A sends Urdu text ('Aap kaise hain?'); User B receives English ('How are you?') and toggles 'Show original'.\n"
        "4. Live Demo 2 (Voice AI): User A records a voice note; User B plays it and shows the automatically generated English transcript.\n"
        "5. Live Demo 3 (Search & Ticks): Tap search icon, filter messages, and point out the blue double-ticks indicating seen status.\n"
        "6. Live Demo 4 (Notification Banner): Send a message while User B is on the Friends tab; show the top banner and jump directly into chat.",
        bold_prefix="Recommended Presentation Flow: "
    )

    # Save document
    filename = "Final_Project_Report_AI_Multilingual_Messenger.docx"
    doc.save(filename)
    print(f"Final Project Report successfully created: {filename}")

if __name__ == "__main__":
    create_final_report()
