import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_phase1_document():
    doc = docx.Document()

    # Page Margins: 1 inch all around
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Color definitions
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
    r_sub = sub_p.add_run("Phase 1 Deliverables & Technical Architecture Report")
    r_sub.font.size = Pt(14)
    r_sub.font.name = "Calibri"
    r_sub.font.color.rgb = SECONDARY_COLOR

    # Meta box
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Course / Project:", "Mobile Application Development / Capstone Project"),
        ("Student Name:", "[ Insert Your Name Here ]"),
        ("Date & Status:", "October 2026 — Phase 1 Completed & Verified"),
        ("Technology Stack:", "Flutter 3.x, Supabase (PostgreSQL/Auth), FastAPI (Python), Groq AI"),
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
        "The AI Multilingual Messenger is a modern 1-to-1 cross-language mobile chat application built with Flutter, "
        "Supabase, and a specialized FastAPI backend. Its purpose is to allow individuals who speak different languages to communicate "
        "effortlessly in real time, with automatic language detection and translation—featuring dedicated support for Roman Urdu "
        "and 10 global languages."
    )
    add_body_paragraph(
        "This document presents the complete implementation and verification results for Phase 1 (Requirements, Auth, "
        "Profile Management, and Translation Backend). All criteria specified in the project roadmap have been fully built, "
        "tested, and validated against the project standards."
    )

    # ==========================
    # SECTION 2: SYSTEM ARCHITECTURE
    # ==========================
    style_heading(doc.add_paragraph(), "2. System Architecture & Workflow", 16)
    add_body_paragraph(
        "The system follows a decoupled, secure client-server architecture designed for high responsiveness, privacy, and low latency:"
    )
    add_body_paragraph(
        "Direct connection to Supabase Auth, PostgreSQL, Realtime channels, and Storage buckets. "
        "State management utilizes plain Provider with ChangeNotifier for transparent, human-readable state flows.",
        bold_prefix="• Frontend Client (Flutter): "
    )
    add_body_paragraph(
        "Lightweight Python service deployed on Vercel dedicated exclusively to translation tasks. "
        "It validates Supabase JWTs, applies per-user rate limits, caches completed translations, and calls Groq AI.",
        bold_prefix="• Translation Backend (FastAPI): "
    )
    add_body_paragraph(
        "Employs model openai/gpt-oss-120b with custom system prompting to detect languages, "
        "translate accurately, and naturally parse Roman Urdu without altering emojis or conversational tone.",
        bold_prefix="• AI Translation Engine (Groq): "
    )
    add_body_paragraph(
        "AI keys and service role credentials reside strictly in backend environment variables and are never bundled inside the mobile client.",
        bold_prefix="• Key Security Principle: "
    )

    # ==========================
    # SECTION 3: PHASE 1 CHECKLIST
    # ==========================
    style_heading(doc.add_paragraph(), "3. Phase 1 Deliverables Checklist", 16)
    checklist_items = [
        ("Flutter Project & Folder Scaffolding", "Completed", "Organized into core/, models/, providers/, services/, screens/, widgets/"),
        ("Database Schema & Migrations", "Completed", "database/migrations/ containing 01_initial_schema, 02_disable_rls_dev, 03_enable_rls"),
        ("Material 3 Light & Dark Themes", "Completed", "Calm teal seed (#007A87) with SharedPreferences persistence"),
        ("Splash Screen with Session Routing", "Completed", "Auto-routes to LoginScreen, OnboardingScreen, or HomeScreen"),
        ("Sign Up & Login Authentication", "Completed", "Supabase Auth with lowercase username and form validation"),
        ("Language Onboarding Screen", "Completed", "Selection from 10 supported languages, saved to user profile"),
        ("Profile Management Screen", "Completed", "Edit display name, change preferred language, dark mode toggle, logout"),
        ("FastAPI Translation Server", "Completed", "Live on port 8000 with /health, JWT security, and rate limiting"),
        ("AI Text Translation (Groq)", "Completed", "Model openai/gpt-oss-120b tested with Roman Urdu ('mera naam Ali hai')"),
        ("Testing & Quality Assurance", "Completed", "flutter analyze (0 issues) and flutter test (smoke test passed)"),
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

    # 4.1 Database
    style_heading(doc.add_paragraph(), "4.1 Database Schema & Migration Architecture", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "All database definitions have been formalized in a dedicated database/migrations/ directory. "
        "The schema includes the profiles table (referencing auth.users.id), friendships table (one-to-one friend pairs), "
        "messages table (supporting text, 1MB images, and 60-second voice notes), and translations table with a unique "
        "caching constraint (message_id, target_language). An automatic handle_new_user() trigger creates profile rows on registration."
    )
    add_screenshot_box(
        "1",
        "Supabase Table Editor (Database Tables)",
        "Shows the created tables (profiles, friendships, messages, translations) in your Supabase dashboard.",
        "Open Supabase Dashboard -> Table Editor. Take a screenshot showing the list of tables on the left and the 'profiles' table data."
    )
    add_screenshot_box(
        "2",
        "Supabase SQL Editor (Migration Execution)",
        "Shows successful execution of database/migrations/01_initial_schema.sql in the Supabase SQL editor.",
        "Open Supabase Dashboard -> SQL Editor. Open your migration query and capture the 'Success. No rows returned' banner."
    )

    # 4.2 Frontend Architecture & Theming
    style_heading(doc.add_paragraph(), "4.2 Frontend UI & Material 3 Theming", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "The Flutter client is built using Material 3 specifications with a calm teal primary seed (Color(0xFF007A87)). "
        "The ThemeProvider cleanly toggles between Light and Dark themes, with user choices saved persistently using SharedPreferences."
    )
    add_screenshot_box(
        "3",
        "Light Mode & Dark Mode Comparison",
        "Side-by-side or consecutive screenshots demonstrating the app running in Light theme and Dark theme.",
        "Launch the Flutter app in Edge/Chrome, take a screenshot in Light Mode, toggle Dark Mode from the Profile screen, and capture Dark Mode."
    )

    # 4.3 Authentication Flow
    style_heading(doc.add_paragraph(), "4.3 User Authentication & Onboarding Flow", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "The application flow starts with an automated Splash screen that verifies active Supabase sessions. "
        "Unauthenticated users navigate to Login or Sign Up. Sign up creates the auth user with a unique lowercase username, "
        "automatically routing them to the Language Setup onboarding screen to pick from 10 supported languages."
    )
    add_screenshot_box(
        "4",
        "Splash Screen",
        "The initial launch screen featuring app branding, icon, and loading indicator during session verification.",
        "Launch the Flutter app and capture the initial splash screen before transition."
    )
    add_screenshot_box(
        "5",
        "Sign Up Screen (Create Account)",
        "The registration screen with username, email, and password form fields.",
        "Navigate to the Create Account screen in the app and capture the form with inputs entered."
    )
    add_screenshot_box(
        "6",
        "Login Screen (Welcome Back)",
        "The user sign-in screen with email, password, and sign-up redirection link.",
        "Open the Login screen in the app and take a screenshot."
    )
    add_screenshot_box(
        "7",
        "Language Setup / Onboarding Screen",
        "The list of 10 supported languages where the user picks their preferred language upon registration.",
        "Complete sign up or open Onboarding to capture the radio list of supported languages (English, Urdu, Arabic, etc.)."
    )

    # 4.4 Profile Management
    style_heading(doc.add_paragraph(), "4.4 Profile & Preferences Management", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "The Home and Profile screens allow users to review their current configuration. Users can update their display name, "
        "change their preferred language via a dropdown, toggle dark mode, and log out."
    )
    add_screenshot_box(
        "8",
        "Home Screen (Authenticated Landing)",
        "The landing screen showing the welcome message, username, current preferred language, and navigation icons.",
        "Capture the Home screen after successfully logging in and completing onboarding."
    )
    add_screenshot_box(
        "9",
        "Profile Screen (Edit Details & Preferences)",
        "The profile view showing display name editing, preferred language selector, dark mode switch, and logout.",
        "From Home, tap the Profile icon and capture the full profile screen."
    )

    # 4.5 Backend API & Groq AI
    style_heading(doc.add_paragraph(), "4.5 FastAPI Backend & Groq AI Translation", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "The translation service is implemented in FastAPI (backend/main.py). It exposes GET /health and POST /translate/text. "
        "It uses Groq's openai/gpt-oss-120b model with custom Roman Urdu prompting. Translations are cached in the database "
        "so identical messages are never translated twice for the same target language."
    )
    add_screenshot_box(
        "10",
        "FastAPI Server Running in Terminal",
        "Terminal output showing uvicorn running the FastAPI backend on port 8000.",
        "Take a screenshot of your backend terminal running: 'uv run python -m uvicorn main:app --reload --port 8000'."
    )
    add_screenshot_box(
        "11",
        "Interactive API Documentation (Swagger UI)",
        "The Swagger UI at http://localhost:8000/docs displaying all available endpoints.",
        "Open http://localhost:8000/docs in your web browser and take a screenshot of the endpoint list."
    )
    add_screenshot_box(
        "12",
        "Roman Urdu Translation Test Output",
        "Terminal or API test showing translation of 'mera naam Ali hai' to 'My name is Ali' with detected language 'ur-roman'.",
        "Run the test command in PowerShell/terminal and capture the JSON output: {'detected_language': 'ur-roman', 'translated_text': 'My name is Ali'}."
    )

    # 4.6 Verification & Testing
    style_heading(doc.add_paragraph(), "4.6 Automated Testing & Code Quality Assurance", 13, SECONDARY_COLOR)
    add_body_paragraph(
        "Code health was verified using Flutter's native static analyzer and test suite. The project complies with "
        "flutter_lints with zero warnings or errors. Automated widget smoke tests pass cleanly."
    )
    add_screenshot_box(
        "13",
        "Flutter Analyze & Flutter Test Terminal Output",
        "Terminal output displaying 'No issues found!' from flutter analyze and 'All tests passed!' from flutter test.",
        "Run 'flutter analyze' and 'flutter test' in your terminal and take a screenshot of the successful completion messages."
    )

    # ==========================
    # SECTION 5: CONCLUSION & PHASE 2 ROADMAP
    # ==========================
    style_heading(doc.add_paragraph(), "5. Conclusion & Transition to Phase 2", 16)
    add_body_paragraph(
        "Phase 1 has established an end-to-end foundation meeting all requirements outlined in the course project schedule. "
        "The authentication layer, database architecture, UI theming, and translation backend are fully functional."
    )
    add_body_paragraph(
        "Phase 2 will introduce interactive messaging capabilities:",
        bold_prefix="Phase 2 Roadmap: "
    )
    add_body_paragraph("• Friend search by username with send, accept, and reject actions.")
    add_body_paragraph("• Real-time 1-on-1 chat powered by Supabase Realtime channels.")
    add_body_paragraph("• Image sharing with strict 1 MB file size enforcement.")
    add_body_paragraph("• Live text translation in chat bubbles with 'Show Original' toggle.")
    add_body_paragraph("• Voice note recording (up to 60 seconds) with audio playback.")

    # Save to file
    output_filename = "Phase_1_Documentation_AI_Multilingual_Messenger.docx"
    doc.save(output_filename)
    print(f"Document successfully created at {output_filename}")

if __name__ == "__main__":
    create_phase1_document()
