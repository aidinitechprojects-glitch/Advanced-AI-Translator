import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------- Page Config ----------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")

# ---------- CSS Styling ----------
st.markdown("""
<style>
body, [data-testid="stAppViewContainer"] {background: linear-gradient(135deg, #fff8f1 0%, #ffe5d1 100%); color: #4a4030; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
.container {background: #fffaf3; border-radius: 18px; padding: 30px 36px 28px; max-width: 720px; margin: 32px auto 48px; box-shadow: 0 10px 35px rgba(255, 135, 0, 0.25); border: 1.5px solid #ffd8a0;}
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.header-title { font-size: 2.2rem; font-weight: 800; color: #e66c02; letter-spacing: 0.04em; }
.header-badge { background-color: #ff7f23; color: white; font-weight: 700; padding: 5px 20px; font-size: 1rem; border-radius: 14px; box-shadow: 0 0 22px #ffB84eaa; }
.subtitle { margin-top: 4px; margin-bottom: 28px; font-weight: 600; font-size: 1.05rem; }
textarea { font-size: 1.0rem !important; line-height: 1.4 !important; padding: 14px !important; background-color: #fff6e9 !important; color: #7a4d00 !important; border-radius: 14px !important; border: 2px solid #ffaf52 !important; min-height: 90px !important; resize: vertical !important;}
textarea:focus { outline: none !important; background-color: #fff5db !important; border-color: #ff8a1e !important; box-shadow: 0 0 10px 4px #ff9c1e95 !important;}
.swap-btn { width: 45px; height: 45px; background: #ff7f23; font-size: 24px; color: white; border-radius: 50%; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; margin: auto; transition: transform 0.24s ease, box-shadow 0.24s ease; box-shadow: 0 0 10px #ffb14dcc; }
.swap-btn:hover { transform: scale(1.15); box-shadow: 0 0 22px #ffb14ddd; }
.action-btn { background: linear-gradient(90deg, #ff7d00, #ffb338); border-radius: 14px; padding: 12px 0; color: #522f00 !important; font-weight: 700; font-size: 1.1rem; border: none; width: 100%; margin-top: 16px; cursor: pointer; transition: background 0.3s ease, box-shadow 0.3s ease; box-shadow: 0 5px 18px #ffa53bcc; }
.action-btn:hover { background: linear-gradient(90deg, #e56e00, #db9f2d); box-shadow: 0 10px 28px #ffb95bcc; }
.clear-btn { background-color: #a6732cdd !important; color: #fbe9cd !important; font-size: 0.95rem; font-weight: 600; border-radius: 12px; padding: 8px 18px; border: none; cursor: pointer; transition: background-color 0.3s ease; margin-top: 14px; }
.clear-btn:hover { background-color: #9e5c00cc !important; }
.output-card { background: #fff9f0; border-radius: 18px; box-shadow: 0 12px 38px #ff9b2b5e; padding: 24px 20px 22px; margin-bottom: 28px; font-size: 1.05rem; color: #7a4d00; line-height: 1.5; }
.output-title { font-weight: 700; font-size: 1.18rem; margin-bottom: 12px; color: #ff7f23; }
.audio-title { font-size: 1.2rem; font-weight: 700; color: #ff9123; text-align: center; margin-bottom: 18px; }
@media (max-width: 720px) { .container { margin: 24px 24px 48px; padding: 28px 24px 20px; } .header-title { font-size: 2rem; } .action-btn { font-size: 1rem; } }
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
col1, col_swap, col2 = st.columns([3.7, 0.5, 3.7])
with col1: st.session_state.source_lang = st.selectbox("From", sorted_langs, index=sorted_langs.index(st.session_state.source_lang))
with col_swap:
    if st.button("⇄", key="swap", help="Swap languages"): 
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
with col2: st.session_state.target_lang = st.selectbox("To", sorted_langs, index=sorted_langs.index(st.session_state.target_lang))

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

# ---------- Translation ----------
openai.api_key = st.secrets["OPENAI_API_KEY"]
if translate_clicked:
    if not st.session_state.text_input.strip():
        st.warning("⚠️ Please enter text to translate.")
    else:
        with st.spinner("Translating…"):
            translate_prompt = f"Translate this text from {st.session_state.source_lang} to {st.session_state.target_lang}. ONLY raw translation, no explanation:\n{st.session_state.text_input}"
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
    st.markdown(f'<div class="output-card"><div class="output-title">🌐 Translation</div>{st.session_state.translated_text}</div>', unsafe_allow_html=True)
if st.session_state.phonetic_text:
    st.markdown(f'<div class="output-card"><div class="output-title">🔤 Phonetic</div>{st.session_state.phonetic_text}</div>', unsafe_allow_html=True)

# ---------- Audio ----------
if st.session_state.translated_text:
    st.markdown('<div class="audio-title">🔊 Audio Playback</div>', unsafe_allow_html=True)
    try:
        tts_lang = lang_map.get(st.session_state.target_lang, "en")
        tts = gTTS(text=st.session_state.translated_text, lang=
