import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------- Page Config ----------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")

# ---------- Styles ----------
st.markdown("""
<style>
body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #fff8f1 0%, #ffe5d1 100%);
    color: #4a4030;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    -webkit-font-smoothing: antialiased;
    user-select: none;
}

.container {
    background: #fffaf3;
    border-radius: 18px;
    padding: 28px 32px 24px;
    max-width: 680px;
    margin: 32px auto 48px;
    box-shadow: 0 10px 35px rgba(255, 135, 0, 0.35);
    border: 1.6px solid #ffd8a0;
}

.header {display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;}
.header-title {font-size:2.4rem; font-weight:800; color:#e66c02; letter-spacing:.03em; user-select:none;}
.header-badge {background-color:#ff7f23; color:white; font-weight:700; padding:5px 22px; font-size:1rem; border-radius:14px; box-shadow:0 0 18px #ffB84eaa; user-select:none;}
.subtitle {margin-top:4px; margin-bottom:28px; font-weight:600; font-size:1.1rem; color:#a15303cc; user-select:none;}

.stSelectbox > div:first-child {font-weight:600; font-size:1rem; color:#bf6e12cc;}
.stSelectbox > div[role="listbox"] > div {font-size:0.96rem; color:#d8922ecc;}

textarea {
    font-size:1rem !important; line-height:1.4 !important; padding:14px !important;
    background-color:#fff6e9 !important; color:#7a4d00 !important;
    border-radius:14px !important; border:2px solid #ffaf52 !important;
    box-shadow:none !important; transition:border-color 0.3s ease, background-color 0.3s ease;
    min-height:90px !important; resize:vertical !important;
}
textarea:focus {outline:none !important; background-color:#fff5db !important; border-color:#ff8a1e !important; box-shadow:0 0 10px 4px #ff9c1e80 !important;}

.swap-btn {width:40px; height:40px; background:#ff7f23; font-size:24px; color:white; border-radius:50%; border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; margin:auto; user-select:none; transition:transform .24s ease, box-shadow .24s ease; box-shadow:0 0 10px #ffb14dcc;}
.swap-btn:hover {transform:scale(1.15); box-shadow:0 0 20px #ffb14ddd;}

.action-btn {background: linear-gradient(90deg,#ff7d00,#ffb338); border-radius:14px; padding:14px 0; color:#522f00 !important; font-weight:700; font-size:1.14rem; border:none; width:100%; margin-top:18px; cursor:pointer; user-select:none; transition:background 0.3s ease, box-shadow 0.3s ease; box-shadow:0 5px 18px #ffa53bcc;}
.action-btn:hover {background: linear-gradient(90deg,#e56e00,#db9f2d); box-shadow:0 10px 28px #ffb95bcc;}

.clear-btn {background-color:#a6732cdd !important; color:#fbe9cd !important; font-size:0.95rem; font-weight:600; border-radius:12px; padding:8px 18px; border:none; cursor:pointer; user-select:none; transition: background-color .3s ease; margin-top:12px;}
.clear-btn:hover {background-color:#9e5c00cc !important;}

.output-card {background:#fff9f0; border-radius:18px; box-shadow:0 12px 38px #ff9b2b50; padding:22px 18px 18px; margin-bottom:24px; font-size:1rem; color:#7a4d00; user-select:text; line-height:1.4; position:relative;}
.output-title {font-weight:700; font-size:1.1rem; margin-bottom:10px; color:#ff7f23; user-select:none;}

.copy-btn {position:absolute; top:10px; right:10px; background:#ff7f23; color:white; border:none; border-radius:10px; padding:4px 10px; font-size:0.85rem; cursor:pointer;}
.copy-btn:hover {background:#e66c02;}

.audio-title {font-size:1.2rem; font-weight:700; color:#ff9123; text-align:center; margin-bottom:18px; user-select:none;}
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "source_lang" not in st.session_state: st.session_state.source_lang = "English"
if "target_lang" not in st.session_state: st.session_state.target_lang = "Hindi"
if "text_input" not in st.session_state: st.session_state.text_input = ""
if "translated_text" not in st.session_state: st.session_state.translated_text = ""
if "phonetic_text" not in st.session_state: st.session_state.phonetic_text = ""

# ---------- Header ----------
st.markdown(f"""
<div class="header">
    <div class="header-title">AI Translator Pro</div>
    <div class="header-badge">PRO</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="subtitle">Translate text across languages with phonetics & audio playback.</div>', unsafe_allow_html=True)

st.markdown('<div class="container">', unsafe_allow_html=True)

# ---------- Language Selection ----------
lang_map = {
    "English": "en", "French": "fr", "Spanish": "es", "German": "de", "Italian": "it",
    "Portuguese": "pt", "Russian": "ru", "Japanese": "ja", "Korean": "ko", "Chinese (Mandarin)": "zh-cn",
    "Arabic": "ar", "Turkish": "tr", "Dutch": "nl", "Greek": "el", "Polish": "pl", "Swedish": "sv",
    "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Kannada": "kn", "Malayalam": "ml",
    "Gujarati": "gu", "Marathi": "mr", "Punjabi": "pa", "Bengali": "bn", "Urdu": "ur", "Odia": "or"
}
sorted_langs = sorted(lang_map.keys())

col1, col_swap, col3 = st.columns([3.7, 0.5, 3.7])
with col1:
    st.session_state.source_lang = st.selectbox("From", sorted_langs, index=sorted_langs.index(st.session_state.source_lang))
with col_swap:
    if st.button("⇆", key="swap"):
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
with col3:
    st.session_state.target_lang = st.selectbox("To", sorted_langs, index=sorted_langs.index(st.session_state.target_lang))

# ---------- Text Input ----------
st.session_state.text_input = st.text_area("Text to translate", value=st.session_state.text_input, height=100, placeholder="Type or paste your text here...")

# ---------- Buttons ----------
clear_col, translate_col = st.columns([1,5])
with clear_col:
    if st.button("Clear", key="clear", use_container_width=True):
        st.session_state.text_input = ""
        st.session_state.translated_text = ""
        st.session_state.phonetic_text = ""
        st.experimental_rerun()
with translate_col:
    translate_clicked = st.button("Translate", key="translate", use_container_width=True)

# ---------- Translation Logic ----------
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

            phonetic_prompt = f"Provide phonetic (romanized) transcription of
