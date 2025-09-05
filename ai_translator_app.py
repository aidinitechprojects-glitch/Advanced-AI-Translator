import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------- Page Config ----------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")

st.markdown("""
<style>
/* Background */
@keyframes bgpulse {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #1c2031, #3e497a, #26418f, #1c2031);
    background-size: 400% 400%;
    animation: bgpulse 18s ease infinite;
    color: #e7f0ff;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    -webkit-font-smoothing: antialiased;
    user-select: none;
}

/* Glass card */
.glass-card {
    background: rgba(29, 42, 73, 0.94);
    border-radius: 25px;
    padding: 48px 56px 40px;
    max-width: 700px;
    margin: 36px auto 48px;
    box-shadow: 0 15px 50px rgba(0, 68, 255, 0.85);
    backdrop-filter: saturate(180%) blur(24px);
    border: 1.5px solid rgba(255, 255, 255, 0.15);
    transition: box-shadow 0.3s ease;
}
.glass-card:hover {
    box-shadow: 0 25px 70px rgba(0, 68, 255, 1);
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
    background: linear-gradient(90deg, #0af, #00d6ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.07em;
    user-select: none;
}
.header-badge {
    background: linear-gradient(90deg, #00d6ff, #0af);
    color: white;
    font-weight: 800;
    padding: 9px 28px;
    font-size: 1.15rem;
    border-radius: 20px;
    box-shadow: 0 0 36px #00c5ffcc;
    user-select: none;
}

/* Subtitle */
.subtitle {
    margin-top: 4px;
    font-weight: 600;
    font-size: 1.32rem;
    color: #7fd7ffcc;
    margin-bottom: 44px;
    user-select: none;
}

/* Selectbox labels & options */
.stSelectbox > div:first-child {
    font-weight: 700;
    font-size: 1.19rem;
    color: #7bd2ffcc;
}
.stSelectbox > div[role="listbox"] > div {
    font-size: 1.14rem;
    color: #c5e8ff;
}

/* Textarea */
textarea {
    font-size: 1.22rem !important;
    line-height: 1.6 !important;
    padding: 20px !important;
    background-color: rgba(48, 67, 114, 0.88) !important;
    color: #d1eaff !important;
    border-radius: 20px !important;
    border: 2px solid rgba(0, 137, 255, 0.63) !important;
    box-shadow: inset 0 0 14px 0 rgba(0, 137, 255, 0.9);
    transition: border-color 0.3s ease, background-color 0.3s ease;
    min-height: 110px !important;
    resize: vertical !important;
}
textarea:focus {
    outline: none !important;
    background-color: rgba(10, 40, 95, 0.98) !important;
    border-color: #00b2ff !important;
    box-shadow: 0 0 24px 5px #00b9ffcc !important;
}

/* Swap button */
.swap-btn {
    width: 50px;
    height: 50px;
    background: linear-gradient(135deg, #00b2ff, #0052d4);
    font-size: 28px;
    color: white;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    box-shadow: 0 0 22px #00b0ffbb;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: auto;
    user-select: none;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.swap-btn:hover {
    transform: scale(1.22);
    box-shadow: 0 0 36px #00d3ffdd;
}

/* Action buttons */
.action-btn {
    background: linear-gradient(90deg, #006dff, #00d3ff);
    border-radius: 18px;
    padding: 16px 0;
    color: white !important;
    font-weight: 800;
    font-size: 1.32rem;
    border: none;
    width: 100%;
    margin-top: 22px;
    box-shadow: 0 12px 36px #00b5ffaa;
    cursor: pointer;
    transition: background 0.3s ease, box-shadow 0.3s ease;
    user-select:none;
}
.action-btn:hover {
    background: linear-gradient(90deg, #004ab5, #00c7ff);
    box-shadow: 0 18px 48px #00dfffbb;
}

/* Clear button */
.clear-btn {
    background-color: #3452a8cc !important;
    color: #b6d1ffdd !important;
    font-size: 1.1rem;
    font-weight: 700;
    border-radius: 16px;
    padding: 12px 26px;
    border: none;
    cursor: pointer;
    user-select:none;
    transition: background-color 0.3s ease;
    margin-top: 18px;
}
.clear-btn:hover {
    background-color: #4f6bcdcc !important;
}

/* Output cards */
.output-card {
    background: rgba(11, 24, 50, 0.95);
    border-radius: 26px;
    box-shadow: 0 14px 56px #009bffcc;
    padding: 34px 30px 28px;
    margin-bottom: 34px;
    font-size: 1.22rem;
    color: #cde7ff;
    user-select: text;
    line-height: 1.6;
}
.output-title {
    font-weight: 800;
    font-size: 1.38rem;
    margin-bottom: 18px;
    background: linear-gradient(90deg, #00a8ff, #00d9ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    user-select:none;
}

/* Audio Playback title */
.audio-title {
    font-size: 1.4rem;
    font-weight: 800;
    color: #00e0ff;
    text-align: center;
    margin-bottom: 24px;
    user-select:none;
}

/* Responsive */
@media (max-width: 720px) {
    .glass-card {
        margin: 22px 18px 42px;
        padding: 32px 28px 24px;
    }
    .header-title {
        font-size: 2.6rem;
    }
    .action-btn {
        font-size: 1.18rem;
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
st.markdown('<div class="subtitle">Translate across languages with phonetics & audio — vivid colors, premium look.</div>', unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

# ---------------- Language Selection ----------------
lang_map = {
    "English":"en","French":"fr","Spanish":"es","German":"de","Italian":"it","Portuguese":"pt",
    "Russian":"ru","Japanese":"ja","Korean":"ko","Chinese (Mandarin)":"zh-cn","Arabic":"ar",
    "Turkish":"tr","Dutch":"nl","Greek":"el","Polish":"pl","Swedish":"sv",
    "Hindi":"hi","Tamil":"ta","Telugu":"te","Kannada":"kn","Malayalam":"ml","Gujarati":"gu",
    "Marathi":"mr","Punjabi":"pa","Bengali":"bn","Urdu":"ur","Odia":"or"
}
sorted_langs = sorted(lang_map.keys())

col1, col_swap, col3 = st.columns([3.7, 0.5, 3.7])

with col1:
    st.session_state.source_lang = st.selectbox("From", sorted_langs, index=sorted_langs.index(st.session_state.source_lang))

with col_swap:
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
