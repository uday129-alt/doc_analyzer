"""
main.py — Multimodal Document Analyzer
=========================================
Premium AI SaaS Interface
Single Tab:
  1. 📄 Summarize   — OCR + multi-mode summary + download
"""

from __future__ import annotations

import sys
import os
import tempfile

import streamlit as st

# Ensure the app package is importable whether run from root or app/
sys.path.insert(0, os.path.dirname(__file__))

from ocr_utils import extract_text, extract_video_text, SUPPORTED_EXTENSIONS, VIDEO_EXTENSIONS
from llm_utils import (
    summarize_text,
    PROVIDER_MODELS,
    SUMMARY_MODES,
    TONES,
    GeminiAPIError,
)
from download_utils import to_txt, to_pdf, to_docx

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Multimodal Document Analyzer",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Premium Glassmorphism UI Styles ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');
    
    :root {
        --bg-primary: #070B14;
        --bg-secondary: #0F172A;
        --bg-card: rgba(255, 255, 255, 0.05);
        --color-primary: #FF9500;
        --color-accent: #FFB84D;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --border-color: rgba(255, 255, 255, 0.08);
        --border-glow: rgba(255, 149, 0, 0.3);
    }

    /* ── Global Styles ── */
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }

    * {
        font-family: 'Inter', sans-serif;
    }

    /* ── Sidebar Glassmorphism ── */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        border-right: 1px solid var(--border-color) !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 1.5rem;
    }

    /* ── Headings ── */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    /* ── Cards & Containers ── */
    .card, [data-testid="stExpander"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }

    .card:hover {
        border-color: var(--border-glow) !important;
        background: rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 12px 48px rgba(139, 92, 246, 0.15);
    }

    /* ── Banners ── */
    .banner-ok {
        background: rgba(34, 197, 94, 0.1) !important;
        border-left: 4px solid #22c55e !important;
        border-radius: 8px !important;
        padding: 0.8rem 1.2rem !important;
        margin-bottom: 1rem !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(34, 197, 94, 0.2) !important;
        color: #86efac !important;
    }

    .banner-err {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 4px solid #ef4444 !important;
        border-radius: 8px !important;
        padding: 0.8rem 1.2rem !important;
        margin-bottom: 1rem !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        color: #fca5a5 !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%) !important;
        color: white !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.7rem 1.5rem !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.2);
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4) !important;
        background: linear-gradient(135deg, #a78bfa 0%, #60a5fa 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── Select & Input Styling ── */
    .stSelectbox, .stTextInput, .stTextArea {
        margin-bottom: 1rem !important;
    }

    .stSelectbox > div > div, .stTextInput > div > div, .stTextArea > div > div {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }

    .stSelectbox > div > div:hover, .stTextInput > div > div:hover, .stTextArea > div > div:hover {
        border-color: var(--color-primary) !important;
        background: rgba(139, 92, 246, 0.05) !important;
    }

    .stSelectbox > div > div:focus-within, .stTextInput > div > div:focus-within, .stTextArea > div > div:focus-within {
        border-color: var(--color-primary) !important;
        background: rgba(139, 92, 246, 0.08) !important;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.2) !important;
    }

    textarea, input[type="text"], input[type="password"] {
        background-color: transparent !important;
        color: var(--text-primary) !important;
        border: none !important;
        font-family: 'Inter', sans-serif !important;
    }

    textarea::placeholder, input::placeholder {
        color: var(--text-secondary) !important;
    }

    /* ── Tabs ── */
    [data-testid="stTabs"] {
        background: transparent !important;
    }

    [data-testid="stTabs"] button {
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        font-size: 1rem !important;
        border-radius: 20px !important;
        padding: 0.6rem 1.4rem !important;
        border: 1px solid transparent !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stTabs"] button:hover {
        color: var(--text-primary) !important;
        border-color: var(--border-glow) !important;
        background: rgba(139, 92, 246, 0.1) !important;
    }

    [data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--text-primary) !important;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(59, 130, 246, 0.1)) !important;
        border: 1px solid var(--border-glow) !important;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
    }

    [data-testid="stTabs"] [role="tablist"] {
        gap: 0.5rem !important;
        background: rgba(255, 255, 255, 0.02) !important;
        padding: 0.8rem !important;
        border-radius: 12px !important;
        border: 1px solid var(--border-color) !important;
        backdrop-filter: blur(10px);
    }

    /* ── Chat Bubbles ── */
    .chat-user {
        background: rgba(139, 92, 246, 0.15) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 14px 14px 2px 14px !important;
        padding: 0.8rem 1.2rem !important;
        margin: 0.6rem 15% 0.6rem auto !important;
        font-size: 0.95rem !important;
        backdrop-filter: blur(10px);
        color: var(--text-primary) !important;
    }

    .chat-bot {
        background: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: 14px 14px 14px 2px !important;
        padding: 0.8rem 1.2rem !important;
        margin: 0.6rem auto 0.6rem 15% !important;
        font-size: 0.95rem !important;
        backdrop-filter: blur(10px);
        color: var(--text-primary) !important;
    }

    /* ── File Uploader ── */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed var(--border-glow) !important;
        border-radius: 16px !important;
        background: rgba(139, 92, 246, 0.05) !important;
        padding: 2.5rem !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stFileUploadDropzone"]:hover {
        border-color: var(--color-primary) !important;
        background: rgba(139, 92, 246, 0.1) !important;
        box-shadow: 0 0 30px rgba(139, 92, 246, 0.2) !important;
    }

    /* ── Scrollbars ── */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.3);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(139, 92, 246, 0.5);
    }

    /* ── Text Utilities ── */
    .gradient-text {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-subtitle {
        color: var(--text-secondary) !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.05em !important;
    }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        background: var(--bg-card) !important;
    }

    [data-testid="stExpander"] details {
        border: none !important;
    }

    [data-testid="stExpander"] summary {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    /* ── Column Layout ── */
    [data-testid="stColumn"] {
        gap: 1rem;
    }

    /* ── Info & Warning Messages ── */
    .stInfo, .stWarning {
        background: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        color: var(--text-primary) !important;
    }

    /* ── Responsive Design ── */
    @media (max-width: 768px) {
        .stSidebar {
            width: 70% !important;
        }
        
        [data-testid="stTabs"] button {
            padding: 0.5rem 1rem !important;
            font-size: 0.9rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Session state initialisation ──────────────────────────────────────────────

_DEFAULTS: dict = {
    "provider": "Gemini",
    "model": PROVIDER_MODELS["Gemini"][0],
    "api_key": "",
    "extracted_text": "",
    "summary": "",
    "summary_mode": SUMMARY_MODES[0],
    "tone": TONES[0],
    "last_uploaded_name": "",
}

for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        "<div style='margin-bottom:1.5rem;'>"
        "<h2 style='font-size:1.2rem; margin:0; color:#FF9500;'>⚙️ Configuration</h2>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("**AI Provider**")
    provider = st.selectbox(
        "Select Provider",
        options=list(PROVIDER_MODELS.keys()),
        index=list(PROVIDER_MODELS.keys()).index(st.session_state["provider"]),
        key="_sb_provider",
        label_visibility="collapsed",
    )
    if provider != st.session_state["provider"]:
        st.session_state["provider"] = provider
        st.session_state["model"] = PROVIDER_MODELS[provider][0]

    st.markdown("**Model**")
    model = st.selectbox(
        "Select Model",
        options=PROVIDER_MODELS[provider],
        index=(
            PROVIDER_MODELS[provider].index(st.session_state["model"])
            if st.session_state["model"] in PROVIDER_MODELS[provider]
            else 0
        ),
        key="_sb_model",
        label_visibility="collapsed",
    )
    st.session_state["model"] = model

    st.markdown("**API Key**")
    api_key = st.text_input(
        f"{provider} API Key",
        type="password",
        value=st.session_state["api_key"],
        help="Stored only in this browser session — never logged.",
        key="_sb_apikey",
        label_visibility="collapsed",
    )
    st.session_state["api_key"] = api_key

    st.markdown("<div style='height:1px; background:rgba(255,255,255,0.08); margin:1.5rem 0;'></div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='margin-bottom:1rem;'>"
        "<h3 style='font-size:1rem; margin:0; color:#FF9500;'>📝 Summary Options</h3>"
        "</div>",
        unsafe_allow_html=True,
    )
    
    st.markdown("**Mode**")
    st.session_state["summary_mode"] = st.selectbox(
        "Summary Mode",
        SUMMARY_MODES,
        index=SUMMARY_MODES.index(st.session_state["summary_mode"]),
        key="_sb_mode",
        label_visibility="collapsed",
    )
    
    st.markdown("**Tone**")
    st.session_state["tone"] = st.selectbox(
        "Tone",
        TONES,
        index=TONES.index(st.session_state["tone"]),
        key="_sb_tone",
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:1px; background:rgba(255,255,255,0.08); margin:1.5rem 0;'></div>", unsafe_allow_html=True)
    st.caption("🔒 Your API keys are stored only in session memory — never logged or sent anywhere.")


# ── Hero Section ─────────────────────────────────────────────────────────────────────

st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        "<h1 style='text-align:center; font-size:3.5rem; margin-bottom:0.5rem; "
        "font-family:\"Space Grotesk\", sans-serif; font-weight:700; "
        "background: linear-gradient(135deg, #FF9500 0%, #FFB84D 100%); "
        "-webkit-background-clip: text; -webkit-text-fill-color: transparent; "
        "background-clip: text; letter-spacing: -0.02em;'>"
        "✨ Multimodal Document Analyzer</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; font-size:1.15rem; color:#94A3B8; "
        "margin-top:1rem; letter-spacing: 0.05em; font-weight:500;'>"
        "OCR • AI Summaries • RAG Chat • PDF/DOCX Export"
        "</p>",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
st.markdown("<div style='height:1px; background:rgba(255,255,255,0.08); margin:2rem 0;'></div>", unsafe_allow_html=True)


# ── Tabs ───────────────────────────────────────────────────────────────────────

tab_sum = st.tabs(["📄 Summarize"])[0]


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SUMMARIZE
# ══════════════════════════════════════════════════════════════════════════════

with tab_sum:
    st.markdown(
        "<h3 style='font-size:1.5rem; font-family:\"Space Grotesk\", sans-serif; "
        "margin-bottom:1.5rem;'>📄 Upload & Analyze</h3>",
        unsafe_allow_html=True,
    )

    supported = ", ".join(sorted(SUPPORTED_EXTENSIONS | VIDEO_EXTENSIONS))
    
    st.markdown(
        "<div style='margin-bottom:1rem;'>"
        "<p style='color:#94A3B8; font-size:0.95rem;'>Supported: " + supported + "</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    
    uploaded = st.file_uploader(
        "Drag & drop your document or click to select",
        type=["pdf", "docx", "jpg", "jpeg", "png", "mp4", "mov", "avi"],
        key="uploader_sum",
        label_visibility="collapsed",
    )

    if uploaded is not None:
        file_bytes = uploaded.read()

        # Size guard
        if len(file_bytes) > 15 * 1024 * 1024:
            st.markdown('<div class="banner-err">❌ File exceeds the 15 MB limit.</div>',
                        unsafe_allow_html=True)
        elif uploaded.name != st.session_state["last_uploaded_name"]:
            # New file — extract
            with st.spinner("🔍 Extracting text via OCR…"):
                tmp_path = None
                try:
                    _, ext = os.path.splitext(uploaded.name.lower())
                    if ext in VIDEO_EXTENSIONS:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=ext or ".mp4") as tmp:
                            tmp.write(file_bytes)
                            tmp_path = tmp.name
                        text = extract_video_text(tmp_path)
                    else:
                        text = extract_text(file_bytes, uploaded.name)

                    st.session_state["extracted_text"] = text
                    st.session_state["summary"] = ""
                    st.session_state["last_uploaded_name"] = uploaded.name

                    st.markdown(
                        f'<div class="banner-ok">✅ Extracted {len(text):,} characters '
                        f'from <strong>{uploaded.name}</strong></div>',
                        unsafe_allow_html=True,
                    )
                except Exception as exc:
                    st.markdown(
                        f'<div class="banner-err">❌ Extraction failed: {exc}</div>',
                        unsafe_allow_html=True,
                    )
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        os.unlink(tmp_path)

    if st.session_state["extracted_text"]:
        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
        
        with st.expander("🔎 View Extracted Text", expanded=False):
            st.text_area(
                "Full document text",
                st.session_state["extracted_text"],
                height=250,
                disabled=True,
                key="preview_text",
            )

        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

        col_btn, col_info = st.columns([1, 3])
        with col_btn:
            do_summarize = st.button("✨ Generate Summary", use_container_width=True, key="btn_summarize")
        with col_info:
            st.markdown(
                f"<div style='padding:0.8rem 1.2rem; background:rgba(255,149,0,0.05); "
                f"border:1px solid rgba(255,149,0,0.2); border-radius:10px; color:#94A3B8;'>"
                f"<strong>Mode:</strong> {st.session_state['summary_mode']} • "
                f"<strong>Tone:</strong> {st.session_state['tone']} • "
                f"<strong>Provider:</strong> {st.session_state['provider']}"
                f"</div>",
                unsafe_allow_html=True,
            )

        if do_summarize:
            if not st.session_state["api_key"]:
                st.warning(f"⚠️ Please enter your {provider} API key in the sidebar.")
            else:
                with st.spinner(f"🤖 Generating summary with {st.session_state['provider']}…"):
                    try:
                        summary = summarize_text(
                            st.session_state["extracted_text"],
                            provider=st.session_state["provider"],
                            model=st.session_state["model"],
                            api_key=st.session_state["api_key"],
                            mode=st.session_state["summary_mode"],
                            tone=st.session_state["tone"],
                        )
                        st.session_state["summary"] = summary
                        st.markdown(
                            '<div class="banner-ok">✅ Summary generated successfully!</div>',
                            unsafe_allow_html=True,
                        )
                    except GeminiAPIError as exc:
                        st.markdown(
                            f'<div class="banner-err">{exc}</div>',
                            unsafe_allow_html=True,
                        )
                    except ValueError as exc:
                        st.markdown(
                            f'<div class="banner-err">⚠️ Input error: {exc}</div>',
                            unsafe_allow_html=True,
                        )
                    except Exception as exc:
                        st.markdown(
                            f'<div class="banner-err">❌ Summary failed: {exc}</div>',
                            unsafe_allow_html=True,
                        )

    if st.session_state["summary"]:
        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📝 Summary")
        st.write(st.session_state["summary"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

        st.markdown(
            "<h4 style='font-family:\"Space Grotesk\", sans-serif; margin-bottom:1rem;'>"
            "📥 Download Summary</h4>",
            unsafe_allow_html=True,
        )
        
        dl1, dl2, dl3 = st.columns(3)

        with dl1:
            st.download_button(
                "⬇️ TXT",
                data=to_txt(st.session_state["summary"]),
                file_name="summary.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with dl2:
            try:
                pdf_bytes = to_pdf(st.session_state["summary"])
                st.download_button(
                    "⬇️ PDF",
                    data=pdf_bytes,
                    file_name="summary.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.caption(f"PDF unavailable: {e}")
        with dl3:
            try:
                docx_bytes = to_docx(st.session_state["summary"])
                st.download_button(
                    "⬇️ DOCX",
                    data=docx_bytes,
                    file_name="summary.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception as e:
                st.caption(f"DOCX unavailable: {e}")

    st.markdown("<div style='height:3rem;'></div>", unsafe_allow_html=True)

    # ── Feature Cards ───────────────────────────────────────────────────────────────
    st.markdown(
        "<div style='text-align:center; margin-bottom:2rem;'>"
        "<p style='color:#94A3B8; font-size:0.95rem; text-transform:uppercase; letter-spacing:0.1em;'>"
        "Powerful Features"
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    feature_cards = [
        {
            "icon": "🔍",
            "title": "OCR",
            "desc": "Extract text from images, PDFs and scanned documents"
        },
        {
            "icon": "✨",
            "title": "AI Summaries",
            "desc": "Get concise and accurate summaries powered by AI"
        },
        {
            "icon": "💬",
            "title": "Smart Analysis",
            "desc": "Analyze your documents with intelligent insights"
        },
        {
            "icon": "📥",
            "title": "Export",
            "desc": "Download your results as PDF or DOCX"
        }
    ]
    
    cols = [col1, col2, col3, col4]
    
    for i, (col, card) in enumerate(zip(cols, feature_cards)):
        with col:
            st.markdown(
                f"""
                <div style='
                    background: rgba(255,255,255,0.03);
                    border: 1px solid rgba(139,92,246,0.2);
                    border-radius: 16px;
                    padding: 1.5rem 1.2rem;
                    text-align: center;
                    backdrop-filter: blur(10px);
                    transition: all 0.3s ease;
                    height: 100%;
                '>
                    <div style='font-size: 2.5rem; margin-bottom: 0.8rem;'>{card["icon"]}</div>
                    <h4 style='
                        font-family: "Space Grotesk", sans-serif;
                        font-weight: 700;
                        margin: 0 0 0.5rem 0;
                        color: #F8FAFC;
                        font-size: 1.1rem;
                    '>{card["title"]}</h4>
                    <p style='
                        color: #94A3B8;
                        font-size: 0.85rem;
                        margin: 0;
                        line-height: 1.4;
                    '>{card["desc"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
