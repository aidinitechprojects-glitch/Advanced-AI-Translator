import streamlit as st
from gtts import gTTS
import openai
import tempfile
import streamlit.components.v1 as components

# ---------- Page Config ----------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")

# ---------- CSS ----------
st.markdown("""
<style>
body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #fdf6f0 0%, #ffe7d2 100%);
    color: #3b2f2f;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.pro-container {
    background: rgba(255,255,255,0.95);
    border-radius: 22px;
    padding: 32px 36px 28px 36px;
    max-width: 700px;
    margin: 36px auto 48px;
    box-shadow: 0 16px 36px rgba(255, 135, 0, 0.25);
    border: 1.5px solid #ffc58f;
}
.pro-header {
    display:flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.pro-title {
    font-size:2.4rem;
    font-weight:900;
    letter-spacing:.03em;
    background:linear-gradient(90deg,#ff7a18,#af002d 70%);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.pro-badge {
    background: linear-gradient(90deg,#af002d,#ff7a18 95%);
    color:#fff;
    font-weight:700;
    padding:5px 18px;
    font-size:1.05rem;
    border-radius:12px;
    box-shadow:0 1px 8px #af002d33;
}
.pro-subtitle {
    font-size:1.15rem;
    color:#5a4233;
    margin-bottom:28px;
}
textarea {
    font-size:1.13rem !important;
    padding:16px !important;
    background:#fff8f2 !important;
    color:#422d20 !important;
    border-radius:16px !important;
    border:2px solid #ffb66d !important;
    transition: all 0.3s ease;
    min-height:100px !important;
}
textarea:focus {
    outline:none !important;
    border-color:#ff8c1f !important;
    background:#fff6e5 !important;
    box-shadow:0 0 12px #ff9d33aa !important;
}
.pro-btn {
    width:100%;
    padding:0.7em 0;
    margin-top:14px;
    background: linear-gradient(90deg,#ff7d00,#ffb338);
    color:#fff;
    font-size:1.17rem;
    font-weight:bold;
    border:none;
    border-radius:14px;
    box-shadow:0 5px 18px #ffb24b44;
    cursor:pointer;
    transition: all 0.2s ease;
}
.pro-btn:hover {
    filter: brightness(1.12);
    box-shadow:0 7px 22px #ffb24b55;
}
.pro-out-card {
    background: #fff7ed;
    border-radius:18px;
    padding:20px 16px 16px;
    box-shadow:0 3px 16px #ffb57d44;
    margin-bottom:18px;
    position:relative;
}
.pro-out-title {
    font-weight:700;
    font-size:1.12rem;
    color:#ff7a18;
    margin-bottom:8px;
}
.pro-out {
    font-size:1.05rem;
    color:#3b2f2f;
    line-height:1.5;
    word-break: break-word;
}
.copy-btn {
    position:absolute;
    top:16px;
    right:16px;
    background:#ff7a18;
    color:white;
    border:none;
    padding:5px 12px;
    border-radius:8px;
    cursor:pointer;
    transition: all 0.2s ease;
}
.copy-btn:hover {
    background:#e56e00;
}
.audio-title {
    font-weight:700;
    font-size:1.12rem;
    color:#ff7a18;
    text-align:center;
    margin-bottom:12px;
}
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
st.markdown("<div class='pro-subtitle'>Translate across languages with phonetics & audio playback.</div>", unsafe_allow_html=True)

st.markdown('<div class="pro-container">', unsafe_allow_html=True)

# ---------- Language Selection ----------
lang_map = {
    "Hindi":"hi","Tamil":"ta","Telugu":"te","Kannada":"kn","Malayalam":"ml",
    "Gujarati":"gu","Marathi":"mr","Punjabi":"pa","Bengali":"bn","Urdu":"ur",
    "Odia":"or","English":"en","French":"fr","Spanish":"es","German":"de",
    "Italian":"it","Portuguese":"pt","Russian":"ru","Japanese":"ja",
    "Korean":"ko","Chinese (Mandarin)":"zh-cn","Arabic":"ar","Turkish":"tr",
    "Dutch":"nl","Greek":"el","Polish":"pl","Swedish":"sv",
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
st.session_state.text_input = st.text_area("Text to translate", value=st.session_state.text_input, height=100, placeholder="Type or paste something...")

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
        response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":st.session_state.text_input}])
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
    st
