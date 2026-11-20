import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_final_report():
    doc = docx.Document()

    # Page Margins: 1 inch all around (matching Phase 2 document)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

        # Footer styling matching Phase 2
        footer = section.footer
        p_f = footer.paragraphs[0]
        p_f.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_f = p_f.add_run("AI Multilingual Messenger — Final Project Comprehensive Report")
        r_f.font.size = Pt(8.5)
        r_f.font.color.rgb = RGBColor(120, 130, 140)
        r_f.font.name = "Calibri"

    # Exact Color Definitions from Phase 2
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

    # ==========================
    # COVER / HEADER (Exact Phase 2 Layout)
    # ==========================
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(24)
    title_p.paragraph_format.space_after = Pt(4)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = title_p.add_run("AI Multilingual Messenger")
    r_title.bold = True
    r_title.font.size = Pt(24)
    r_title.font.name = "Calibri"
    r_title.font.color.rgb = PRIMARY_COLOR

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(18)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = sub_p.add_run("Complete Final Project Report & Technical Architecture Documentation")
    r_sub.font.size = Pt(14)
    r_sub.font.name = "Calibri"
    r_sub.font.color.rgb = SECONDARY_COLOR

    # Meta Table (matching Phase 2 box layout exactly)
    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Course / Project:", "Mobile Application Development / Capstone Project"),
        ("Project Name:", "AI Multilingual Messenger"),
        ("Group Members:", 
         "1. Rao Hamza Tariq (CSC-24F-042)\n"
         "2. Imtiaz Maqbool (SCS-24F-003)\n"
         "3. Fahad Yaseen (CSC-25S-201)\n"
         "4. Muhammad Saad (CSC-24F-025)\n"
         "5. Shahmeer Baqai (CSC-24F-027)"),
        ("Date & Status:", "November 2026 — Final Project Completed, Verified & Approved"),
        ("Technology Stack:", "Flutter 3.x, Supabase (PostgreSQL 15 / Auth / Realtime / Storage), FastAPI, Groq AI, Google Gemini 3.1 Flash-Lite, Audio Record & Playback"),
    ]
    for i, (k, v) in enumerate(meta_data):
        cell_k, cell_v = meta_table.cell(i, 0), meta_table.cell(i, 1)
        cell_k.width = Inches(2.2)
        cell_v.width = Inches(4.3)

        # Style borders like Phase 2
        for cell in (cell_k, cell_v):
            borders = parse_xml(f'''
                <w:tcBorders {nsdecls("w")}>
                    <w:top w:val="single" w:sz="4" w:space="0" w:color="{BORDER_COLOR}"/>
                    <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{BORDER_COLOR}"/>
                    <w:left w:val="single" w:sz="4" w:space="0" w:color="{BORDER_COLOR}"/>
                    <w:right w:val="single" w:sz="4" w:space="0" w:color="{BORDER_COLOR}"/>
                </w:tcBorders>
            ''')
            cell._tc.get_or_add_tcPr().append(borders)

        pk = cell_k.paragraphs[0]
        pk.paragraph_format.space_before = Pt(3)
        pk.paragraph_format.space_after = Pt(3)
        rk = pk.add_run(k)
        rk.bold = True
        rk.font.size = Pt(10)
        rk.font.name = "Calibri"
        rk.font.color.rgb = PRIMARY_COLOR

        pv = cell_v.paragraphs[0]
        pv.paragraph_format.space_before = Pt(3)
        pv.paragraph_format.space_after = Pt(3)
        rv = pv.add_run(v)
        rv.font.size = Pt(9.5)
        rv.font.name = "Calibri"
        rv.font.color.rgb = DARK_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ==========================
    # SECTION 1: EXECUTIVE SUMMARY
    # ==========================
    style_heading(doc.add_paragraph(), "1. Executive Summary", 16)
    add_body_paragraph(
        "The AI Multilingual Messenger is an end-to-end real-time messaging application designed to dissolve language "
        "barriers in mobile and digital communication. While standard chat apps force users to manually copy foreign text, "
        "switch to external translation tools, and paste translations back into chat, this project integrates automatic, "
        "context-aware AI translation directly into the real-time message stream for both text and voice notes."
    )
    add_body_paragraph(
        "The application has been engineered across three cohesive phases: Phase 1 established the Supabase authentication, "
        "profiles with preferred language choices, dark/light themes, and Groq AI text translation; Phase 2 introduced "
        "username-based friendship requests, the 3-tab home navigation (Chats, Friends, Profile), Supabase Realtime 1-on-1 "
        "messaging, image sharing with strict 1 MB validation, and in-bubble voice recording up to 60 seconds; Phase 3 completed "
        "the suite with multimodal AI voice translation (Gemini 3.1 Flash-Lite), in-chat message search, in-app notification "
        "banners, and real-time message delivery/seen checkmarks."
    )
    add_body_paragraph(
        "All code is implemented in simple, human-readable Flutter following plain Provider state management without "
        "over-engineering, passing all static code analyses (0 issues) and automated widget test suites."
    )

    # ==========================
    # SECTION 2: ARCHITECTURE & MESSAGE LIFECYCLES
    # ==========================
    style_heading(doc.add_paragraph(), "2. Architecture & Message Lifecycles", 16)
    add_body_paragraph(
        "The architecture maintains strict decoupling between user data operations and AI translation workloads, "
        "ensuring that network delays or AI rate limits never block message delivery."
    )
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
        "Sender selects an image via the image_picker package. The app validates the byte length against AppConstants.maxImageSizeBytes (1,048,576 bytes). "
        "Oversized files are immediately rejected with an explanatory SnackBar. Valid images are uploaded to the private 'chat-images' "
        "Supabase Storage bucket, and a message of type 'image' containing the file path is inserted. Recipients generate a secure "
        "signed URL to render the image in the bubble, with tap-to-expand full-screen zoom.",
        bold_prefix="• Image Sharing Pipeline: "
    )
    add_body_paragraph(
        "Sender taps the microphone icon to begin audio recording (Opus WebM on browser platforms, AAC M4A on mobile). "
        "A live timer counts up to 60 seconds (AppConstants.maxVoiceDurationSeconds) with auto-stop cap. The audio file is uploaded to "
        "the private 'chat-voice' bucket, and the recipient client calls FastAPI `POST /translate/voice`. Google Gemini 3.1 Flash-Lite "
        "transcribes the audio verbatim, detects the language (counting Roman Urdu as Urdu), and translates the speech into the recipient's "
        "preferred language in a single inference call. The voice bubble reactively displays the translated transcript with a toggle button.",
        bold_prefix="• Voice Note & AI Translation Pipeline: "
    )

    # ==========================
    # SECTION 3: DELIVERABLES CHECKLIST
    # ==========================
    style_heading(doc.add_paragraph(), "3. Final Project Deliverables Checklist", 16)
    checklist_items = [
        ("Supabase Auth & Session Persistence", "Completed", "Email/password signup, login, auto-restore session on restart, and sign out"),
        ("User Onboarding & Language Picker", "Completed", "Selection of primary language (10 supported languages) saved to profiles table"),
        ("Friend Search by Username", "Completed", "Exact @username search in Supabase with self-add and duplicate request prevention"),
        ("Send, Accept & Reject Requests", "Completed", "State management in FriendsProvider with pending incoming/outgoing filtering"),
        ("3-Tab Navigation Bar", "Completed", "Material 3 NavigationBar on HomeScreen hosting Chats, Friends, and Profile tabs"),
        ("Realtime 1-on-1 Chat Screen", "Completed", "Active chat UI with auto-scrolling ListView and Supabase Realtime channel listener"),
        ("AI Text Translation Engine", "Completed", "FastAPI /translate/text using Groq (openai/gpt-oss-120b) with Roman Urdu support"),
        ("Show Original / Translated Toggle", "Completed", "message_bubble.dart displays 'Translated' badge and interactive toggle link"),
        ("Translation Cache & Fallback", "Completed", "Checks database cache before calling AI; falls back to original text on any failure"),
        ("Image Sharing (up to 1 MB)", "Completed", "image_picker integration, strict 1 MB file size validation, and full-screen viewer"),
        ("Voice Note Recording (max 60s)", "Completed", "audio_service.dart using record 7.x, live timer bar, and 60-second auto-stop"),
        ("Voice Note In-Bubble Playback", "Completed", "voice_message_bubble.dart using audioplayers 6.x with progress indicator"),
        ("AI Voice Translation & Transcript", "Completed", "Gemini 3.1 Flash-Lite multimodal translation displaying transcript in bubble"),
        ("In-Chat Message Search Screen", "Completed", "Instant search filtering across text, translation, voice transcripts, and photos"),
        ("In-App Notification Banner", "Completed", "Top overlay banner for incoming messages with sender preview and 1-tap navigation"),
        ("Message Delivery & Seen Status Ticks", "Completed", "Realtime double-ticks: subtle gray for delivered/unseen, bright blue for seen"),
        ("Material 3 Light & Dark Mode", "Completed", "Dynamic theme toggle with persisted user preference across sessions"),
        ("Code Quality & Static Analysis", "Completed", "flutter analyze completed with 0 errors/0 warnings; flutter test passed"),
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
    # SECTION 4: IMPLEMENTATION DETAILS & VISUAL EVIDENCE
    # ==========================
    style_heading(doc.add_paragraph(), "4. Implementation Details & Visual Evidence", 16)

    # 4.1 Friendship & Social Layer
    style_heading(doc.add_paragraph(), "4.1 Friendship System & Request Management", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "The social graph is managed by the friendships table and exposed via FriendsProvider. Users can look up friends "
        "by their exact unique username. Pending friend requests appear in dedicated cards with one-tap Accept and Reject buttons. "
        "Accepted friendships immediately unlock one-to-one real-time messaging."
    )
    add_screenshot_box(
        "1",
        "Friends Tab & Send Friend Request",
        "The Friends tab showing the username search input bar, existing friends list with preferred language tags, and empty state.",
        "Open the app, switch to the Friends tab, enter a username in the '@username' field, and take a screenshot."
    )
    add_screenshot_box(
        "2",
        "Pending Friend Requests (Accept / Reject)",
        "A user receiving a friend request showing the requester's avatar, username, and green Accept / red Reject buttons.",
        "Log in as user B after user A sends a request. Capture the 'Friend Requests (1)' section with the action buttons."
    )

    # 4.2 Home Screen & 3-Tab Architecture
    style_heading(doc.add_paragraph(), "4.2 Home Screen Navigation (Chats, Friends, Profile)", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "HomeScreen implements an IndexedStack controlled by a modern Material 3 NavigationBar. "
        "The Chats tab displays active conversations with friends, the Friends tab manages the social network, "
        "and the Profile tab provides user configuration without nesting redundant AppBars."
    )
    add_screenshot_box(
        "3",
        "Chats Tab (Active Conversations List)",
        "The primary landing tab displaying list of friends available for chat, their preferred languages, and navigation arrows.",
        "On the Home screen, select the Chats tab and take a screenshot showing the list of available conversations."
    )

    # 4.3 Realtime 1-on-1 Chat Screen
    style_heading(doc.add_paragraph(), "4.3 Realtime 1-on-1 Chat Screen & Message Flow", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "ChatScreen establishes a direct Supabase Realtime channel subscription upon entry. When either user sends a message, "
        "it immediately streams to the other party's phone without requiring manual pull-to-refresh or polling. "
        "Sent messages align to the right in the primary teal theme; received messages align to the left in surface gray."
    )
    add_screenshot_box(
        "4",
        "1-on-1 Realtime Chat Conversation",
        "Active chat view displaying message bubbles exchanged in real time between two connected users.",
        "Open a chat conversation with a friend and capture the messages exchanged in the chat screen."
    )

    # 4.4 Automated Translation & 'Show Original' Toggle
    style_heading(doc.add_paragraph(), "4.4 Automated Translation & 'Show Original' Toggle", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "When a text message arrives, translation_service.dart checks the database cache and invokes the FastAPI backend. "
        "The message renders in the recipient's preferred language with a small 'Translated' badge. Tapping 'Show original' "
        "instantly toggles the display back to the sender's exact original text (e.g., Roman Urdu 'mera naam Ali hai'), "
        "and tapping 'Show translated' returns to the translated version ('My name is Ali')."
    )
    add_screenshot_box(
        "5",
        "Translated Message with 'Show Original' Toggle",
        "Message bubble displaying translated text alongside the 'Translated' badge and 'Show original' interactive link.",
        "Send a message from an Urdu account to an English account. Take a screenshot showing the translated text and the toggle."
    )

    # 4.5 Image Sharing & 1 MB Size Limit Enforcement
    style_heading(doc.add_paragraph(), "4.5 Image Sharing & 1 MB Size Limit Enforcement", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "Users can attach images from their photo gallery. The client verifies the exact file size prior to network transfer. "
        "If the image exceeds 1,048,576 bytes, upload is immediately halted and an alert SnackBar is displayed. Valid images "
        "are uploaded to the private 'chat-images' bucket and rendered inside the bubble with full-screen zoom support."
    )
    add_screenshot_box(
        "6",
        "Image Attachment Bubble in Chat",
        "Sent image rendered cleanly inside the chat bubble with rounded corners and loading placeholder.",
        "Select and send an image from gallery under 1 MB. Capture the image bubble in the chat view."
    )
    add_screenshot_box(
        "7",
        "Full-Screen Interactive ImageViewer",
        "InteractiveViewer modal displaying the full-resolution image with pinch-to-zoom and pan gestures.",
        "Tap on an image inside a chat bubble to open the full-screen view and take a screenshot."
    )

    # 4.6 Voice Note Recording & Playback
    style_heading(doc.add_paragraph(), "4.6 Voice Note Recording & Playback (60s Cap)", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "Voice notes are recorded using the record package (Opus WebM on web browsers, AAC M4A on mobile). Tapping the mic "
        "icon switches the input bar into a live recording banner showing elapsed time. The recorder strictly auto-stops at 60 seconds. "
        "Recorded audio uploads to the 'chat-voice' bucket, and the VoiceMessageBubble provides responsive play/pause, "
        "a visual progress bar, and duration counters."
    )
    add_screenshot_box(
        "8",
        "Live Voice Recording Banner (with Timer)",
        "The active recording banner at the bottom of the chat screen showing 'Recording: Xs / 60s' and 'Stop & Send'.",
        "Tap the microphone icon in the chat input bar and capture the screen while recording is actively counting."
    )
    add_screenshot_box(
        "9",
        "Voice Note Bubble with Playback Controls",
        "A sent or received voice note bubble showing the play button, progress bar, and timestamp.",
        "Send a voice note and take a screenshot of the rendered voice bubble in the chat conversation."
    )

    # 4.7 AI Voice Translation & Transcript Display
    style_heading(doc.add_paragraph(), "4.7 AI Voice Translation & Transcript Display", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "When an incoming voice note is received, the client invokes FastAPI `POST /translate/voice`. Google Gemini 3.1 Flash-Lite "
        "transcribes the spoken audio, detects the language, and translates the speech into the recipient's language in a single "
        "inference call. The VoiceMessageBubble reactively renders the translated transcript directly underneath the playback controls "
        "with an interactive 'Show original' toggle link."
    )
    add_screenshot_box(
        "10",
        "AI Voice Translation with Transcript & Toggle",
        "A voice note bubble displaying the audio playback controls, the translated speech transcript, and 'Show original' toggle.",
        "Send a voice note in a foreign language. On the recipient device, capture the voice bubble showing the English transcript."
    )

    # 4.8 In-Chat Message Search Screen
    style_heading(doc.add_paragraph(), "4.8 In-Chat Message Search Screen", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "A dedicated SearchScreen enables real-time search within any conversation thread. The search bar filters instantly "
        "across original text content, translated text, voice note speech transcripts, and photo attachment queries. Selecting "
        "any search result immediately returns to the chat and smoothly auto-scrolls directly to that targeted message."
    )
    add_screenshot_box(
        "11",
        "In-Chat Search Screen with Filtered Results",
        "SearchScreen displaying real-time query matches across text messages, voice transcripts, and photos with sender labels.",
        "Tap the search icon in the chat AppBar. Type a search query and capture the filtered results list."
    )

    # 4.9 In-App Notification Banner & Delivery Ticks
    style_heading(doc.add_paragraph(), "4.9 In-App Notification Banner & Delivery Status Ticks", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "When an incoming message arrives from a friend whose chat is not currently open, an animated overlay banner slides down "
        "from the top of the screen displaying the sender's avatar, name, and message preview. Tapping the banner immediately opens "
        "the chat. Additionally, sent bubbles display real-time checkmarks: subtle gray double-ticks (✓✓) when delivered/unseen, and "
        "bright cyan-blue double-ticks (✓✓) as soon as the recipient opens the conversation."
    )
    add_screenshot_box(
        "12",
        "In-App Top Notification Banner",
        "Animated top banner appearing on the Chats or Friends tab displaying sender avatar, name, and short message preview.",
        "Leave user B on the Friends tab, send a message from user A, and capture the top notification banner."
    )
    add_screenshot_box(
        "13",
        "Seen Status Indicators (Blue Double-Ticks)",
        "Chat bubble displaying the blue double-checkmarks next to the timestamp indicating the message has been seen.",
        "Capture a sent message bubble where the checkmarks have turned cyan-blue after the recipient viewed the chat."
    )

    # 4.10 Cloud Storage & Database Architecture
    style_heading(doc.add_paragraph(), "4.10 Supabase Cloud Storage & Database Evidence", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "All media files and translated records are verified in the Supabase Cloud backend. Storage buckets enforce "
        "privacy, and database rows in 'messages' and 'translations' reflect real chat history."
    )
    add_screenshot_box(
        "14",
        "Supabase Storage Buckets ('chat-images' and 'chat-voice')",
        "Supabase Storage dashboard showing the two private buckets containing uploaded user files.",
        "Open Supabase Dashboard -> Storage. Take a screenshot showing 'chat-images' and 'chat-voice' buckets."
    )
    add_screenshot_box(
        "15",
        "Supabase Table Editor ('messages' & 'translations')",
        "Supabase Table Editor showing rows for text, image, and voice messages alongside cached translations.",
        "Open Supabase Dashboard -> Table Editor -> 'messages' (and 'translations') to show the inserted records."
    )

    # 4.11 Material 3 Dark Theme Polish
    style_heading(doc.add_paragraph(), "4.11 Material 3 Dark Theme Polish", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "The application provides full support for Material Design 3 dark mode with high-contrast surfaces, readable text, "
        "and consistent bubble styling across all screens and dialogs."
    )
    add_screenshot_box(
        "16",
        "Material 3 Dark Mode Chat Screen",
        "The chat interface operating in Dark Mode with dark surface backgrounds, teal sent bubbles, and light gray text.",
        "Go to the Profile tab, toggle Dark Mode ON, enter a chat, and capture the dark theme conversation."
    )

    # ==========================
    # SECTION 5: GROUP CONTRIBUTIONS & INSTRUCTOR PRESENTATION
    # ==========================
    style_heading(doc.add_paragraph(), "5. Group Contributions & Presentation Guide", 16)
    add_body_paragraph(
        "The project was executed through collaborative teamwork across the frontend, backend, database, and AI pipelines:"
    )

    contrib_headers = ["Group Member", "Roll Number", "Key Contributions & Ownership"]
    contrib_rows = [
        ["Rao Hamza Tariq", "CSC-24F-042", "Full-Stack Lead: Supabase Architecture, FastAPI AI Gateway, Gemini Voice Engine & GitHub Actions CI/CD."],
        ["Imtiaz Maqbool", "SCS-24F-003", "Frontend Lead: Real-Time Chat Screen, Message Bubbles, In-Bubble Audio Player & Codec Adaptation."],
        ["Fahad Yaseen", "CSC-25S-201", "UI/UX & Navigation: 3-Tab Home Shell, Material 3 Light/Dark ThemeProvider & Onboarding Flows."],
        ["Muhammad Saad", "CSC-24F-025", "Social Graph & Search: Friendship State Machine, SearchScreen Filtering & Media Viewer."],
        ["Shahmeer Baqai", "CSC-24F-027", "Notification & Status Systems: In-App Top Notification Banner, Delivery & Seen Ticks, and QA Testing."]
    ]

    t_contrib = doc.add_table(rows=len(contrib_rows) + 1, cols=3)
    t_contrib.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(contrib_headers):
        cell = t_contrib.cell(0, j)
        tcPr = cell._tc.get_or_add_tcPr()
        tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="007A87"/>'))
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.name = "Calibri"

    for i, (mem, roll, con) in enumerate(contrib_rows):
        r_cells = t_contrib.rows[i + 1].cells
        r_cells[0].width = Inches(1.8)
        r_cells[1].width = Inches(1.3)
        r_cells[2].width = Inches(3.4)
        r_cells[0].paragraphs[0].add_run(mem).font.size = Pt(9.5)
        r_cells[1].paragraphs[0].add_run(roll).font.size = Pt(9.5)
        r_cells[2].paragraphs[0].add_run(con).font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    add_body_paragraph(
        "1. Slide 1 (Title & Problem): Introduce the group members and articulate the problem — manual translation in chat is slow and breaks for voice.\n"
        "2. Slide 2 (Architecture): Walk through the 3-tier architecture (Flutter + FastAPI + Supabase + Gemini/Groq).\n"
        "3. Live Demo 1 (Text AI): User A sends Urdu text ('Aap kaise hain?'); User B receives English ('How are you?') and toggles 'Show original'.\n"
        "4. Live Demo 2 (Voice AI): User A records a voice note; User B plays it and shows the automatically generated English transcript.\n"
        "5. Live Demo 3 (Search & Ticks): Tap search icon, filter messages, and point out the blue double-ticks indicating seen status.\n"
        "6. Live Demo 4 (Notification Banner): Send a message while User B is on the Friends tab; show the top banner and jump directly into chat.",
        bold_prefix="Recommended Presentation Script for Instructor: "
    )

    # Save to file
    output_filename = "AI_Multilingual_Messenger_Final_Report.docx"
    doc.save(output_filename)
    print(f"Final Project Report successfully created at {output_filename}")

    # Also try to update the original filename if not currently open in Word
    try:
        doc.save("Final_Project_Report_AI_Multilingual_Messenger.docx")
        print("Also updated Final_Project_Report_AI_Multilingual_Messenger.docx")
    except Exception:
        pass

if __name__ == "__main__":
    create_final_report()
