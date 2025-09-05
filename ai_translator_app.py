import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------- Page Config ----------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")

st.markdown("""
<style>
/* Smooth dark gradient background with subtle animation */
@keyframes bgpulse {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #1c2031, #3e497a, #26418f, #1c2031);
    background-size: 400% 400%;
    animation: bgpulse 18s ease infinite;
    color: #e3e6f3;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    -webkit-font-smoothing: antialiased;
    user-select: none;
}

/* Glass card for the content */
.glass-card {
    background: rgba(23, 35, 61, 0.85);
    border-radius: 24px;
    padding: 48px 56px 40px;
    max-width: 700px;
    margin: 36px auto 48px;
    box-shadow: 0 15px 50px rgba(0, 64, 255, 0.7);
    backdrop-filter: saturate(180%) blur(20px);
    border: 1.5px solid rgba(255, 255, 255, 0.12);
    transition: box-shadow 0.3s ease;
}
.glass-card:hover {
    box-shadow: 0 25px 70px rgba(0, 64, 255, 1);
}

/* Header */
.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}
.header-title {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(90deg, #0088ff 0%, #00e0ff 80%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.06em;
}
.header-badge {
    background: linear-gradient(90deg, #00e0ff, #0088ff);
    color: white;
    font-weight: 700;
    padding: 9px 28px;
    font-size: 1.15rem;
    border-radius: 20px;
    box-shadow: 0 0 30px #00a4ffaa;
    user-select: none;
}

/* Subtitle */
.subtitle {
    margin-top: 4px;
    font-weight: 600;
    font-size: 1.25rem;
    color: #a2b3ffcc;
    margin-bottom: 44px;
    user-select: none;
}

/* Selectbox labels and options */
.stSelectbox > div:first-child {
    font-weight: 600;
    font-size: 1.18rem;
    color: #66aaffcc;
}
.stSelectbox > div[role="listbox"] > div {
    font-size: 1.12rem;
    color: #dde9ff;
}

/* Textarea styles */
textarea {
    font-size: 1.2rem !important;
    line-height: 1.5 !important;
    padding: 20px !important;
    background-color: rgba(38, 54, 89, 0.8) !important;
    color: #d4e1ff !important;
    border-radius: 20px !important;
    border: 2px solid rgba(0, 136, 255, 0.5) !important;
    box-shadow: inset 0 0 12px 0 rgba(0, 136, 255, 0.7);
    transition: border-color 0.3s ease, background-color 0.3s ease;
    min-height: 110px !important;
    resize: vertical !important;
}
textarea:focus {
    outline: none !important;
    background-color: rgba(12, 34, 68, 0.95) !important;
    border-color: #00abff !important;
    box-shadow: 0 0 18px 4px #00b0ffaa !important;
}

/* Swap button styling */
.swap-btn {
    width: 50px;
    height: 50px;
    background: linear-gradient(135deg, #00a9ff, #004abf);
    font-size: 28px;
    color: white;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    box-shadow: 0 0 20px #00abffa6;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: auto;
    user-select: none;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.swap-btn:hover {
    transform: scale(1.2);
    box-shadow: 0 0 30px #00d3ffdd;
}

/* Action buttons */
.action-btn {
    background: linear-gradient(90deg, #007aff, #00d3ff);
    border-radius: 18px;
    padding: 14px 0;
    color: white !important;
    font-weight: 700;
    font-size: 1.3rem;
    border: none;
    width: 100%;
    margin-top: 20px;
    box-shadow: 0 10px 35px #00b5ff6b;
    cursor: pointer;
    transition: background 0.3s ease, box-shadow 0.3s ease;
    user-select:none;
}
.action-btn:hover {
    background: linear-gradient(90deg, #005ecc, #00c7ff);
    box-shadow: 0 15px 50px #00cfffb3;
}

/* Clear button */
.clear-btn {
    background-color: #2b3a66cc !important;
    color: #acc7ffdd !important;
    font-size: 1.05rem;
    font-weight: 600;
    border-radius: 16px;
    padding: 10px 22px;
    border: none;
    cursor: pointer;
    user-select:none;
    transition: background-color 0.3s ease;
    margin-top: 16px;
}
.clear-btn:hover {
    background-color: #4063a5dd !important;
}

/* Output cards */
.output-card {
    background: rgba(10, 23, 45, 0.9);
    border-radius: 24px;
    box-shadow: 0 12px 42px #00aaff88;
    padding: 30px 28px 24px;
    margin-bottom: 30px;
    font-size: 1.17rem;
    color: #cbe1ff;
    user-select: text;
    line-height: 1.5;
}
.output-title {
    font-weight: 700;
    font-size: 1.3rem;
    margin-bottom: 14px;
    background: linear-gradient(90deg, #008aff, #00e0ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    user-select:none;
}

/* Audio playback title */
.audio-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #00d0ff;
    text-align: center;
    margin-bottom: 20px;
    user-select:none;
}

/* Responsive */
@media (max-width: 700px) {
    .glass-card {
        margin: 20px;
        padding: 26px 24px 20px;
    }
    .header-title {
        font-size: 2.5rem;
    }
    .action-btn {
        font-size: 1.1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------- Session State ----------------
if "source_lang" not in st.session_state: st.session_state.source_lang = "English"
if "target_lang" not in st.session_state: st.session_state.target_lang = "Hindi"
if "text_input" not in st.session_state: st.session_state.text_input = ""
if "translated_text" not in st.session_state: st.session_state.translated_text = ""
if "phonetic_text" not in st.session_state: st.session_state.phonetic_text = ""

# ---------------- Header ----------------
st.markdown("""
<div class="header">
  <div class="header-title">AI Translator Pro</div>
  <div class="header-badge">PRO</div>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Translate across languages with phonetics & audio — now with an ultra-modern dark tech look.</div>', unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

# ---------------- Language Selectors + Swap ----------------
lang_map = {
    "English":"en","French":"fr","Spanish":"es","German":"de","Italian":"it","Portuguese":"pt",
    "Russian":"ru","Japanese":"ja","Korean":"ko","Chinese (Mandarin)":"zh-cn","Arabic":"ar",
    "Turkish":"tr","Dutch":"nl","Greek":"el","Polish":"pl","Swedish":"sv",
    "Hindi":"hi","Tamil":"ta","Telugu":"te","Kannada":"kn","Malayalam":"ml","Gujarati":"gu",
    "Marathi":"mr","Punjabi":"pa","Bengali":"bn","Urdu":"ur","Odia":"or"
}
sorted_langs = sorted(lang_map.keys())

col1, col2, col3 = st.columns([3.7, 0.5, 3.7])

with col1:
    st.session_state.source_lang = st.selectbox("From", sorted_langs, index=sorted_langs.index(st.session_state.source_lang))

with col2:
    st.markdown('<div style="margin-top:20px;text-align:center;">', unsafe_allow_html=True)
    if st.button("⇆", key="swap", help="Swap languages", args=None):
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.session_state.target_lang = st.selectbox("To", sorted_langs, index=sorted_langs.index(st.session_state.target_lang))

# ---------------- Text Input ----------------
st.session_state.text_input = st.text_area("Text to translate", value=st.session_state.text_input, height=120, placeholder="Type or paste your text here...")

# ---------------- Action Buttons ----------------
clear_col, translate_col = st.columns([1,5])

with clear_col:
    if st.button("Clear", key="clear", help="Clear input", use_container_width=True):
        st.session_state.text_input = ""
        st.session_state.translated_text = ""
        st.session_state.phonetic_text = ""
        st.experimental_rerun()

with translate_col:
    translate_clicked = st.button("Translate", key="translate", help="Translate text", use_container_width=True)

# ---------------- Translation Logic (Original) ----------------
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

# ---------------- Outputs ----------------
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
