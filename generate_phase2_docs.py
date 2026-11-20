import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_phase2_document():
    doc = docx.Document()

    # Page Margins: 1 inch all around
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Color definitions (matching Phase 1 style)
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

        # Style cell background and border
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
    # COVER / HEADER
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
    r_sub = sub_p.add_run("Phase 2 Deliverables & Technical Architecture Report")
    r_sub.font.size = Pt(14)
    r_sub.font.name = "Calibri"
    r_sub.font.color.rgb = SECONDARY_COLOR

    # Meta box
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Course / Project:", "Mobile Application Development / Capstone Project"),
        ("Student Name:", "[ Insert Your Name Here ]"),
        ("Date & Status:", "November 2026 — Phase 2 Completed & Verified"),
        ("Technology Stack:", "Flutter 3.x, Supabase (PostgreSQL/Auth/Realtime/Storage), FastAPI, Groq AI, Audio Record & Playback"),
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
        rv.font.size = Pt(10)
        rv.font.name = "Calibri"

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ==========================
    # SECTION 1: EXECUTIVE SUMMARY
    # ==========================
    style_heading(doc.add_paragraph(), "1. Executive Summary", 16)
    add_body_paragraph(
        "Phase 2 of the AI Multilingual Messenger project shifts the application from initial authentication and "
        "infrastructure into a feature-complete, interactive real-time messaging platform. While Phase 1 established "
        "the database schema, user onboarding, profile preferences, and backend Groq AI translation service, Phase 2 "
        "connects all layers to deliver seamless 1-on-1 multilingual communication between friends."
    )
    add_body_paragraph(
        "During this phase, we implemented: (1) an end-to-end friendship and request system, (2) a clean 3-tab Home "
        "screen navigation layout (Chats, Friends, Profile), (3) real-time message exchange powered by Supabase Realtime, "
        "(4) automatic background text translation with Roman Urdu detection and interactive 'Show original' toggles, "
        "(5) secure image sharing with a strictly enforced 1 MB size limit, and (6) voice note recording up to 60 seconds "
        "with an auto-stop cap and in-bubble playback controls."
    )
    add_body_paragraph(
        "All code is implemented in simple, human-readable Flutter following plain Provider state management without "
        "over-engineering, passing all static code analyses (0 issues) and automated widget test suites."
    )

    # ==========================
    # SECTION 2: SYSTEM ARCHITECTURE & MESSAGE PIPELINE
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
        "Sender taps the microphone icon to begin AAC recording. A live timer counts up to 60 seconds (AppConstants.maxVoiceDurationSeconds). "
        "If 60 seconds are reached, the recorder automatically finalizes and sends the audio. The file is uploaded to the private "
        "'chat-voice' bucket, and a message of type 'voice' is inserted with its recorded duration. The recipient plays the audio "
        "directly using the custom VoiceMessageBubble widget.",
        bold_prefix="• Voice Note Pipeline: "
    )

    # ==========================
    # SECTION 3: PHASE 2 DELIVERABLES CHECKLIST
    # ==========================
    style_heading(doc.add_paragraph(), "3. Phase 2 Deliverables Checklist", 16)
    checklist_items = [
        ("Friend Search by Username", "Completed", "Exact username search in Supabase with self-add and duplicate request prevention"),
        ("Send, Accept & Reject Requests", "Completed", "State management in FriendsProvider with pending incoming/outgoing filtering"),
        ("3-Tab Navigation Bar", "Completed", "Material 3 NavigationBar on HomeScreen hosting Chats, Friends, and Profile tabs"),
        ("Realtime 1-on-1 Chat Screen", "Completed", "Active chat UI with auto-scrolling ListView and Supabase Realtime channel listener"),
        ("FastAPI Translation Client", "Completed", "translation_service.dart calling POST /translate/text with Bearer JWT"),
        ("Show Original / Translated Toggle", "Completed", "message_bubble.dart displays 'Translated' badge and interactive toggle link"),
        ("Translation Cache & Fallback", "Completed", "Checks database cache before calling AI; falls back to original text on any failure"),
        ("Image Sharing (up to 1 MB)", "Completed", "image_picker integration, strict 1 MB file size validation, and full-screen viewer"),
        ("Voice Note Recording (max 60s)", "Completed", "audio_service.dart using record 7.x, live timer bar, and 60-second auto-stop"),
        ("Voice Note In-Bubble Playback", "Completed", "voice_message_bubble.dart using audioplayers 6.x with progress indicator"),
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
    # SECTION 4: DETAILED IMPLEMENTATION & EVIDENCE
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
        "A live chat screen showing the friend's name and preferred language in the top AppBar, followed by sent and received message bubbles.",
        "Open a chat between two registered test users, send several messages back and forth, and capture the conversation thread."
    )

    # 4.4 Automated Live Translation & Show Original
    style_heading(doc.add_paragraph(), "4.4 Automated Translation & 'Show Original' Toggle", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "When a text message arrives, translation_service.dart checks the database cache and invokes the FastAPI backend. "
        "The message renders in the recipient's preferred language with a small 'Translated' badge. Tapping 'Show original' "
        "instantly toggles the display back to the sender's exact original text (e.g., Roman Urdu 'mera naam Ali hai'), "
        "and tapping 'Show translated' returns to the translated version ('My name is Ali')."
    )
    add_screenshot_box(
        "5",
        "Translated Message Bubble with 'Show original' Link",
        "A received message displayed in translated English with the 'Translated' badge and underline 'Show original' action link.",
        "Send a Roman Urdu or Urdu message from Phone 1 to Phone 2 (set to English). Capture the translated bubble on Phone 2."
    )
    add_screenshot_box(
        "6",
        "Original Message View After Toggling",
        "The same message bubble after tapping 'Show original', displaying the original raw text and a 'Show translated' link.",
        "Tap 'Show original' on the translated bubble and capture the updated view showing the original text."
    )

    # 4.5 Image Sharing & 1 MB Validation
    style_heading(doc.add_paragraph(), "4.5 Image Sharing & 1 MB Size Limit Enforcement", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "Users can attach images from their photo gallery. The client verifies the exact file size prior to network transfer. "
        "If the image exceeds 1,048,576 bytes, upload is immediately halted and an alert SnackBar is displayed. Valid images "
        "are uploaded to the private 'chat-images' bucket and render inside the bubble with full-screen zoom support."
    )
    add_screenshot_box(
        "7",
        "Image Message Bubble in Chat Thread",
        "A message bubble containing an image thumbnail preview with rounded corners and timestamp.",
        "Send an image under 1 MB in the chat. Capture the image bubble rendered in the chat stream."
    )
    add_screenshot_box(
        "8",
        "Full-Screen Image Viewer with Zoom",
        "The InteractiveViewer full-screen modal opened upon tapping an image bubble.",
        "Tap the image in the chat bubble to open full screen and take a screenshot of the viewer."
    )
    add_screenshot_box(
        "9",
        "1 MB Limit Rejection Alert",
        "The red alert SnackBar shown when selecting an image larger than 1 MB, stating the exact file size.",
        "Attempt to pick an image larger than 1 MB in the chat input and capture the resulting error SnackBar."
    )

    # 4.6 Voice Note Recording & Playback
    style_heading(doc.add_paragraph(), "4.6 Voice Note Recording & Playback (60s Cap)", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "Voice notes are recorded using the record package in AAC/M4A format. Tapping the mic icon switches the input "
        "bar into a live recording banner showing the elapsed time. The recorder strictly auto-stops at 60 seconds. "
        "Recorded audio uploads to the 'chat-voice' bucket, and the VoiceMessageBubble provides responsive play/pause, "
        "a visual progress bar, and elapsed/total duration counters."
    )
    add_screenshot_box(
        "10",
        "Live Voice Recording Banner (with Timer)",
        "The active recording banner at the bottom of the chat screen showing 'Recording: Xs / 60s' and 'Stop & Send'.",
        "Tap the microphone icon in the chat input bar and capture the screen while recording is actively counting."
    )
    add_screenshot_box(
        "11",
        "Voice Note Bubble with Playback Controls",
        "A sent or received voice note bubble showing the play button, progress bar, and timestamp.",
        "Send a voice note and take a screenshot of the rendered voice bubble in the chat conversation."
    )
    add_screenshot_box(
        "12",
        "Voice Note Audio Playback in Progress",
        "The voice note bubble actively playing audio, showing the pause button and updated progress indicator.",
        "Tap the play button on a voice note and capture the bubble while playback progress is active."
    )

    # 4.7 Cloud Storage & Database Evidence
    style_heading(doc.add_paragraph(), "4.7 Supabase Cloud Storage & Database Evidence", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "All media files and translated records are verified in the Supabase Cloud backend. Storage buckets enforce "
        "privacy, and database rows in 'messages' and 'translations' reflect real chat history."
    )
    add_screenshot_box(
        "13",
        "Supabase Storage Buckets ('chat-images' and 'chat-voice')",
        "Supabase Storage dashboard showing the two private buckets containing uploaded user files.",
        "Open Supabase Dashboard -> Storage. Take a screenshot showing 'chat-images' and 'chat-voice' buckets."
    )
    add_screenshot_box(
        "14",
        "Supabase Table Editor ('messages' & 'translations')",
        "Supabase Table Editor showing rows for text, image, and voice messages alongside cached translations.",
        "Open Supabase Dashboard -> Table Editor -> 'messages' (and 'translations') to show the inserted records."
    )

    # 4.8 Automated Testing & Static Code Analysis
    style_heading(doc.add_paragraph(), "4.8 Automated Testing & Static Code Analysis", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "Phase 2 was validated using Flutter's native analysis and test suite. The codebase complies with standard lints "
        "with zero warnings or errors. Automated widget tests confirm that providers and screens initialize correctly."
    )
    add_screenshot_box(
        "15",
        "Flutter Analyze & Flutter Test Terminal Output",
        "Terminal output displaying 'No issues found!' from flutter analyze and 'All tests passed!' from flutter test.",
        "Run 'flutter analyze' and 'flutter test' in your terminal and take a screenshot of both passing results."
    )

    # ==========================
    # SECTION 5: CONCLUSION & PHASE 3 ROADMAP
    # ==========================
    style_heading(doc.add_paragraph(), "5. Conclusion & Transition to Phase 3", 16)
    add_body_paragraph(
        "Phase 2 has successfully achieved all core communication goals. Two users can now establish a friendship, "
        "exchange real-time messages in different languages, toggle translations with high fidelity, share images with "
        "enforced size limits, and exchange voice notes capped at 60 seconds."
    )
    add_body_paragraph(
        "The project is now primed for Phase 3 (Final Phase), which will complete the application suite:",
        bold_prefix="Phase 3 Final Delivery Roadmap: "
    )
    add_body_paragraph("• AI Voice Translation: Gemini (gemini-3.1-flash-lite) transcription and translation in ONE request via POST /translate/voice.")
    add_body_paragraph("• In-Bubble Voice Transcript: Displaying translated transcripts directly under voice message players.")
    add_body_paragraph("• In-Chat Search: Searching historical messages within a chat thread via search_screen.dart.")
    add_body_paragraph("• In-App Notification Banner: Showing preview banners when incoming messages arrive from other chats.")
    add_body_paragraph("• Theme & UI Polish: Final aesthetic pass, accessibility review, and dark mode refinement.")
    add_body_paragraph("• Final Demo & Delivery: Real-world Android phone validation and capstone demo preparation.")

    # Save to file
    output_filename = "Phase_2_Documentation_AI_Multilingual_Messenger.docx"
    doc.save(output_filename)
    print(f"Document successfully created at {output_filename}")

if __name__ == "__main__":
    create_phase2_document()
