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
body, [data-testid="stAppViewContainer"] {background: linear-gradient(135deg, #fff8f1 0%, #ffe5d1 100%); color: #4a4030; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
.container {background: #fffaf3; border-radius: 22px; padding: 46px 52px 40px; max-width: 720px; margin: 48px auto 64px; box-shadow: 0 15px 50px rgba(255, 135, 0, 0.35); border: 1.8px solid #ffd8a0;}
.header {display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;}
.header-title {font-size:2.8rem; font-weight:800; color:#e66c02; letter-spacing:0.04em;}
.header-badge {background-color:#ff7f23; color:white; font-weight:700; padding:7px 26px; font-size:1.15rem; border-radius:16px; box-shadow:0 0 28px #ffB84eaa;}
.subtitle {margin-top:6px; margin-bottom:38px; font-weight:600; font-size:1.22rem; color:#a15303cc;}
textarea {font-size:1.05rem !important; line-height:1.4 !important; padding:14px !important; background-color:#fff6e9 !important; color:#7a4d00 !important; border-radius:14px !important; border:2px solid #ffaf52 !important; min-height:90px !important; resize:vertical !important;}
textarea:focus {outline:none !important; background-color:#fff5db !important; border-color:#ff8a1e !important;}
.swap-btn {width:50px; height:50px; background:#ff7f23; font-size:28px; color:white; border-radius:50%; border:none; display:flex; align-items:center; justify-content:center; margin:auto; transition:transform 0.24s ease, box-shadow 0.24s ease; cursor:pointer;}
.swap-btn:hover {transform:scale(1.18); box-shadow:0 0 28px #ffb14ddd;}
.action-btn {background:linear-gradient(90deg,#ff7d00,#ffb338); border-radius:18px; padding:14px 0; color:#522f00; font-weight:700; font-size:1.2rem; border:none; width:100%; margin-top:18px; cursor:pointer; box-shadow:0 7px 22px #ffa53bcc;}
.action-btn:hover {background:linear-gradient(90deg,#e56e00,#db9f2d); box-shadow:0 12px 36px #ffb95bcc;}
.clear-btn {background-color:#a6732cdd; color:#fbe9cd; font-size:1rem; font-weight:600; border-radius:14px; padding:8px 20px; border:none; cursor:pointer; margin-top:14px;}
.clear-btn:hover {background-color:#9e5c00cc;}
.output-card {background:#fff9f0; border-radius:20px; box-shadow:0 16px 48px #ff9b2b5e; padding:24px 20px 20px; font-size:1rem; color:#7a4d00; margin-bottom:28px; line-height:1.5; position:relative;}
.output-title {font-weight:700; font-size:1.2rem; margin-bottom:10px; color:#ff7f23;}
.audio-title {font-size:1.2rem; font-weight:700; color:#ff9123; text-align:center; margin-bottom:18px;}
.copy-btn {background:#ff7f23; color:white; border:none; padding:5px 12px; border-radius:8px; font-size:0.95rem; cursor:pointer; position:absolute; top:20px; right:20px; transition:all 0.2s;}
.copy-btn:hover {background:#e56e00;}
.copy-status {position:absolute; top:20px; right:100px; color:#228B22; font-weight:600;}
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "source_lang" not in st.session_state: st.session_state.source_lang = "English"
if "target_lang" not in st.session_state: st.session_state.target_lang = "Hindi"
if "text_input" not in st.session_state: st.session_state.text_input = ""
if "translated_text" not in st.session_state: st.session_state.translated_text = ""
if "phonetic_text" not in st.session_state: st.session_state.phonetic_text = ""
if "copy_status" not in st.session_state: st.session_state.copy_status = ""

# ---------- Header ----------
st.markdown("""
<div class="header">
    <div class="header-title">AI Translator Pro</div>
    <div class="header-badge">PRO</div>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Translate text across languages with phonetics & audio playback.</div>', unsafe_allow_html=True)
st.markdown('<div class="container">', unsafe_allow_html=True)

# ---------- Language Selection ----------
lang_map = {
    "English":"en","French":"fr","Spanish":"es","German":"de","Italian":"it","Portuguese":"pt",
    "Russian":"ru","Japanese":"ja","Korean":"ko","Chinese (Mandarin)":"zh-cn","Arabic":"ar",
    "Turkish":"tr","Dutch":"nl","Greek":"el","Polish":"pl","Swedish":"sv",
    "Hindi":"hi","Tamil":"ta","Telugu":"te","Kannada":"kn","Malayalam":"ml",
    "Gujarati":"gu","Marathi":"mr","Punjabi":"pa","Bengali":"bn","Urdu":"ur","Odia":"or"
}
sorted_langs = sorted(lang_map.keys())

col1, col_swap, col3 = st.columns([3.7,0.5,3.7])
with col1:
    st.session_state.source_lang = st.selectbox("From", sorted_langs, index=sorted_langs.index(st.session_state.source_lang))
with col_swap:
    if st.button("⇆", key="swap"):
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
with col3:
    st.session_state.target_lang = st.selectbox("To", sorted_langs, index=sorted_langs.index(st.session_state.target_lang))

# ---------- Text Input ----------
st.session_state.text_input = st.text_area("Text to translate", value=st.session_state.text_input, height=110, placeholder="Type or paste your text here...")

# ---------- Action Buttons ----------
clear_col, translate_col = st.columns([1,5])
with clear_col:
    if st.button("Clear", key="clear", use_container_width=True):
        st.session_state.text_input = ""
        st.session_state.translated_text = ""
        st.session_state.phonetic_text = ""
        st.session_state.copy_status = ""
        st.experimental_rerun()
with translate_col:
    translate_clicked = st.button("Translate", key="translate", use_container_width=True)

# ---------- Translation ----------
openai.api_key = st.secrets["OPENAI_API_KEY"]
if translate_clicked:
    if not st.session_state.text_input.strip():
        st.warning("⚠️ Please enter text to translate.")
    else:
        with st.spinner("Translating…"):
            # Only raw translation
            translate_prompt = f"Translate this text from {st.session_state.source_lang} to {st.session_state.target_lang}:\n{st.session_state.text_input}"
            response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":translate_prompt}])
            st.session_state.translated_text = response.choices[0].message.content.strip()

            # Phonetic output
            phonetic_prompt = f"{st.session_state.translated_text}"
            phonetic_resp = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":phonetic_prompt}])
            st.session_state.phonetic_text = phonetic_resp.choices[0].message.content.strip()

# ---------- Function to display output with inline copy ----------
def output_with_copy(title, text, key_name):
    if text:
        html_code = f"""
        <div class="output-card">
            <div class="output-title">{title}</div>
            <textarea id="{key_name}" readonly style="width:100%; height:90px;">{text}</textarea>
            <span class="copy-status" id="{key_name}_status"></span>
            <button class="copy-btn" onclick="
                navigator.clipboard.writeText(document.getElementById('{key_name}').value);
                document.getElementById('{key_name}_status').innerText='Copied ✅';
            ">Copy</button>
        </div>
        """
        components.html(html_code, height=150)

# ---------- Display Outputs ----------
if st.session_state.translated_text:
    output_with_copy("🌐 Translation", st.session_state.translated_text, "translation_box")
if st.session_state.phonetic_text:
    output_with_copy("🔤 Phonetic", st.session_state.phonetic_text, "phonetic_box")

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
