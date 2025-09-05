import streamlit as st
from gtts import gTTS
import openai
import tempfile
import streamlit.components.v1 as components

# ---------- Page Config ----------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")

# ---------- CSS Styling ----------
st.markdown("""
<style>
body, [data-testid="stAppViewContainer"] {background:linear-gradient(135deg,#fff8f1 0%,#ffe5d1 100%);color:#4a4030;font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
.container {background:#fffaf3;border-radius:22px;padding:36px 32px 32px;max-width:720px;margin:24px auto;box-shadow:0 10px 40px rgba(255,135,0,0.25);border:1.5px solid #ffd8a0;}
.header {display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;}
.header-title {font-size:2.4rem;font-weight:800;color:#e66c02;letter-spacing:0.04em;}
.header-badge {background-color:#ff7f23;color:white;font-weight:700;padding:6px 22px;font-size:1.05rem;border-radius:14px;box-shadow:0 0 22px #ffB84eaa;}
.subtitle {margin-top:4px;margin-bottom:28px;font-weight:600;font-size:1.18rem;color:#a15303cc;}
textarea {font-size:1.15rem !important;line-height:1.5 !important;padding:16px !important;background-color:#fff6e9 !important;color:#7a4d00 !important;border-radius:14px !important;border:2px solid #ffaf52 !important;min-height:100px !important;resize:vertical !important;}
textarea:focus {outline:none !important;background-color:#fff5db !important;border-color:#ff8a1e !important;box-shadow:0 0 12px 4px #ff9c1e95 !important;}
.swap-btn {width:45px;height:45px;background:#ff7f23;font-size:26px;color:white;border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;margin:auto;transition:transform 0.22s ease,box-shadow 0.22s ease;box-shadow:0 0 10px #ffb14dcc;}
.swap-btn:hover {transform:scale(1.15);box-shadow:0 0 24px #ffb14ddd;}
.action-btn {background:linear-gradient(90deg,#ff7d00,#ffb338);border-radius:16px;padding:14px 0;color:#522f00 !important;font-weight:700;font-size:1.22rem;border:none;width:100%;margin-top:18px;cursor:pointer;transition:background 0.3s ease,box-shadow 0.3s ease;box-shadow:0 5px 18px #ffa53bcc;}
.action-btn:hover {background:linear-gradient(90deg,#e56e00,#db9f2d);box-shadow:0 10px 28px #ffb95bcc;}
.clear-btn {background-color:#a6732cdd !important;color:#fbe9cd !important;font-size:1rem;font-weight:600;border-radius:12px;padding:8px 20px;border:none;cursor:pointer;margin-top:14px;}
.clear-btn:hover {background-color:#9e5c00cc !important;}
.output-box {background:#fff9f0;border-radius:18px;border:1.5px solid #ffb350;padding:24px 20px 20px;margin-bottom:20px;position:relative;font-size:1.18rem;color:#7a4d00;line-height:1.55;}
.output-title {font-weight:700;font-size:1.3rem;margin-bottom:12px;color:#ff7f23;}
.copy-btn {position:absolute;top:16px;right:16px;background:#ffb338;border:none;border-radius:10px;padding:5px 10px;font-size:0.85rem;color:#522f00;cursor:pointer;transition:filter 0.2s;}
.copy-btn:hover {filter:brightness(1.15);}
.copied-feedback {position:absolute;top:16px;right:68px;color:#ff7f23;font-weight:700;font-size:0.9rem;}
.audio-title {font-size:1.3rem;font-weight:700;color:#ff9123;text-align:center;margin-bottom:16px;}
@media (max-width:720px){.container{margin:16px 16px 32px;padding:28px 24px 24px;}.header-title{font-size:2.2rem;}.action-btn{font-size:1.12rem;}}
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "source_lang" not in st.session_state: st.session_state.source_lang = "English"
if "target_lang" not in st.session_state: st.session_state.target_lang = "Hindi"
if "text_input" not in st.session_state: st.session_state.text_input = ""
if "translated_text" not in st.session_state: st.session_state.translated_text = ""
if "phonetic_text" not in st.session_state: st.session_state.phonetic_text = ""
if "copy_feedback" not in st.session_state: st.session_state.copy_feedback = ""

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
col1, col_swap, col3 = st.columns([3.7,0.5,3.7])

with col1:
    st.session_state.source_lang = st.selectbox("From", sorted_langs, index=sorted_langs.index(st.session_state.source_lang))
with col_swap:
    st.markdown('<div style="margin-top:20px;text-align:center;">', unsafe_allow_html=True)
    if st.button("⇆", key="swap"):
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    st.session_state.target_lang = st.selectbox("To", sorted_langs, index=sorted_langs.index(st.session_state.target_lang))

# ---------- Text Input ----------
st.session_state.text_input = st.text_area("Text to translate", value=st.session_state.text_input, height=120, placeholder="Type or paste your text here...")

# ---------- Action Buttons ----------
clear_col, translate_col = st.columns([1,5])
with clear_col:
    if st.button("Clear", key="clear"):
        st.session_state.text_input = ""
        st.session_state.translated_text = ""
        st.session_state.phonetic_text = ""
        st.session_state.copy_feedback = ""
        st.experimental_rerun()
with translate_col:
    translate_clicked = st.button("Translate", key="translate")

# ---------- Translation ----------
openai.api_key = st.secrets["OPENAI_API_KEY"]

if translate_clicked and st.session_state.text_input.strip():
    with st.spinner("Translating…"):
        prompt_translate = f"Translate the following text from {st.session_state.source_lang} to {st.session_state.target_lang}. ONLY output raw translation:\n{st.session_state.text_input}"
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt_translate}]
        )
        st.session_state.translated_text = response.choices[0].message.content.strip()

        prompt_phonetic = f"Provide phonetic (romanized) transcription of this {st.session_state.target_lang} text. ONLY raw output:\n{st.session_state.translated_text}"
        phonetic_resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt_phonetic}]
        )
        st.session_state.phonetic_text = phonetic_resp.choices[0].message.content.strip()
        st.session_state.copy_feedback = ""

# ---------- Output with Copy ----------
def output_with_copy(title, text, key_suffix):
    if text:
        container_html = f"""
        <div class="output-box">
            <div class="output-title">{title}</div>
            {text}
            <button class="copy-btn" onclick="navigator.clipboard.writeText(`{text}`).then(() => {{
                const fb = document.getElementById('feedback_{key_suffix}');
                fb.style.display='inline';
                setTimeout(()=>{{fb.style.display='none';}},1500);
            }})">Copy</button>
            <span id="feedback_{key_suffix}" class="copied-feedback" style="display:none;">Copied!</span>
        </div>
        """
        components.html(container_html, height=150)

# ---------- Show Outputs ----------
output_with_copy("🌐 Translation", st.session_state.translated_text, "trans")
output_with_copy("🔤 Phonetic", st.session_state.phonetic_text, "phon")

# ---------- Audio Playback ----------
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
