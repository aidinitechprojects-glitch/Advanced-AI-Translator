import streamlit as st
from gtts import gTTS
import openai
import tempfile
import uuid

# ---------- Page Config ----------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")

# ---------- CSS ----------
st.markdown("""
<style>
.container { background:#fffaf3; border-radius:18px; padding:16px; max-width:720px; margin:12px auto; box-shadow:0 8px 30px rgba(255,135,0,0.25); border:1.5px solid #ffd8a0;}
.header-title {font-size:2rem;font-weight:800;color:#e66c02;}
.header-badge {background-color:#ff7f23;color:white;padding:4px 16px;border-radius:12px;}
.subtitle {margin:2px 0 12px;font-weight:600;font-size:1.15rem;color:#a15303cc;}
textarea {font-size:1.12rem !important;line-height:1.4 !important;padding:10px !important;background-color:#fff6e9 !important;color:#7a4d00 !important;border-radius:12px !important;border:2px solid #ffaf52 !important;min-height:90px !important;resize:vertical !important;}
textarea:focus {outline:none !important;background-color:#fff5db !important;border-color:#ff8a1e !important;box-shadow:0 0 10px 3px #ff9c1e95 !important;}
.output-box {background:#fff9f0;border-radius:16px;border:1.8px solid #ffb350;padding:14px;margin-bottom:8px;font-size:1.13rem;color:#7a4d00;line-height:1.45;position:relative;}
.output-title {font-weight:700;font-size:1.2rem;margin-bottom:6px;color:#ff7f23;}
.copy-feedback {color:#ff7f23;font-weight:700;font-size:0.9rem;margin-left:10px;}
.audio-title {font-size:1.18rem;font-weight:700;color:#ff9123;text-align:center;margin-bottom:10px;}
.copy-btn {position:absolute;right:14px;top:14px;background:#ff7f23;color:white;border:none;padding:4px 10px;border-radius:6px;cursor:pointer;}
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
for key in ["source_lang","target_lang","text_input","translated_text","phonetic_text"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# ---------- Header ----------
st.markdown('<div class="container">', unsafe_allow_html=True)
st.markdown('<div class="header-title">AI Translator Pro</div><div class="header-badge">PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Translate across languages with phonetics & audio playback.</div>', unsafe_allow_html=True)

# ---------- Language Selection ----------
lang_map = {"English":"en","French":"fr","Spanish":"es","German":"de","Italian":"it","Portuguese":"pt",
            "Russian":"ru","Japanese":"ja","Korean":"ko","Chinese (Mandarin)":"zh-cn","Arabic":"ar",
            "Turkish":"tr","Dutch":"nl","Greek":"el","Polish":"pl","Swedish":"sv",
            "Hindi":"hi","Tamil":"ta","Telugu":"te","Kannada":"kn","Malayalam":"ml","Gujarati":"gu",
            "Marathi":"mr","Punjabi":"pa","Bengali":"bn","Urdu":"ur","Odia":"or"}
sorted_langs = sorted(lang_map.keys())
col1,col_swap,col3 = st.columns([3.7,0.5,3.7])
with col1:
    st.session_state.source_lang = st.selectbox("From", sorted_langs, index=sorted_langs.index(st.session_state.source_lang))
with col_swap:
    if st.button("⇆"):
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
with col3:
    st.session_state.target_lang = st.selectbox("To", sorted_langs, index=sorted_langs.index(st.session_state.target_lang))

# ---------- Text Input ----------
st.session_state.text_input = st.text_area("Text to translate", value=st.session_state.text_input, height=100, placeholder="Type or paste text here...")

# ---------- Action Buttons ----------
clear_col, translate_col = st.columns([1,5])
with clear_col:
    if st.button("Clear"):
        for key in ["text_input","translated_text","phonetic_text"]:
            st.session_state[key] = ""
        st.experimental_rerun()
with translate_col:
    translate_clicked = st.button("Translate")

# ---------- Translation Logic ----------
openai.api_key = st.secrets["OPENAI_API_KEY"]
if translate_clicked and st.session_state.text_input.strip():
    with st.spinner("Translating…"):
        # Translation
        translate_prompt = f"Translate this text from {st.session_state.source_lang} to {st.session_state.target_lang}. ONLY raw output:\n{st.session_state.text_input}"
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":translate_prompt}]
        )
        st.session_state.translated_text = response.choices[0].message.content.strip()

        # Phonetic
        phonetic_prompt = f"Provide phonetic (romanized) transcription of this {st.session_state.target_lang} text. ONLY raw output:\n{st.session_state.translated_text}"
        phonetic_resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":phonetic_prompt}]
        )
        st.session_state.phonetic_text = phonetic_resp.choices[0].message.content.strip()

# ---------- Output Box with JS Copy ----------
def output_box(title, text):
    if text:
        unique_id = str(uuid.uuid4()).replace("-", "")
        st.markdown(f"""
        <div class="output-box">
            <div class="output-title">{title}</div>
            {text}
            <button class="copy-btn" onclick="navigator.clipboard.writeText(document.getElementById('{unique_id}').innerText).then(()=>{{document.getElementById('{unique_id}-feedback').innerText='Copied!';}})">Copy</button>
            <div id="{unique_id}" style="display:none;">{text}</div>
            <div id="{unique_id}-feedback" class="copy-feedback"></div>
        </div>
        """, unsafe_allow_html=True)

output_box("🌐 Translation", st.session_state.translated_text)
output_box("🔤 Phonetic", st.session_state.phonetic_text)

# ---------- Audio ----------
if st.session_state.translated_text:
    st.markdown('<div class="audio-title">🔊 Audio Playback</div>', unsafe_allow_html=True)
    try:
        tts_lang = lang_map.get(st.session_state.target_lang,"en")
        tts = gTTS(text=st.session_state.translated_text,lang=tts_lang)
        tts_file = tempfile.NamedTemporaryFile(delete=False,suffix=".mp3")
        tts.save(tts_file.name)
        st.audio(tts_file.name,format="audio/mp3")
    except Exception as e:
        st.error(f"❌ Speech generation failed: {e}")

st.markdown('</div>', unsafe_allow_html=True)
