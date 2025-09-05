import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------- Page Config ----------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")

st.markdown("""
<style>
/* Background: subtle smooth gradient */
body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    color: #1f2937;
    font-family: 'Open Sans', Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* Main container with soft shadow and rounded corners */
.container {
    background: #ffffff;
    border-radius: 18px;
    padding: 42px 48px 36px;
    max-width: 700px;
    margin: 48px auto 64px;
    box-shadow: 0 8px 24px rgba(148, 163, 184, 0.25);
}

/* Header */
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.header-title {
    font-size: 2.8rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: #111827;
    user-select: none;
}
.header-badge {
    background-color: #2563eb;
    color: white;
    font-weight: 600;
    padding: 6px 22px;
    font-size: 1.1rem;
    border-radius: 12px;
    user-select: none;
}

/* Subtitle */
.subtitle {
    margin-top: 6px;
    margin-bottom: 36px;
    font-weight: 500;
    font-size: 1.15rem;
    color: #4b5563;
    user-select: none;
}

/* Selectbox labels and list items */
.stSelectbox > div:first-child {
    font-weight: 600;
    font-size: 1.1rem;
    color: #1f2937;
}
.stSelectbox > div[role="listbox"] > div {
    font-size: 1.0rem;
    color: #374151;
}

/* Textarea */
textarea {
    font-size: 1.12rem !important;
    line-height: 1.5 !important;
    padding: 18px !important;
    background-color: #f9fafb !important;
    color: #111827 !important;
    border-radius: 14px !important;
    border: 1.8px solid #d1d5db !important;
    box-shadow: none !important;
    transition: border-color 0.3s ease, background-color 0.3s ease;
    min-height: 110px !important;
    resize: vertical !important;
}
textarea:focus {
    outline: none !important;
    background-color: #ffffff !important;
    border-color: #2563eb !important;
    box-shadow: 0 0 8px 2px #bfdbfe !important;
}

/* Swap Button */
.swap-btn {
    width: 44px;
    height: 44px;
    background-color: #2563eb;
    font-size: 22px;
    color: #ffffff;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: auto;
    user-select: none;
    transition: background-color 0.2s ease;
}
.swap-btn:hover {
    background-color: #1d4ed8;
}

/* Action Buttons */
.action-btn {
    background-color: #2563eb;
    border-radius: 14px;
    padding: 14px 0;
    color: white !important;
    font-weight: 600;
    font-size: 1.15rem;
    border: none;
    width: 100%;
    margin-top: 20px;
    cursor: pointer;
    user-select: none;
    transition: background-color 0.3s ease;
}
.action-btn:hover {
    background-color: #1d4ed8;
}

/* Clear Button */
.clear-btn {
    background-color: #6b7280 !important;
    color: white !important;
    font-size: 1.0rem;
    font-weight: 600;
    border-radius: 12px;
    padding: 8px 20px;
    border: none;
    cursor: pointer;
    user-select: none;
    transition: background-color 0.3s ease;
    margin-top: 16px;
}
.clear-btn:hover {
    background-color: #4b5563 !important;
}

/* Output Cards */
.output-card {
    background-color: #f3f4f6;
    border-radius: 18px;
    padding: 26px 24px 22px;
    margin-bottom: 32px;
    font-size: 1.12rem;
    color: #1e293b;
    user-select: text;
    line-height: 1.6;
}
.output-title {
    font-weight: 700;
    font-size: 1.25rem;
    margin-bottom: 14px;
    color: #2563eb;
    user-select: none;
}

/* Audio Playback Title */
.audio-title {
    font-size: 1.28rem;
    font-weight: 700;
    color: #2563eb;
    text-align: center;
    margin-bottom: 20px;
    user-select: none;
}

/* Responsive */
@media (max-width: 700px) {
    .container {
        margin: 24px 18px 48px;
        padding: 32px 28px 24px;
    }
    .header-title {
        font-size: 2.4rem;
    }
    .action-btn {
        font-size: 1.05rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "source_lang" not in st.session_state:
    st.session_state.source_lang = "English"
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Hindi"
if "text_input" not in st.session_state:
    st.session_state.text_input = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "phonetic_text" not in st.session_state:
    st.session_state.phonetic_text = ""

# ---------- Header ----------
st.markdown("""
<div class="header">
    <div class="header-title">AI Translator Pro</div>
    <div class="header-badge">PRO</div>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Translate text across languages with phonetics & audio playback.</div>', unsafe_allow_html=True)

st.markdown('<div class="container">', unsafe_allow_html=True)

# ---------- Language Selection with Swap Button ----------
lang_map = {
    "English": "en", "French": "fr", "Spanish": "es", "German": "de", "Italian": "it", "Portuguese": "pt",
    "Russian": "ru", "Japanese": "ja", "Korean": "ko", "Chinese (Mandarin)": "zh-cn", "Arabic": "ar",
    "Turkish": "tr", "Dutch": "nl", "Greek": "el", "Polish": "pl", "Swedish": "sv",
    "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Kannada": "kn", "Malayalam": "ml", "Gujarati": "gu",
    "Marathi": "mr", "Punjabi": "pa", "Bengali": "bn", "Urdu": "ur", "Odia": "or"
}
sorted_langs = sorted(lang_map.keys())

col1, col_swap, col3 = st.columns([3.7, 0.5, 3.7])

with col1:
    st.session_state.source_lang = st.selectbox("From", sorted_langs, index=sorted_langs.index(st.session_state.source_lang))

with col_swap:
    st.markdown('<div style="margin-top:20px;text-align:center;">', unsafe_allow_html=True)
    if st.button("⇆", key="swap", help="Swap languages"):
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.session_state.target_lang = st.selectbox("To", sorted_langs, index=sorted_langs.index(st.session_state.target_lang))

# ---------- Text Input ----------
st.session_state.text_input = st.text_area("Text to translate", value=st.session_state.text_input, height=100, placeholder="Type or paste your text here...")

# ---------- Action Buttons ----------
clear_col, translate_col = st.columns([1, 5])

with clear_col:
    if st.button("Clear", key="clear", help="Clear input", use_container_width=True):
        st.session_state.text_input = ""
        st.session_state.translated_text = ""
        st.session_state.phonetic_text = ""
        st.experimental_rerun()

with translate_col:
    translate_clicked = st.button("Translate", key="translate", help="Translate text", use_container_width=True)

# ---------- Translation Logic (Unchanged) ----------
openai.api_key = st.secrets["OPENAI_API_KEY"]

if translate_clicked:
    if not st.session_state.text_input.strip():
        st.warning("⚠️ Please enter text to translate.")
    else:
        with st.spinner("Translating…"):
            translate_prompt = f"Translate this text from {st.session_state.source_lang} to {st.session_state.target_lang}:\n{st.session_state.text_input}"
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": translate_prompt}]
            )
            st.session_state.translated_text = response.choices[0].message.content.strip()

            phonetic_prompt = f"Provide phonetic (romanized) transcription of this {st.session_state.target_lang} text:\n{st.session_state.translated_text}"
            phonetic_resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": phonetic_prompt}]
            )
            st.session_state.phonetic_text = phonetic_resp.choices[0].message.content.strip()

# ---------- Outputs ----------
if st.session_state.translated_text:
    st.markdown(
        f'<div class="output-card"><div class="output-title">🌐 Translation</div>{st.session_state.translated_text}</div>',
        unsafe_allow_html=True)
if st.session_state.phonetic_text:
    st.markdown(
        f'<div class="output-card"><div class="output-title">🔤 Phonetic</div>{st.session_state.phonetic_text}</div>',
        unsafe_allow_html=True)

if st.session_state.translated_text:
    st.markdown('<div class="audio-title">🔊 Audio Playback</div>', unsafe_allow_html=True)
    try:
        tts_lang = lang_map.get(st.session_state.target_lang, "en")
        tts = gTTS(text=st.session_state.translated_text, lang=tts_lang)
        tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tts_file.name)
        st.audio(tts_file.name, format="audio/mp3")
    except Exception as e:
        st.error(f"❌ Speech generation failed: {e}")

st.markdown('</div>', unsafe_allow_html=True)
