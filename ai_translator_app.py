import streamlit as st
from gtts import gTTS
import openai
import tempfile
import streamlit.components.v1 as components

# ---------- Page Config ----------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")

# ---------- CSS (Previous UI) ----------
st.markdown("""
<style>
body, [data-testid="stAppViewContainer"] {background: linear-gradient(120deg,#ece9f3 60%,#fff8ed 115%); color:#4a4030; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
.pro-glass {background:rgba(255,255,255,0.91);border-radius:28px;box-shadow:0 12px 56px 0 #bf7cf328, 0 0.5px 2px #00000012;padding:38px 38px 30px 38px;margin:28px 0 0 0;}
.pro-header {display:flex;align-items:center;justify-content:space-between;margin-bottom:0;}
.pro-title {font-size:2.4rem;font-weight:900;letter-spacing:.03em;background:linear-gradient(90deg,#ff7a18,#af002d 70%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.pro-badge {font-size:1.05rem;background:linear-gradient(90deg,#af002d,#ff7a18 95%);color:#fff;border-radius:8px;padding:4px 20px;margin-left:16px;font-weight:500;box-shadow:0 1px 7px #af002d22;}
.pro-subtitle {font-size:1.13rem;color:#2b2542;font-weight:500;text-align:left;margin-bottom:24px;margin-top:4px;}
textarea {background:rgba(255,245,230,0.97)!important;border-radius:19px!important;font-size:1.11rem;color:#222!important;border:2px solid #ffd6b7!important;box-shadow:0 4px 24px #ff7a1812;}
textarea:focus {border:2.5px solid #ff7a18!important;background:#fff9f0!important;}
.pro-swap-btn {width:44px;height:44px;background:linear-gradient(90deg,#3a86ff,#ff7a18);color:#fff;border-radius:50%;font-size:1.25rem;border:none;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 20px #ff7a1810;transition:filter .2s;}
.pro-swap-btn:hover {filter:brightness(1.13);}
.pro-btn {width:100%;padding:.7em 0;margin-top:13px;background:linear-gradient(90deg,#af002d,#ff7a18 75%);color:#fff;border:none;border-radius:13px;font-size:1.17rem;font-weight:bold;box-shadow:0 5px 18px #ff7a1825;transition:filter .18s,box-shadow .13s;}
.pro-btn:hover {filter:brightness(1.13);}
.clear-btn {background:#857fa4cc!important;color:#fff!important;border-radius:11px;font-size:15px;margin:7px 0 17px 0;}
.pro-out-card {background:rgba(255,245,230,0.98);border-radius:17px;padding:19px 16px 12px 16px;box-shadow:0 3px 13px #ff7a1817;margin-bottom:17px;position:relative;}
.pro-out-title {font-weight:700;font-size:1.047rem;letter-spacing:.01em;color:#af002d;}
.pro-out {font-size:1.07rem;color:#1d1728;margin-bottom:8px;}
.copy-btn {position:absolute;top:16px;right:16px;background:#ff7a18;color:white;border:none;padding:5px 12px;border-radius:8px;cursor:pointer;}
.copy-btn:hover {background:#e56e00;}
.audio-title {font-weight:700;font-size:1.11rem;color:#ff7a18;text-align:center;margin-bottom:8px;}
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
<div class='pro-header'>
  <span class='pro-title'>AI Translator</span>
  <span class='pro-badge'>PRO</span>
</div>
""", unsafe_allow_html=True)
st.markdown("<div class='pro-subtitle'>Premium-style AI translation—text, phonetic, and audio in one click.</div>", unsafe_allow_html=True)
st.markdown('<div class="pro-glass">', unsafe_allow_html=True)

# ---------- Language Selection ----------
lang_map = {
    "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Kannada": "kn", "Malayalam": "ml",
    "Gujarati": "gu", "Marathi": "mr", "Punjabi": "pa", "Bengali": "bn", "Urdu": "ur",
    "Odia": "or", "English": "en", "French": "fr", "Spanish": "es", "German": "de",
    "Italian": "it", "Portuguese": "pt", "Russian": "ru", "Japanese": "ja",
    "Korean": "ko", "Chinese (Mandarin)": "zh-cn", "Arabic": "ar", "Turkish": "tr",
    "Dutch": "nl", "Greek": "el", "Polish": "pl", "Swedish": "sv",
}
sorted_langs = sorted(lang_map.keys())
col1, col_swap, col3 = st.columns([3.5,1,3.5])
with col1:
    st.session_state.source_lang = st.selectbox("From", sorted_langs, index=sorted_langs.index(st.session_state.source_lang))
with col_swap:
    if st.button("⇆"):
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
with col3:
    st.session_state.target_lang = st.selectbox("To", sorted_langs, index=sorted_langs.index(st.session_state.target_lang))

# ---------- Text Input ----------
st.session_state.text_input = st.text_area("Text to translate", value=st.session_state.text_input, height=94, placeholder="Type or paste something...")

# ---------- Action Buttons ----------
clear_col, translate_col = st.columns([1,5])
with clear_col:
    if st.button("Clear"):
        st.session_state.text_input = ""
        st.session_state.translated_text = ""
        st.session_state.phonetic_text = ""
        st.experimental_rerun()
with translate_col:
    translate_clicked = st.button("Translate", key="translate", use_container_width=True)

# ---------- Translation Logic ----------
openai.api_key = st.secrets["OPENAI_API_KEY"]
if translate_clicked and st.session_state.text_input.strip():
    with st.spinner("Translating…"):
        translate_prompt = f"{st.session_state.text_input}"
        response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":translate_prompt}])
        st.session_state.translated_text = response.choices[0].message.content.strip()
        phonetic_resp = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":st.session_state.translated_text}])
        st.session_state.phonetic_text = phonetic_resp.choices[0].message.content.strip()

# ---------- Output with Inline Copy ----------
def output_with_copy(title, text):
    if text:
        html_code = f"""
        <div class="pro-out-card">
            <span class="pro-out-title">{title}</span>
            <div class="pro-out">{text}</div>
            <button class="copy-btn" onclick="
                navigator.clipboard.writeText(`{text}`);
                this.innerText='Copied ✅';
            ">Copy</button>
        </div>
        """
        components.html(html_code, height=130)

output_with_copy("🌐 Translation", st.session_state.translated_text)
output_with_copy("🔤 Phonetic", st.session_state.phonetic_text)

# ---------- Audio ----------
if st.session_state.translated_text:
    st.markdown('<div class="audio-title">🔊 Audio</div>', unsafe_allow_html=True)
    try:
        tts_lang = lang_map.get(st.session_state.target_lang, "en")
        tts = gTTS(text=st.session_state.translated_text, lang=tts_lang)
        tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tts_file.name)
        st.audio(tts_file.name, format="audio/mp3")
    except Exception as e:
        st.error(f"❌ Speech generation failed: {e}")

st.markdown('</div>', unsafe_allow_html=True)
