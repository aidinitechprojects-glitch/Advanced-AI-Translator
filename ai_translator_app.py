import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------- Page Config ----------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")

st.markdown("""
<style>
/* Background deep dark with subtle radial gradient */
body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, #0a0a0a, #111820);
    color: #cce6ff;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    -webkit-font-smoothing: antialiased;
    user-select: none;
}

/* Main container with smooth rounded corners and neon blue glow */
.container {
    background: #121520;
    border-radius: 20px;
    padding: 44px 50px 38px;
    max-width: 720px;
    margin: 48px auto 64px;
    box-shadow: 0 0 25px #00f2ff80, 0 20px 40px #000a11cc;
    border: 1.6px solid #00e9ff9a;
    backdrop-filter: saturate(180%) blur(12px);
}

/* Header with neon cyan gradient text */
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}
.header-title {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00f0ff, #0051bb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.06em;
    user-select: none;
}
.header-badge {
    background: #00dbff;
    color: #0c111b;
    font-weight: 700;
    padding: 8px 28px;
    font-size: 1.15rem;
    border-radius: 14px;
    box-shadow: 0 0 25px #00f2ffcc;
    user-select: none;
}

/* Subtitle with soft pastel cyan */
.subtitle {
    margin-top: 6px;
    margin-bottom: 40px;
    font-weight: 500;
    font-size: 1.24rem;
    color: #7ae8ffcc;
    user-select: none;
}

/* Selectbox */
.stSelectbox > div:first-child {
    font-weight: 600;
    font-size: 1.1rem;
    color: #72cee8ff;
}
.stSelectbox > div[role="listbox"] > div {
    font-size: 1.03rem;
    color: #a4dbfaff;
}

/* Textarea with dark navy bg and bright cyan border/glow on focus */
textarea {
    font-size: 1.17rem !important;
    line-height: 1.5 !important;
    padding: 20px !important;
    background-color: #192431 !important;
    color: #a6dbff !important;
    border-radius: 16px !important;
    border: 2px solid #2caaff !important;
    box-shadow: none !important;
    transition: border-color 0.25s ease, background-color 0.25s ease;
    min-height: 110px !important;
    resize: vertical !important;
}
textarea:focus {
    outline: none !important;
    background-color: #0e1a28 !important;
    border-color: #00f1ff !important;
    box-shadow: 0 0 12px 3px #00d4ffe8 !important;
}

/* Swap button with glowing cyan */
.swap-btn {
    width: 50px;
    height: 50px;
    background: #0087c0;
    font-size: 28px;
    color: #ceffff;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: auto;
    user-select: none;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    box-shadow: 0 0 8px #00e2ff99;
}
.swap-btn:hover {
    transform: scale(1.18);
    box-shadow: 0 0 20px #00fbffff;
}

/* Action buttons with vibrant cyan to deep blue gradient */
.action-btn {
    background: linear-gradient(90deg, #00f5ff, #006acc);
    border-radius: 18px;
    padding: 16px 0;
    color: #e0ffff !important;
    font-weight: 700;
    font-size: 1.28rem;
    border: none;
    width: 100%;
    margin-top: 22px;
    cursor: pointer;
    user-select: none;
    transition: background 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 7px 22px #00bfffbb;
}
.action-btn:hover {
    background: linear-gradient(90deg, #00bbff, #004f9a);
    box-shadow: 0 12px 36px #00dfffcc;
}

/* Clear button with mild dark background */
.clear-btn {
    background-color: #34637cdd !important;
    color: #c3e6f7dd !important;
    font-size: 1.05rem;
    font-weight: 600;
    border-radius: 14px;
    padding: 10px 24px;
    border: none;
    cursor: pointer;
    user-select: none;
    transition: background-color 0.3s ease;
    margin-top: 18px;
}
.clear-btn:hover {
    background-color: #2073a0dd !important;
}

/* Output cards with rich navy background and bright text */
.output-card {
    background: #0f172a;
    border-radius: 22px;
    box-shadow: 0 20px 40px #006d8999;
    padding: 32px 28px 28px;
    margin-bottom: 34px;
    font-size: 1.22rem;
    color: #a5e3ff;
    user-select: text;
    line-height: 1.6;
}
.output-title {
    font-weight: 800;
    font-size: 1.36rem;
    margin-bottom: 18px;
    color: #00dffc;
    user-select: none;
}

/* Audio title in neon cyan */
.audio-title {
    font-size: 1.38rem;
    font-weight: 800;
    color: #00eaff;
    text-align: center;
    margin-bottom: 22px;
    user-select: none;
}

/* Responsive */
@media (max-width: 720px) {
    .container {
        margin: 24px 18px 48px;
        padding: 32px 28px 24px;
    }
    .header-title {
        font-size: 2.6rem;
    }
    .action-btn {
        font-size: 1.16rem;
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
st.markdown('<div class="subtitle">Translate across languages with phonetics & audio playback — powered by sleek iqoo Neo 9 Pro colors.</div>', unsafe_allow_html=True)

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
st.session_state.text_input = st.text_area("Text to translate", value=st.session_state.text_input, height=120, placeholder="Type or paste your text here...")

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
