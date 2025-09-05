import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------- Page Config ----------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")

# ---------- CSS Styling ----------
st.markdown("""
<style>
/* Background gradient */
body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #fff8f1 0%, #ffe5d1 100%);
    color: #4a4030;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Container */
.container {
    background: #fffaf3;
    border-radius: 22px;
    padding: 46px 52px 40px;
    max-width: 720px;
    margin: 48px auto 64px;
    box-shadow: 0 15px 50px rgba(255, 135, 0, 0.35);
    border: 1.8px solid #ffd8a0;
}

/* Header */
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.header-title { font-size: 2.8rem; font-weight: 800; color: #e66c02; letter-spacing: 0.04em; }
.header-badge { background-color: #ff7f23; color: white; font-weight: 700; padding: 7px 26px; font-size: 1.15rem; border-radius: 16px; box-shadow: 0 0 28px #ffB84eaa; }

/* Subtitle */
.subtitle { margin-top: 6px; margin-bottom: 38px; font-weight: 600; font-size: 1.22rem; color: #a15303cc; }

/* Selectbox */
.stSelectbox > div:first-child { font-weight: 600; font-size: 1.1rem; color: #bf6e12cc; }
.stSelectbox > div[role="listbox"] > div { font-size: 1.02rem; color: #d8922ecc; }

/* Textarea */
textarea {
    font-size: 1.17rem !important; line-height: 1.5 !important; padding: 20px !important;
    background-color: #fff6e9 !important; color: #7a4d00 !important; border-radius: 16px !important;
    border: 2px solid #ffaf52 !important; min-height: 110px !important; resize: vertical !important;
}
textarea:focus {
    outline: none !important; background-color: #fff5db !important; border-color: #ff8a1e !important;
    box-shadow: 0 0 14px 5px #ff9c1e95 !important;
}

/* Swap button */
.swap-btn {
    width: 50px; height: 50px; background: #ff7f23; font-size: 28px; color: white; border-radius: 50%;
    border: none; cursor: pointer; display: flex; align-items: center; justify-content: center;
    margin: auto; transition: transform 0.24s ease, box-shadow 0.24s ease; box-shadow: 0 0 12px #ffb14dcc;
}
.swap-btn:hover { transform: scale(1.18); box-shadow: 0 0 28px #ffb14ddd; }

/* Buttons */
.action-btn {
    background: linear-gradient(90deg, #ff7d00, #ffb338);
    border-radius: 18px; padding: 16px 0; color: #522f00 !important; font-weight: 700;
    font-size: 1.28rem; border: none; width: 100%; margin-top: 22px; cursor: pointer;
    transition: background 0.3s ease, box-shadow 0.3s ease; box-shadow: 0 7px 22px #ffa53bcc;
}
.action-btn:hover { background: linear-gradient(90deg, #e56e00, #db9f2d); box-shadow: 0 12px 36px #ffb95bcc; }
.clear-btn { background-color: #a6732cdd !important; color: #fbe9cd !important; font-size: 1.05rem; font-weight: 600; border-radius: 14px; padding: 10px 22px; border: none; cursor: pointer; transition: background-color 0.3s ease; margin-top: 18px; }
.clear-btn:hover { background-color: #9e5c00cc !important; }

/* Output cards */
.output-card {
    background: #fff9f0; border-radius: 22px; box-shadow: 0 16px 48px #ff9b2b5e; padding: 32px 28px 28px; margin-bottom: 34px;
    font-size: 1.22rem; color: #7a4d00; line-height: 1.6;
}
.output-title { font-weight: 800; font-size: 1.36rem; margin-bottom: 18px; color: #ff7f23; }

/* Audio title */
.audio-title { font-size: 1.38rem; font-weight: 800; color: #ff9123; text-align: center; margin-bottom: 22px; }

/* Responsive */
@media (max-width: 720px) { .container { margin: 24px 24px 48px; padding: 32px 28px 24px; } .header-title { font-size: 2.6rem; } .action-btn { font-size: 1.16rem; } }
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "source_lang" not in st.session_state: st.session_state.source_lang = "English"
if "target_lang" not in st.session_state: st.session_state.target_lang = "Hindi"
if "text_input" not in st.session_state: st.session_state.text_input = ""
if "translated_text" not in st.session_state: st.session_state.translated_text = ""
if "phonetic_text" not in st.session_state: st.session_state.phonetic_text = ""

# ---------- Header ----------
st.markdown("""
<div class="header">
    <div class="header-title">AI Translator Pro</div>
    <div class="header-badge">PRO</div>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Translate across languages with phonetics & audio playback.</div>', unsafe_allow_html=True)
st.markdown('<div class="container">', unsafe_allow_html=True)

# ---------- Language Selection ----------
lang_map = {
    "English": "en", "French": "fr", "Spanish": "es", "German": "de", "Italian": "it", "Portuguese": "pt",
    "Russian": "ru", "Japanese": "ja", "Korean": "ko", "Chinese (Mandarin)": "zh-cn", "Arabic": "ar",
    "Turkish": "tr", "Dutch": "nl", "Greek": "el", "Polish": "pl", "Swedish": "sv",
    "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Kannada": "kn", "Malayalam": "ml", "Gujarati": "gu",
    "Marathi": "mr", "Punjabi": "pa", "Bengali": "bn", "Urdu": "ur", "Odia": "or"
}
sorted_langs = sorted(lang_map.keys())
col1, col_swap, col3 = st.columns([3.7, 0.5, 3.7])
with col1: st.session_state.source_lang = st.selectbox("From", sorted_langs, index=sorted_langs.index(st.session_state.source_lang))
with col_swap:
    st.markdown('<div style="margin-top:20px;text-align:center;">', unsafe_allow_html=True)
    if st.button("⇄", key="swap", help="Swap languages"):
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with col3: st.session_state.target_lang = st.selectbox("To", sorted_langs, index=sorted_langs.index(st.session_state.target_lang))

# ---------- Text Input ----------
st.session_state.text_input = st.text_area("Text to translate", value=st.session_state.text_input, height=120, placeholder="Type or paste your text here...")

# ---------- Action Buttons ----------
clear_col, translate_col = st.columns([1, 5])
with clear_col:
    if st.button("Clear", key="clear", help="Clear input", use_container_width=True):
        st.session_state.text_input = ""
        st.session_state.translate_
