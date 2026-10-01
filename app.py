import streamlit as st
import html
import io
import textwrap
from pathlib import Path

from services.ai_service import (
    analyze_bug_report,
    generate_meeting_tickets,
    analyze_phishing_email,
)
from services.pdf_service import (
    extract_text_from_pdf,
    generate_bug_analysis_pdf,
    generate_meeting_analysis_pdf,
    generate_phishing_analysis_pdf,
)
from services.email_service import parse_eml_file


_streamlit_markdown = st.markdown
_streamlit_html = st.html


def render_markdown(body, *args, **kwargs):
    """Render indented Markdown and HTML as content, not code blocks."""

    if isinstance(body, str):
        body = textwrap.dedent(body)

        if kwargs.get("unsafe_allow_html") and "<" in body:
            return _streamlit_html(body)

    return _streamlit_markdown(body, *args, **kwargs)


st.markdown = render_markdown


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="DevSift - Sift the Noise. Surface the Insight.",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --ink: #f7f7f8;
        --muted: #a1a1aa;
        --paper: #000000;
        --panel: #111113;
        --line: #2b2b2f;
        --accent: #f7f7f8;
        --accent-soft: #1c1c20;
        --blue: #6ea8fe;
        --primary-color: #6ea8fe !important;
    }

    html,
    body,
    [class*="css"] {
        font-family: "Inter", sans-serif;
    }

    .stApp {
        background: var(--paper);
        color: var(--ink);
    }

    .main {
        background: var(--paper);
    }

    /* Defer paint and layout work for sections below the fold. */
    .hero,
    .feature-card,
    .pipeline,
    .capability-card,
    .output-card {
        content-visibility: auto;
        contain: content;
        contain-intrinsic-size: 220px;
    }

    .pipeline {
        contain-intrinsic-size: 480px;
    }

    @keyframes reveal-on-scroll {
        from {
            opacity: 0;
            transform: translateY(24px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @supports (animation-timeline: view()) {
        .feature-card,
        .pipeline,
        .capability-card,
        .output-card {
            opacity: 0;
            animation: reveal-on-scroll linear both;
            animation-timeline: view();
            animation-range: entry 0% cover 35%;
        }

        .pipeline-step {
            opacity: 0;
            animation: reveal-on-scroll linear both;
            animation-timeline: view();
            animation-range: entry 0% cover 45%;
        }
    }

    header[data-testid="stHeader"],
    [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Remove Streamlit default spacing */

    .block-container {
        padding-top: 86px;
        padding-bottom: 4rem;
        max-width: 1200px;
    }

    .top-nav {
        display: flex;
        align-items: center;
        min-height: 76px;
        margin-bottom: 0;
    }

    .top-nav-brand-wrap {
        display: flex;
        align-items: center;
        gap: 12px;
        height: 76px;
    }

    .top-nav-logo {
        width: 48px;
        height: 48px;
        object-fit: contain;
        flex: 0 0 48px;
    }

    .top-nav-brand {
        color: var(--ink);
        font-family: "Inter", sans-serif;
        font-size: 20px;
        font-weight: 700;
        letter-spacing: -0.035em;
        line-height: 1;
    }

    .top-nav-brand .brand-sift {
        color: var(--blue);
    }

    .top-nav-caption {
        margin-top: 5px;
        color: var(--muted);
        font-family: "DM Mono", monospace;
        font-size: 9px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        line-height: 1;
    }

    .st-key-top-nav-links {
        display: flex;
        justify-content: flex-end;
        align-items: center;
    }

    /* ========================================================
    TOP NAV — SMOOTH ANIMATED TABS
    ======================================================== */

    .st-key-top-nav-links {
        display: flex;
        justify-content: flex-end;
        align-items: center;
    }

    .st-key-top-nav-links .stButton > button {
        position: relative !important;
        min-height: 40px !important;
        padding: 8px 10px !important;

        background: transparent !important;
        border: 0 !important;
        border-radius: 0 !important;

        color: var(--muted) !important;
        font-size: 13px !important;
        font-weight: 600 !important;

        transition:
            color 220ms ease,
            opacity 220ms ease,
            transform 220ms ease !important;
    }

    /* Animated underline */
    .st-key-top-nav-links .stButton > button::after {
        content: "";
        position: absolute;

        left: 10px;
        right: 10px;
        bottom: 0;

        height: 2px;
        border-radius: 999px;

        background: var(--blue);

        transform: scaleX(0);
        transform-origin: center;

        opacity: 0;

        transition:
            transform 260ms cubic-bezier(0.22, 1, 0.36, 1),
            opacity 180ms ease;
    }

    /* Hover */
    .st-key-top-nav-links .stButton > button:hover {
        color: var(--ink) !important;
        opacity: 1;
    }

    /* Active tab */
    .st-key-top-nav-links .stButton > button[kind="primary"] {
        color: var(--ink) !important;
    }

    /* Animate active underline */
    .st-key-top-nav-links .stButton > button[kind="primary"]::after {
        transform: scaleX(1);
        opacity: 1;
    }

    /* Slight press feedback */
    .st-key-top-nav-links .stButton > button:active {
        transform: scale(0.97);
    }

    .block-container div[data-testid="stHorizontalBlock"]:has(.st-key-top-nav-links) {
        position: fixed !important;
        top: 0;
        left: 0;
        right: 0;
        width: 100%;
        box-sizing: border-box;
        z-index: 1000;
        background: var(--paper);
        border-bottom: 1px solid var(--line);
        padding: 0 max(1rem, calc((100vw - 1200px) / 2)) 10px;
        margin-bottom: 0;
    }

    .st-key-top-nav-links .stButton > button:hover {
        color: var(--ink) !important;
        opacity: 1;
    }

    .st-key-top-nav-links .stButton > button[kind="primary"] {
        color: var(--ink) !important;
        border-bottom-color: var(--blue) !important;
    }

    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background: #09090b;
        border-right: 1px solid var(--line);
    }

    section[data-testid="stSidebar"] > div {
        background: #09090b;
    }

    .sidebar-brand {
        padding: 10px 8px 24px 8px;
        border-bottom: 1px solid var(--line);
        margin-bottom: 24px;
    }

    .sidebar-brand-title {
        font-family: "DM Mono", monospace;
        font-size: 14px;
        font-weight: 500;
        letter-spacing: 0.08em;
        color: var(--ink);
        text-transform: uppercase;
    }

    .sidebar-brand-subtitle {
        margin-top: 7px;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.5;
    }

    .sidebar-section {
        font-family: "DM Mono", monospace;
        font-size: 11px;
        color: var(--blue);
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 0 0 8px 8px;
    }

    section[data-testid="stSidebar"] .stRadio > label {
        display: none;
    }

    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 4px;
    }

    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
        background: transparent;
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 10px 12px;
        color: var(--muted);
        transition: all 0.15s ease;
    }

    section[data-testid="stSidebar"]
    .stRadio
    div[role="radiogroup"]
    > label:hover {
        background: var(--panel);
        border-color: var(--line);
        color: var(--ink);
    }

    section[data-testid="stSidebar"]
    .stRadio
    div[role="radiogroup"]
    > label[data-checked="true"] {
        background: var(--accent-soft);
        border-color: var(--line);
        color: var(--ink);
    }

    section[data-testid="stSidebar"]
    .stRadio
    div[role="radiogroup"]
    > label
    p {
        font-size: 14px;
        margin: 0;
    }

    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        color: #52525b;
        font-family: "DM Mono", monospace;
        font-size: 10px;
        letter-spacing: 0.05em;
    }

    /* ========================================================
       PAGE HEADER
       ======================================================== */

    .page-kicker {
        font-family: "DM Mono", monospace;
        color: var(--blue);
        font-size: 11px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .page-title {
        color: var(--ink);
        font-size: 40px;
        font-weight: 700;
        line-height: 1.1;
        letter-spacing: -0.03em;
        margin: 0;
    }

    .page-subtitle {
        color: var(--muted);
        font-size: 16px;
        line-height: 1.7;
        max-width: 760px;
        margin-top: 12px;
    }

    /* Sleek typewriter animation for page headings only. */
    .page-title.typing-title {
        display: inline-block;
        width: max-content;
        max-width: 0;
        overflow: hidden;
        white-space: nowrap;
        vertical-align: bottom;
        border-right: 1px solid var(--blue);
        animation:
            title-typing 2.0s steps(var(--typing-chars), end) forwards,
            title-caret 720ms step-end infinite;
    }

    @keyframes title-typing {
        from { max-width: 0; }
        to { max-width: 100%; }
    }

    @keyframes title-caret {
        0%, 45% { border-right-color: var(--blue); }
        46%, 100% { border-right-color: transparent; }
    }

    @media (prefers-reduced-motion: reduce) {
        .page-title.typing-title {
            width: auto;
            white-space: normal;
            border-right: none;
            animation: none;
        }
    }

    .page-divider {
        height: 1px;
        background: var(--line);
        margin: 28px 0 30px 0;
    }

    /* ========================================================
       HERO
       ======================================================== */

    .hero {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 26px;
        margin: 20px 0 30px 0;
    }

    .hero-label {
        font-family: "DM Mono", monospace;
        color: var(--blue);
        font-size: 11px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .hero-title {
        color: var(--ink);
        font-size: 28px;
        font-weight: 600;
        letter-spacing: -0.02em;
        margin-bottom: 10px;
    }

    .hero-text {
        color: var(--muted);
        font-size: 15px;
        line-height: 1.7;
        max-width: 780px;
    }

    /* ========================================================
       CARDS
       ======================================================== */

    .feature-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 7px;
        padding: 20px;
        min-height: 175px;
    }

    .feature-number {
        font-family: "DM Mono", monospace;
        color: var(--blue);
        font-size: 11px;
        letter-spacing: 0.1em;
        margin-bottom: 14px;
    }

    .feature-title {
        color: var(--ink);
        font-size: 19px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .feature-text {
        color: var(--muted);
        font-size: 14px;
        line-height: 1.65;
    }

    .capability-card {
        background: #0d0d0f;
        border: 1px solid var(--line);
        border-radius: 7px;
        padding: 18px;
        min-height: 130px;
    }

    .capability-title {
        color: var(--ink);
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 7px;
    }

    .capability-text {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.6;
    }

    /* ========================================================
       PIPELINE
       ======================================================== */

    .pipeline {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 7px;
        padding: 20px;
    }

    .pipeline-step {
        background: #0d0d0f;
        border: 1px solid var(--line);
        border-radius: 5px;
        padding: 12px;
        margin-bottom: 8px;
    }

    .pipeline-step:last-child {
        margin-bottom: 0;
    }

    .pipeline-index {
        font-family: "DM Mono", monospace;
        color: var(--blue);
        font-size: 11px;
        margin-bottom: 5px;
    }

    .pipeline-title {
        color: var(--ink);
        font-size: 14px;
        font-weight: 600;
    }

    .pipeline-description {
        color: var(--muted);
        font-size: 12px;
        margin-top: 4px;
        line-height: 1.5;
    }

    /* ========================================================
       INPUTS
       ======================================================== */

    .input-label {
        font-family: "DM Mono", monospace;
        color: var(--blue);
        font-size: 11px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin: 0 0 8px 0;
    }

    .stTextArea textarea {
        background: var(--panel) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        border-radius: 6px !important;
        font-family: "Inter", sans-serif !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        outline: none !important;
    }

    /* Blue focus state — applies to all text areas */
    .stTextArea textarea:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 1px var(--blue) !important;
        outline: none !important;
    }

    /* Streamlit/BaseWeb focus wrapper */
    .stTextArea div[data-baseweb="textarea"]:focus-within {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 1px var(--blue) !important;
    }

    .stFileUploader {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 5px;
    }

    .stFileUploader section {
        background: transparent !important;
        border: none !important;
    }

    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        background: var(--accent) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 999px !important;
        font-family: "Inter", sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 10px 18px !important;
        transition: opacity 0.15s ease;
    }

    .stButton > button:hover {
        opacity: 0.85;
    }

    .stButton > button:focus {
        box-shadow: none !important;
    }

    /* ========================================================
       OUTPUT
       ======================================================== */

    .output-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 7px;
        padding: 20px;
        margin: 12px 0;
    }

    .output-label {
        font-family: "DM Mono", monospace;
        color: var(--blue);
        font-size: 11px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 7px;
    }

    .output-title {
        color: var(--ink);
        font-size: 21px;
        font-weight: 600;
        line-height: 1.35;
        margin-bottom: 10px;
    }

    .output-text {
        color: #d4d4d8;
        font-size: 14px;
        line-height: 1.65;
    }

    .mono-output {
        font-family: "DM Mono", monospace;
        color: #d4d4d8;
        font-size: 13px;
        line-height: 1.7;
    }

    .tag {
        display: inline-block;
        background: var(--accent-soft);
        border: 1px solid var(--line);
        color: var(--ink);
        border-radius: 4px;
        padding: 4px 8px;
        margin: 2px 4px 2px 0;
        font-family: "DM Mono", monospace;
        font-size: 11px;
    }

    .empty-state {
        background: var(--panel);
        border: 1px dashed var(--line);
        border-radius: 7px;
        padding: 35px;
        text-align: center;
        color: var(--muted);
        font-size: 14px;
    }

    /* ========================================================
    TABS — DEVSIFT BLUE THEME
    ======================================================== */

    /* Tab container */
    .stTabs [data-testid="stTab"] {
        color: var(--muted) !important;
        background: transparent !important;
        border: none !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    /* Active tab text */
    .stTabs [data-testid="stTab"][data-selected="true"],
    .stTabs [data-testid="stTab"][data-selected="true"] p,
    .stTabs [data-testid="stTab"][data-selected="true"] div {
        color: var(--blue) !important;
        -webkit-text-fill-color: var(--blue) !important;
    }

    /* Inactive tabs */
    .stTabs [data-testid="stTab"][data-selected="false"],
    .stTabs [data-testid="stTab"][data-selected="false"] p {
        color: var(--muted) !important;
    }

    /* Hover */
    .stTabs [data-testid="stTab"]:hover,
    .stTabs [data-testid="stTab"]:hover p {
        color: var(--ink) !important;
    }

    /* Active tab underline */
    .stTabs [data-testid="stTab"][data-selected="true"]
    .react-aria-SelectionIndicator {
        background-color: var(--blue) !important;
        height: 2px !important;
    }

    /* Tab list bottom border */
    .stTabs [role="tablist"] {
        border-bottom: 1px solid var(--line) !important;
    }

    /* ========================================================
       STREAMLIT ELEMENT CLEANUP
       ======================================================== */

    div[data-testid="stMarkdownContainer"] p {
        color: inherit;
    }

    .stAlert {
        border-radius: 6px !important;
    }

    [data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--ink) !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def render_page_header(kicker: str, title: str, subtitle: str):
    """Render a consistent page header."""

    st.markdown(
        f"""
        <div class="page-kicker">{html.escape(kicker)}</div>
        <h1
            class="page-title typing-title"
            style="--typing-chars: {len(title)};"
        >{html.escape(title)}</h1>
        <div class="page-subtitle">{html.escape(subtitle)}</div>
        <div class="page-divider"></div>
        """,
        unsafe_allow_html=True,
    )


def render_error(error: Exception, operation: str):
    """Display user-friendly errors for AI operations."""

    error_text = str(error)

    if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
        st.error(
            f"{operation} could not be completed because the AI service "
            "rate limit has been reached. Please try again later."
        )

    elif "503" in error_text or "UNAVAILABLE" in error_text:
        st.error(
            f"{operation} could not be completed because the AI service "
            "is temporarily unavailable. Please try again."
        )

    elif "404" in error_text or "NOT_FOUND" in error_text:
        st.error(
            f"{operation} could not be completed because the configured "
            "AI model is unavailable."
        )

    elif "validation" in error_text.lower():
        st.error(
            f"{operation} returned an unexpected response format. "
            "Please try again."
        )

    else:
        st.error(
            f"{operation} failed. Please check the input and try again."
        )


def select_page(page: str):
    """Switch the active page from the top navigation."""

    st.session_state.selected_page = page


def render_list(items: list[str], empty_text: str = "None identified."):
    """Render a list of output items."""

    if not items:
        st.markdown(
            f'<div class="output-text">{html.escape(empty_text)}</div>',
            unsafe_allow_html=True,
        )
        return

    for item in items:
        st.markdown(
            f"""
            <div style="
                color:#d4d4d8;
                font-size:14px;
                line-height:1.6;
                margin-bottom:8px;
            ">
                • {html.escape(item)}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_ticket(ticket, index: int):
    """Render one generated engineering ticket."""

    st.markdown(
        f"""
        <div class="output-card">

            <div class="output-label">
                TICKET {index:02d}
            </div>

            <div class="output-title">
                {html.escape(ticket.title)}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="output-label">USER STORY</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="output-card">
                <div class="output-text">
                    {html.escape(ticket.user_story)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            '<div class="output-label">PRIORITY</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="output-card">
                <span class="tag">{html.escape(ticket.priority)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="output-label">DESCRIPTION</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="output-card">
            <div class="output-text">
                {html.escape(ticket.description)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="output-label">ACCEPTANCE CRITERIA</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            render_list(
                ticket.acceptance_criteria,
                "No acceptance criteria identified.",
            )

    with col2:
        st.markdown(
            '<div class="output-label">EDGE CASES</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            render_list(
                ticket.edge_cases,
                "No edge cases identified.",
            )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="output-label">DEPENDENCIES</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            render_list(
                ticket.dependencies,
                "No dependencies identified.",
            )

    with col2:
        st.markdown(
            '<div class="output-label">OPEN QUESTIONS</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            render_list(
                ticket.open_questions,
                "No open questions identified.",
            )

    st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# TOP NAVIGATION
# ============================================================

nav_brand, nav_links = st.columns([2, 5], vertical_alignment="center")

with nav_brand:
    logo_path = Path(__file__).parent / "assets" / "devsift_logo.png"
    if logo_path.exists():
        import base64
        logo_data = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
        logo_src = f"data:image/png;base64,{logo_data}"
    else:
        logo_src = ""

    st.markdown(
        f"""
        <div class="top-nav">
            <div class="top-nav-brand-wrap">
                <img class="top-nav-logo" src="{logo_src}" alt="DevSift logo">
                <div>
                    <div class="top-nav-brand">Dev<span class="brand-sift">Sift</span></div>
                    <div class="top-nav-caption">Sift the Noise. Surface the Insight.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_links:
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "Home"

    with st.container(key="top-nav-links"):
        nav_home, nav_bug, nav_meeting, nav_phishing = st.columns(4)

        with nav_home:
            st.button(
                "Home",
                key="nav_home",
                type=(
                    "primary"
                    if st.session_state.selected_page == "Home"
                    else "secondary"
                ),
                use_container_width=True,
                on_click=select_page,
                args=("Home",),
            )

        with nav_bug:
            st.button(
                "Bug Analyzer",
                key="nav_bug",
                type=(
                    "primary"
                    if st.session_state.selected_page == "Bug Report Analyzer"
                    else "secondary"
                ),
                use_container_width=True,
                on_click=select_page,
                args=("Bug Report Analyzer",),
            )

        with nav_meeting:
            st.button(
                "Meeting Refiner",
                key="nav_meeting",
                type=(
                    "primary"
                    if st.session_state.selected_page == "Meeting-to-Ticket Refiner"
                    else "secondary"
                ),
                use_container_width=True,
                on_click=select_page,
                args=("Meeting-to-Ticket Refiner",),
            )

        with nav_phishing:
            st.button(
                "Phishing Investigator",
                key="nav_phishing",
                type=(
                    "primary"
                    if st.session_state.selected_page == "Phishing Email Investigator"
                    else "secondary"
                ),
                use_container_width=True,
                on_click=select_page,
                args=("Phishing Email Investigator",),
            )

selected_page = st.session_state.selected_page


# ============================================================
# HOME PAGE
# ============================================================

if selected_page == "Home":

    render_page_header(
        "DEVSIFT - SIFT THE NOISE. SURFACE THE INSIGHT.",
        "From messy input to engineering-ready output.",
        "Turn unstructured bug reports and meeting discussions into "
        "clear, structured, actionable engineering work.",
    )

    st.markdown(
        """
        <div class="hero">

            <div class="hero-label">
                WHAT THIS APP DOES
            </div>

            <div class="hero-title">
                Less noise. More actionable engineering work.
            </div>

            <div class="hero-text">
                Engineering information rarely arrives perfectly structured.
                This assistant takes messy requirements and turns them into
                structured engineering outputs so teams can review, refine,
                and use them faster.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # FEATURE CARDS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-number">
                    01 — BUG ANALYSIS
                </div>

                <div class="feature-title">
                    Bug Report Analyzer
                </div>

                <div class="feature-text">
                    Transform messy bug reports into structured engineering
                    tickets with severity, category, environment,
                    reproduction steps, expected behavior, actual behavior,
                    missing information, and acceptance criteria.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-number">
                    02 — REQUIREMENT REFINEMENT
                </div>

                <div class="feature-title">
                    Meeting-to-Ticket Refiner
                </div>

                <div class="feature-text">
                    Transform meeting notes and transcripts into focused
                    engineering tickets with user stories, descriptions,
                    acceptance criteria, priorities, edge cases,
                    dependencies, and open questions.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-number">
                    03 — SECURITY ANALYSIS
                </div>

                <div class="feature-title">
                    Phishing Email Investigator
                </div>

                <div class="feature-text">
                    Analyze suspicious emails for sender-origin indicators,
                    social engineering, credential harvesting, suspicious
                    URLs, header inconsistencies, and risky attachment metadata.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # WORKFLOW
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="page-kicker">
            HOW IT WORKS
        </div>

        <h2 style="
            color:#f7f7f8;
            font-size:26px;
            font-weight:600;
            margin-top:0;
            margin-bottom:16px;
        ">
            A structured path from input to output.
        </h2>
        """,
        unsafe_allow_html=True,
    )

    workflow_col1, workflow_col2 = st.columns(2)

    with workflow_col1:

        st.markdown(
            """
            <div class="pipeline">

                <div class="pipeline-step">
                    <div class="pipeline-index">01</div>
                    <div class="pipeline-title">Unstructured Input</div>
                    <div class="pipeline-description">
                        Bug reports, meeting notes, or transcripts.
                    </div>
                </div>

                <div class="pipeline-step">
                    <div class="pipeline-index">02</div>
                    <div class="pipeline-title">Prompt Engineering</div>
                    <div class="pipeline-description">
                        Specialized prompts guide the AI toward
                        engineering-specific outputs.
                    </div>
                </div>

                <div class="pipeline-step">
                    <div class="pipeline-index">03</div>
                    <div class="pipeline-title">OpenRouter AI</div>
                    <div class="pipeline-description">
                        The AI analyzes the input and generates
                        structured information.
                    </div>
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with workflow_col2:

        st.markdown(
            """
            <div class="pipeline">

                <div class="pipeline-step">
                    <div class="pipeline-index">04</div>
                    <div class="pipeline-title">Pydantic Validation</div>
                    <div class="pipeline-description">
                        AI output is validated against predefined
                        engineering schemas.
                    </div>
                </div>

                <div class="pipeline-step">
                    <div class="pipeline-index">05</div>
                    <div class="pipeline-title">Structured Output</div>
                    <div class="pipeline-description">
                        The validated result is displayed as
                        actionable engineering information.
                    </div>
                </div>

                <div class="pipeline-step">
                    <div class="pipeline-index">06</div>
                    <div class="pipeline-title">Human Review</div>
                    <div class="pipeline-description">
                        Engineers review and refine the generated
                        information before using it.
                    </div>
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # CAPABILITIES
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="page-kicker">
            BUILT FOR ENGINEERING WORKFLOWS
        </div>

        <h2 style="
            color:#f7f7f8;
            font-size:26px;
            font-weight:600;
            margin-top:0;
            margin-bottom:18px;
        ">
            Clear outputs. Less guessing. Human in the loop.
        </h2>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="capability-card">

                <div class="capability-title">
                    Clear outputs
                </div>

                <div class="capability-text">
                    AI responses are transformed into structured
                    engineering data using Pydantic schemas.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="capability-card">

                <div class="capability-title">
                    Less guessing
                </div>

                <div class="capability-text">
                    Prompts instruct the AI to avoid unsupported
                    assumptions and surface missing information.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="capability-card">

                <div class="capability-title">
                    Human in the loop
                </div>

                <div class="capability-text">
                    Generated tickets are designed to support
                    engineering review rather than replace it.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.info(
        "Choose a workflow from the top navigation to start."
    )


# ============================================================
# BUG REPORT ANALYZER PAGE
# ============================================================

elif selected_page == "Bug Report Analyzer":

    render_page_header(
        "01 — BUG REPORT ANALYZER",
        "Turn messy bugs into actionable tickets.",
        "Paste a bug report or upload a PDF. The AI extracts the useful "
        "engineering information and organizes it into a structured ticket.",
    )

    st.markdown(
        """
        <div class="hero">

            <div class="hero-label">
                BUG → STRUCTURED TICKET
            </div>

            <div class="hero-title">
                Give it the mess. Get back the signal.
            </div>

            <div class="hero-text">
                The analyzer identifies what is known, separates expected
                and actual behavior, extracts reproduction steps, and
                highlights information that still needs to be collected.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    st.markdown(
        '<div class="input-label">BUG REPORT INPUT</div>',
        unsafe_allow_html=True,
    )

    bug_report = st.text_area(
        "Bug report",
        height=230,
        placeholder=(
            "Example:\n\n"
            "Users are unable to log in after the latest release. "
            "The login button keeps loading after entering valid "
            "credentials. This happens in Chrome on Windows 11."
        ),
        label_visibility="collapsed",
    )

    st.markdown(
        """
        <div style="
            text-align:center;
            color:#71717a;
            font-family:'DM Mono', monospace;
            font-size:11px;
            margin:12px 0;
            letter-spacing:0.08em;
        ">
            OR
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="input-label">UPLOAD BUG REPORT PDF</div>',
        unsafe_allow_html=True,
    )

    uploaded_pdf = st.file_uploader(
        "Upload bug report PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )

    # --------------------------------------------------------
    # PDF PROCESSING
    # --------------------------------------------------------

    if uploaded_pdf is not None:

        try:
            pdf_text = extract_text_from_pdf(uploaded_pdf)

            if pdf_text.strip():

                st.success(
                    "PDF text extracted successfully."
                )

                with st.expander("Preview extracted PDF text"):
                    st.text(pdf_text[:5000])

                if not bug_report.strip():
                    bug_report = pdf_text

            else:
                st.warning(
                    "No readable text was found in the uploaded PDF."
                )

        except Exception:
            st.error(
                "The PDF could not be processed. "
                "Please check that it is a valid text-based PDF."
            )

    st.markdown("<br>", unsafe_allow_html=True)

    analyze_button = st.button(
        "Analyze Bug Report",
        use_container_width=False,
    )

    # --------------------------------------------------------
    # AI ANALYSIS
    # --------------------------------------------------------

    if analyze_button:

        if not bug_report.strip():
            st.warning(
                "Please enter a bug report or upload a PDF."
            )

        else:

            with st.spinner(
                "Analyzing the bug report..."
            ):

                try:

                    result = analyze_bug_report(
                        bug_report.strip()
                    )

                    st.markdown(
                        "<br>",
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        """
                        <div class="page-kicker">
                            ANALYSIS COMPLETE
                        </div>

                        <h2 style="
                            color:#f7f7f8;
                            font-size:26px;
                            font-weight:600;
                            margin-top:0;
                        ">
                            Engineering-ready bug ticket
                        </h2>
                        """,
                        unsafe_allow_html=True,
                    )

                    # ------------------------------------------------
                    # TITLE + SEVERITY
                    # ------------------------------------------------

                    col1, col2 = st.columns([3, 1])

                    with col1:

                        st.markdown(
                            '<div class="output-label">TITLE</div>',
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            f"""
                            <div class="output-card">
                                <div class="output-title">
                                    {html.escape(result.title)}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    with col2:

                        st.markdown(
                            '<div class="output-label">SEVERITY</div>',
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            f"""
                            <div class="output-card">
                                <span class="tag">
                                    {html.escape(result.severity)}
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    # ------------------------------------------------
                    # DESCRIPTION + CATEGORY
                    # ------------------------------------------------

                    col1, col2 = st.columns([3, 1])

                    with col1:

                        st.markdown(
                            '<div class="output-label">DESCRIPTION</div>',
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            f"""
                            <div class="output-card">
                                <div class="output-text">
                                    {html.escape(result.description)}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    with col2:

                        st.markdown(
                            '<div class="output-label">CATEGORY</div>',
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            f"""
                            <div class="output-card">
                                <span class="tag">
                                    {html.escape(result.category)}
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    # ------------------------------------------------
                    # ENVIRONMENT
                    # ------------------------------------------------

                    st.markdown(
                        '<div class="output-label">ENVIRONMENT</div>',
                        unsafe_allow_html=True,
                    )

                    with st.container(border=True):
                        render_list(
                            result.environment,
                            "No environment information identified.",
                        )

                    # ------------------------------------------------
                    # REPRODUCTION STEPS
                    # ------------------------------------------------

                    st.markdown(
                        '<div class="output-label">REPRODUCTION STEPS</div>',
                        unsafe_allow_html=True,
                    )

                    with st.container(border=True):

                        if result.reproduction_steps:

                            for index, step in enumerate(
                                result.reproduction_steps,
                                start=1,
                            ):

                                st.markdown(
                                    f"""
                                    <div style="
                                        color:#d4d4d8;
                                        font-size:14px;
                                        line-height:1.6;
                                        margin-bottom:9px;
                                    ">
                                        <span style="
                                            color:#6ea8fe;
                                            font-family:'DM Mono', monospace;
                                        ">
                                            {index:02d}
                                        </span>
                                        &nbsp;&nbsp;
                                        {html.escape(step)}
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                        else:

                            st.markdown(
                                '<div class="output-text">'
                                'No reproduction steps identified.'
                                '</div>',
                                unsafe_allow_html=True,
                            )

                    # ------------------------------------------------
                    # EXPECTED VS ACTUAL
                    # ------------------------------------------------

                    col1, col2 = st.columns(2)

                    with col1:

                        st.markdown(
                            '<div class="output-label">'
                            'EXPECTED BEHAVIOR'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            f"""
                            <div class="output-card">
                                <div class="output-text">
                                    {html.escape(
                                        result.expected_behavior
                                    )}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    with col2:

                        st.markdown(
                            '<div class="output-label">'
                            'ACTUAL BEHAVIOR'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            f"""
                            <div class="output-card">
                                <div class="output-text">
                                    {html.escape(
                                        result.actual_behavior
                                    )}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    # ------------------------------------------------
                    # MISSING INFORMATION
                    # ------------------------------------------------

                    st.markdown(
                        '<div class="output-label">'
                        'MISSING INFORMATION'
                        '</div>',
                        unsafe_allow_html=True,
                    )

                    with st.container(border=True):
                        render_list(
                            result.missing_information,
                            "No important missing information identified.",
                        )

                    # ------------------------------------------------
                    # ACCEPTANCE CRITERIA
                    # ------------------------------------------------

                    st.markdown(
                        '<div class="output-label">'
                        'ACCEPTANCE CRITERIA'
                        '</div>',
                        unsafe_allow_html=True,
                    )

                    with st.container(border=True):
                        render_list(
                            result.acceptance_criteria,
                            "No acceptance criteria identified.",
                        )

                    st.download_button(
                        "Download Analysis as PDF",
                        data=generate_bug_analysis_pdf(result),
                        file_name="devsift-bug-analysis.pdf",
                        mime="application/pdf",
                        on_click="ignore",
                    )

                except Exception as error:

                    render_error(
                        error,
                        "Bug analysis",
                    )


# ============================================================
# MEETING-TO-TICKET REFINER PAGE
# ============================================================

elif selected_page == "Meeting-to-Ticket Refiner":

    render_page_header(
        "02 — MEETING-TO-TICKET REFINER",
        "Turn conversations into engineering work.",
        "Paste meeting notes or a transcript and transform discussed "
        "requirements into focused, Jira-ready engineering tickets.",
    )

    st.markdown(
        """
        <div class="hero">

            <div class="hero-label">
                MEETING → ENGINEERING TICKETS
            </div>

            <div class="hero-title">
                Capture the discussion. Clarify the work.
            </div>

            <div class="hero-text">
                The refiner separates meaningful requirements, creates
                focused user stories, defines acceptance criteria,
                identifies edge cases and dependencies, and surfaces
                unresolved questions.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    st.markdown(
        '<div class="input-label">MEETING NOTES / TRANSCRIPT</div>',
        unsafe_allow_html=True,
    )

    meeting_notes = st.text_area(
        "Meeting notes",
        height=280,
        placeholder=(
            "Example:\n\n"
            "The team discussed adding Google login. Users should "
            "be able to sign in using their Google account. The "
            "backend needs OAuth configuration. We also need to "
            "handle authentication failures gracefully."
        ),
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    generate_button = st.button(
        "Generate Engineering Tickets",
        use_container_width=False,
    )

    # --------------------------------------------------------
    # AI ANALYSIS
    # --------------------------------------------------------

    if generate_button:

        if not meeting_notes.strip():

            st.warning(
                "Please enter meeting notes or a transcript."
            )

        else:

            with st.spinner(
                "Refining meeting discussion into engineering tickets..."
            ):

                try:

                    result = generate_meeting_tickets(
                        meeting_notes.strip()
                    )

                    st.markdown(
                        "<br>",
                        unsafe_allow_html=True,
                    )

                    if not result.tickets:

                        st.warning(
                            "No actionable engineering requirements "
                            "were identified in the meeting notes."
                        )

                    else:

                        st.markdown(
                            """
                            <div class="page-kicker">
                                REFINEMENT COMPLETE
                            </div>

                            <h2 style="
                                color:#f7f7f8;
                                font-size:26px;
                                font-weight:600;
                                margin-top:0;
                            ">
                                Engineering tickets generated
                            </h2>
                            """,
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            f"""
                            <div style="
                                color:#a1a1aa;
                                font-size:14px;
                                margin-bottom:20px;
                            ">
                                {len(result.tickets)}
                                actionable ticket(s) identified.
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        for index, ticket in enumerate(
                            result.tickets,
                            start=1,
                        ):

                            render_ticket(
                                ticket,
                                index,
                            )

                        st.download_button(
                            "Download Analysis as PDF",
                            data=generate_meeting_analysis_pdf(result),
                            file_name="devsift-meeting-tickets.pdf",
                            mime="application/pdf",
                            on_click="ignore",
                        )

                except Exception as error:

                    render_error(
                        error,
                        "Meeting-to-ticket refinement",
                    )
# ============================================================
# PHISHING EMAIL INVESTIGATOR PAGE
# ============================================================

elif selected_page == "Phishing Email Investigator":

    render_page_header(
        "03 — PHISHING EMAIL INVESTIGATOR",
        "Analyze Suspicious Emails for Phishing Threats.",
        "Analyze email content, sender-origin indicators, headers, URLs, "
        "social-engineering signals, and attachment metadata using a "
        "defensive AI-assisted workflow.",
    )

    st.markdown(
        """
        <div class="hero">

            <div class="hero-label">
                EMAIL → SECURITY ASSESSMENT
            </div>

            <div class="hero-title">
                Inspect the evidence. Don't trust the message.
            </div>

            <div class="hero-text">
                The investigator treats email content as untrusted data,
                extracts evidence locally, and uses the AI to produce a
                structured security assessment for human review.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # SECURITY / PRIVACY NOTICE
    # --------------------------------------------------------

    st.warning(
        "Privacy and security notice: email data submitted for AI analysis "
        "may be transmitted to the configured OpenRouter API. Do not submit "
        "confidential business information, passwords, OTPs, API keys, "
        "access tokens, financial secrets, or other sensitive data. "
        "Uploaded .eml files are parsed locally; URLs are not visited and "
        "attachments are not executed."
    )

    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    st.markdown(
        '<div class="input-label">EMAIL INPUT</div>',
        unsafe_allow_html=True,
    )

    input_tab, upload_tab = st.tabs(
        [
            "Paste Raw Email",
            "Upload .eml",
        ],
        key="phishing_input_tabs",
        on_change="rerun",
    )

    pasted_email = ""

    with input_tab:
        pasted_email = st.text_area(
            "Paste raw email",
            height=300,
            placeholder=(
                "Paste the raw email here, including headers if available.\n\n"
                "Example:\n"
                "From: Security Team <security@example.com>\n"
                "To: user@company.com\n"
                "Subject: Verify your account\n"
                "X-External: External\n\n"
                "Your account requires verification..."
            ),
            label_visibility="collapsed",
        )

    with upload_tab:
        uploaded_eml = st.file_uploader(
            "Upload an email file",
            type=["eml"],
            label_visibility="collapsed",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    analyze_phishing_button = st.button(
        "Investigate Email",
        use_container_width=False,
    )

    # --------------------------------------------------------
    # AI ANALYSIS
    # --------------------------------------------------------

    if analyze_phishing_button:

        if input_tab.open and not pasted_email.strip():
            st.warning(
                "Please paste a raw email."
            )

        elif upload_tab.open and uploaded_eml is None:
            st.warning(
                "Please upload an .eml file."
            )

        else:

            try:

                # Parse locally first. Nothing is sent to OpenRouter during
                # parsing, and the parser does not visit URLs or execute
                # attachments.
                if input_tab.open:
                    pasted_file = io.BytesIO(
                        pasted_email.encode("utf-8")
                    )
                    pasted_file.name = "pasted_email.eml"
                    email_data = parse_eml_file(pasted_file)
                else:
                    email_data = parse_eml_file(uploaded_eml)

                if not email_data.get("body", "").strip():
                    st.warning(
                        "No readable email body was found. "
                        "Headers may still be available for analysis."
                    )

                # Show a local extraction preview before the AI request.
                with st.expander("Preview locally extracted email data"):
                    st.markdown(
                        '<div class="output-label">SENDER</div>',
                        unsafe_allow_html=True,
                    )
                    st.code(
                        email_data.get("sender", "") or "Not available"
                    )

                    st.markdown(
                        '<div class="output-label">SUBJECT</div>',
                        unsafe_allow_html=True,
                    )
                    st.code(
                        email_data.get("subject", "") or "Not available"
                    )

                    st.markdown(
                        '<div class="output-label">EXTRACTED URLS</div>',
                        unsafe_allow_html=True,
                    )

                    extracted_urls = email_data.get("urls", [])

                    if extracted_urls:
                        for url in extracted_urls:
                            st.code(url)
                    else:
                        st.write("No URLs extracted.")

                    st.markdown(
                        '<div class="output-label">ATTACHMENT METADATA</div>',
                        unsafe_allow_html=True,
                    )

                    attachments = email_data.get("attachments", [])

                    if attachments:
                        for attachment in attachments:
                            st.code(
                                f"{attachment.get('filename', 'unnamed')} "
                                f"({attachment.get('mime_type', 'unknown')})"
                            )
                    else:
                        st.write("No attachments detected.")

                with st.spinner(
                    "Investigating the email for phishing indicators..."
                ):

                    result = analyze_phishing_email(
                        email_data
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown(
                    """
                    <div class="page-kicker">
                        INVESTIGATION COMPLETE
                    </div>

                    <h2 style="
                        color:#f7f7f8;
                        font-size:26px;
                        font-weight:600;
                        margin-top:0;
                    ">
                        Security assessment
                    </h2>
                    """,
                    unsafe_allow_html=True,
                )

                # ----------------------------------------------------
                # SUMMARY METRICS
                # ----------------------------------------------------

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown(
                        '<div class="output-label">SENDER ORIGIN</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"""
                        <div class="output-card">
                            <span class="tag">
                                {html.escape(result.sender_origin)}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col2:
                    st.markdown(
                        '<div class="output-label">VERDICT</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"""
                        <div class="output-card">
                            <span class="tag">
                                {html.escape(result.verdict)}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col3:
                    st.markdown(
                        '<div class="output-label">RISK LEVEL</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"""
                        <div class="output-card">
                            <span class="tag">
                                {html.escape(result.risk_level)}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col4:
                    st.markdown(
                        '<div class="output-label">CONFIDENCE</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"""
                        <div class="output-card">
                            <span class="tag">
                                {result.confidence}%
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # ----------------------------------------------------
                # SUMMARY
                # ----------------------------------------------------

                st.markdown(
                    '<div class="output-label">SUMMARY</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div class="output-card">
                        <div class="output-text">
                            {html.escape(result.summary)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # ----------------------------------------------------
                # HUMAN REVIEW
                # ----------------------------------------------------

                if result.human_review_required:
                    st.warning(
                        "Human/security review is recommended for this result."
                    )
                else:
                    st.info(
                        "No mandatory human review was flagged by the model. "
                        "The result should still be treated as an AI-assisted "
                        "assessment rather than a definitive security verdict."
                    )

                # ----------------------------------------------------
                # SENDER ANALYSIS
                # ----------------------------------------------------

                st.markdown(
                    '<div class="output-label">SENDER ANALYSIS</div>',
                    unsafe_allow_html=True,
                )

                with st.container(border=True):
                    render_list(
                        result.sender_analysis,
                        "No sender indicators identified.",
                    )

                # ----------------------------------------------------
                # HEADER ANALYSIS
                # ----------------------------------------------------

                st.markdown(
                    '<div class="output-label">HEADER ANALYSIS</div>',
                    unsafe_allow_html=True,
                )

                header_col1, header_col2 = st.columns(2)

                with header_col1:
                    st.markdown(
                        '<div class="output-label">OBSERVED</div>',
                        unsafe_allow_html=True,
                    )
                    with st.container(border=True):
                        render_list(
                            result.header_analysis.observed,
                            "No important header observations.",
                        )

                with header_col2:
                    st.markdown(
                        '<div class="output-label">INCONSISTENCIES</div>',
                        unsafe_allow_html=True,
                    )
                    with st.container(border=True):
                        render_list(
                            result.header_analysis.inconsistencies,
                            "No header inconsistencies identified.",
                        )

                header_col1, header_col2 = st.columns(2)

                with header_col1:
                    st.markdown(
                        '<div class="output-label">AUTHENTICATION RESULTS</div>',
                        unsafe_allow_html=True,
                    )
                    with st.container(border=True):
                        render_list(
                            result.header_analysis.authentication_results,
                            "No explicit SPF, DKIM, or DMARC results available.",
                        )

                with header_col2:
                    st.markdown(
                        '<div class="output-label">MISSING HEADER EVIDENCE</div>',
                        unsafe_allow_html=True,
                    )
                    with st.container(border=True):
                        render_list(
                            result.header_analysis.missing_headers,
                            "No important missing header evidence identified.",
                        )

                # ----------------------------------------------------
                # URL ANALYSIS
                # ----------------------------------------------------

                st.markdown(
                    '<div class="output-label">URL ANALYSIS</div>',
                    unsafe_allow_html=True,
                )

                if result.url_analysis:

                    for index, url_result in enumerate(
                        result.url_analysis,
                        start=1,
                    ):

                        st.markdown(
                            f"""
                            <div class="output-card">

                                <div class="output-label">
                                    URL {index:02d}
                                </div>

                                <div class="mono-output">
                                    {html.escape(url_result.url)}
                                </div>

                                <br>

                                <div class="output-text">
                                    <strong>Domain:</strong>
                                    {html.escape(url_result.domain or "Unavailable")}
                                    <br>
                                    <strong>HTTPS:</strong>
                                    {"Yes" if url_result.https else "No"}
                                    <br>
                                    <strong>Risk:</strong>
                                    {html.escape(url_result.risk_level)}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if url_result.suspicious_indicators:
                            with st.container(border=True):
                                render_list(
                                    url_result.suspicious_indicators,
                                    "No suspicious URL indicators identified.",
                                )

                else:
                    with st.container(border=True):
                        st.markdown(
                            '<div class="output-text">'
                            'No URLs were identified for analysis.'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                # ----------------------------------------------------
                # SOCIAL ENGINEERING
                # ----------------------------------------------------

                st.markdown(
                    '<div class="output-label">'
                    'SOCIAL-ENGINEERING INDICATORS'
                    '</div>',
                    unsafe_allow_html=True,
                )

                if result.social_engineering_indicators:

                    for item in result.social_engineering_indicators:
                        st.markdown(
                            f"""
                            <div class="output-card">

                                <div class="output-title">
                                    {html.escape(item.finding)}
                                </div>

                                <div class="output-text">
                                    <strong>Evidence:</strong>
                                    {html.escape(item.evidence)}
                                    <br><br>
                                    <strong>Interpretation:</strong>
                                    {html.escape(item.interpretation)}
                                    <br><br>
                                    <strong>Risk contribution:</strong>
                                    {html.escape(item.risk_contribution)}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                else:
                    with st.container(border=True):
                        st.markdown(
                            '<div class="output-text">'
                            'No social-engineering indicators identified.'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                # ----------------------------------------------------
                # CREDENTIAL HARVESTING
                # ----------------------------------------------------

                st.markdown(
                    '<div class="output-label">'
                    'CREDENTIAL-HARVESTING INDICATORS'
                    '</div>',
                    unsafe_allow_html=True,
                )

                if result.credential_harvesting_indicators:

                    for item in result.credential_harvesting_indicators:
                        st.markdown(
                            f"""
                            <div class="output-card">

                                <div class="output-title">
                                    {html.escape(item.finding)}
                                </div>

                                <div class="output-text">
                                    <strong>Evidence:</strong>
                                    {html.escape(item.evidence)}
                                    <br><br>
                                    <strong>Interpretation:</strong>
                                    {html.escape(item.interpretation)}
                                    <br><br>
                                    <strong>Risk contribution:</strong>
                                    {html.escape(item.risk_contribution)}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                else:
                    with st.container(border=True):
                        st.markdown(
                            '<div class="output-text">'
                            'No credential-harvesting indicators identified.'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                # ----------------------------------------------------
                # ATTACHMENT ANALYSIS
                # ----------------------------------------------------

                st.markdown(
                    '<div class="output-label">'
                    'ATTACHMENT ANALYSIS'
                    '</div>',
                    unsafe_allow_html=True,
                )

                if result.attachment_analysis:

                    for attachment in result.attachment_analysis:
                        st.markdown(
                            f"""
                            <div class="output-card">

                                <div class="output-title">
                                    {html.escape(attachment.filename)}
                                </div>

                                <div class="output-text">
                                    <strong>MIME type:</strong>
                                    {html.escape(attachment.mime_type)}
                                    <br>
                                    <strong>Risk:</strong>
                                    {html.escape(attachment.risk_level)}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        with st.container(border=True):
                            render_list(
                                attachment.suspicious_indicators,
                                "No suspicious attachment indicators identified.",
                            )

                else:
                    with st.container(border=True):
                        st.markdown(
                            '<div class="output-text">'
                            'No attachment metadata was identified.'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                # ----------------------------------------------------
                # STRONGEST EVIDENCE
                # ----------------------------------------------------

                st.markdown(
                    '<div class="output-label">STRONGEST EVIDENCE</div>',
                    unsafe_allow_html=True,
                )

                if result.evidence:

                    for item in result.evidence:
                        st.markdown(
                            f"""
                            <div class="output-card">

                                <div class="output-title">
                                    {html.escape(item.finding)}
                                </div>

                                <div class="output-text">
                                    <strong>Evidence:</strong>
                                    {html.escape(item.evidence)}
                                    <br><br>
                                    <strong>Interpretation:</strong>
                                    {html.escape(item.interpretation)}
                                    <br><br>
                                    <strong>Risk contribution:</strong>
                                    {html.escape(item.risk_contribution)}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                else:
                    with st.container(border=True):
                        st.markdown(
                            '<div class="output-text">'
                            'No strong evidence was identified.'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                # ----------------------------------------------------
                # MISSING INFORMATION
                # ----------------------------------------------------

                st.markdown(
                    '<div class="output-label">MISSING INFORMATION</div>',
                    unsafe_allow_html=True,
                )

                with st.container(border=True):
                    render_list(
                        result.missing_information,
                        "No important missing information identified.",
                    )

                # ----------------------------------------------------
                # RECOMMENDED ACTIONS
                # ----------------------------------------------------

                st.markdown(
                    '<div class="output-label">RECOMMENDED ACTIONS</div>',
                    unsafe_allow_html=True,
                )

                with st.container(border=True):
                    render_list(
                        result.recommended_actions,
                        "No additional defensive actions identified.",
                    )

                st.download_button(
                    "Download Analysis as PDF",
                    data=generate_phishing_analysis_pdf(result),
                    file_name="devsift-phishing-investigation.pdf",
                    mime="application/pdf",
                    on_click="ignore",
                )

            except Exception as error:

                render_error(
                    error,
                    "Phishing email investigation",
                )

