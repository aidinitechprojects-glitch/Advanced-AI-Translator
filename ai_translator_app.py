import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------- Page Config ----------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")

st.markdown("""
<style>
/* Background gradient */
body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1a2238 0%, #4e5d78 100%);
    color: #f0f2f5;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* Glass container */
.pro-glass {
    background: rgba(30, 38, 60, 0.85);
    border-radius: 25px;
    box-shadow: 0 20px 40px rgba(10, 14, 38, 0.7);
    padding: 40px 48px 36px;
    margin: 32px auto 48px;
    max-width: 720px;
    backdrop-filter: blur(10px);
    border: 2px solid rgba(255,255,255,0.06);
    transition: box-shadow 0.3s ease;
}
.pro-glass:hover {
    box-shadow: 0 30px 60px rgba(10, 14, 38, 0.9);
}

/* Header */
.pro-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.pro-title {
    font-size: 3.2rem;
    font-weight: 900;
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.08em;
}
.pro-badge {
    background: #0072ff;
    font-weight: 700;
    color: #fff;
    padding: 7px 22px;
    border-radius: 16px;
    font-size: 1.1rem;
    box-shadow: 0 4px 16px rgba(0, 114, 255, 0.46);
    user-select: none;
}
.pro-subtitle {
    color: #b8c1e2;
    font-weight: 500;
    font-size: 1.3rem;
    margin-bottom: 40px;
}

/* Selectboxes */
.stSelectbox > div:first-child {
    font-size: 1.18rem;
    font-weight: 600;
    color: #add8ff;
}
.stSelectbox > div[role="listbox"] > div {
    font-size: 1.1rem;
    color: #d1d9ff;
}

/* Textarea */
textarea {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #e0e9ff !important;
    font-size: 1.15rem !important;
    border-radius: 18px !important;
    border: 1.8px solid rgba(255, 255, 255, 0.3) !important;
    padding: 18px !important;
    min-height: 98px !important;
    box-shadow: inset 0 0 15px rgba(0, 114, 255, 0.3);
    transition: border-color 0.3s ease, background-color 0.3s ease;
}

textarea:focus {
    border: 2.5px solid #00b4ff !important;
    background-color: rgba(6, 71, 197, 0.25) !important;
    outline: none !important;
}

/* Swap Button */
.pro-swap-btn {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #0072ff, #00c6ff);
    border-radius: 50%;
    border: none;
    color: white;
    font-size: 26px;
    font-weight: 900;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    cursor: pointer;
    transition: transform 0.2s ease;
    box-shadow: 0 6px 12px rgba(0, 198, 255, 0.6);
}

.pro-swap-btn:hover {
    transform: scale(1.14);
    box-shadow: 0 9px 20px rgba(0, 198, 255, 0.9);
}

/* Buttons */
.pro-btn {
    background: linear-gradient(90deg, #0072ff, #00c6ff);
    color: #ffffff !important;
    font-weight: 700;
    font-size: 1.28rem;
    border-radius: 16px;
    padding: 14px 0;
    width: 100%;
    border: none;
    box-shadow: 0 8px 24px rgba(0, 198, 255, 0.45);
    transition: background 0.3s ease, box-shadow 0.3s ease;
    cursor: pointer;
    margin-top: 18px;
}

.pro-btn:hover {
    background: linear-gradient(90deg, #005bb5, #008de4);
    box-shadow: 0 12px 32px rgba(0, 180, 255, 0.8);
}

/* Clear Button */
.clear-btn {
    background: #3a4284cc !important;
    color: #e0e9ff !important;
    font-weight: 600;
    border-radius: 14px;
    padding: 8px 18px;
    font-size: 1.05rem;
    border: none;
    cursor: pointer;
    transition: background-color 0.23s ease;
    margin-top: 14px;
}

.clear-btn:hover {
    background: #5e65c9cc !important;
}

/* Output Cards */
.pro-out-card {
    background: rgba(16, 28, 64, 0.75);
    border-radius: 20px;
    padding: 26px 22px 20px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px rgba(0, 114, 255, 0.33);
    font-size: 1.15rem;
    color: #c9d1ff;
    user-select: text;
    transition: background-color 0.35s ease;
}

.pro-out-card:hover {
    background-color: rgba(16, 28, 64, 0.9);
}

.pro-out-title {
    color: #00b4ff;
    font-weight: 700;
    font-size: 1.21rem;
    margin-bottom: 10px;
    user-select: none;
}

/* Audio Title */
.audio-title {
    color: #00c6ff;
    font-size: 1.25rem;
    font-weight: 700;
    text-align: center;
    margin-top: 6px;
    margin-bottom: 16px;
}

/* Responsive columns */
@media (max-width: 640px) {
    .pro-glass {
        padding: 28px 30px 24px;
        margin: 16px 12px 36px;
    }
    .pro-title {
        font-size: 2.5rem;
    }
    .pro-subtitle {
        font-size: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# --------- Session State Initialization ---------
if "source_lang" not in st.session_state: st.session_state.source_lang = "English"
if "target_lang" not in st.session_state: st.session_state.target_lang = "Hindi"
if "text_input" not in st.session_state: st.session_state.text_input = ""
if "translated_text" not in st.session_state: st.session_state.translated_text = ""
if "phonetic_text" not in st.session_state: st.session_state.phonetic_text = ""

# --------- Header Section ---------
st.markdown("""
<div class="pro-header">
    <div class="pro-title">AI Translator Pro</div>
    <div class="pro-badge">PRO</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-subtitle">Translate text across languages with phonetics & audio playback, now with a sleek modern interface.</div>', unsafe_allow_html=True)

st.markdown('<div class="pro-glass">', unsafe_allow_html=True)

# --------- Language Selection with Swap Button ---------
lang_map = {
    "English":"en","French":"fr","Spanish":"es","German":"de","Italian":"it","Portuguese":"pt",
    "Russian":"ru","Japanese":"ja","Korean":"ko","Chinese (Mandarin)":"zh-cn","Arabic":"ar",
    "Turkish":"tr","Dutch":"nl","Greek":"el","Polish":"pl","Swedish":"sv",
    "Hindi":"hi","Tamil":"ta","Telugu":"te","Kannada":"kn","Malayalam":"ml","Gujarati":"gu",
    "Marathi":"mr","Punjabi":"pa","Bengali":"bn","Urdu":"ur","Odia":"or"
}
sorted_langs = sorted(lang_map.keys())

col1, col_swap, col3 = st.columns([3.6, 0.7, 3.6])

with col1:
    st.session_state.source_lang = st.selectbox("From", sorted_langs, index=sorted_langs.index(st.session_state.source_lang))

with col_swap:
    st.markdown('<div style="margin-top:18px;">', unsafe_allow_html=True)
    if st.button("⇆", key="swap", help="Swap languages"):
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.session_state.target_lang = st.selectbox("To", sorted_langs, index=sorted_langs.index(st.session_state.target_lang))

# --------- Text Input with Clear & Translate Buttons ---------
st.session_state.text_input = st.text_area(
    "Text to translate",
    value=st.session_state.text_input,
    height=100,
    placeholder="Type or paste your text here...")

btn_clear, btn_translate = st.columns([1,5])

with btn_clear:
    if st.button("Clear", key="clear", help="Clear input"):
        st.session_state.text_input = ""
        st.session_state.translated_text = ""
        st.session_state.phonetic_text = ""
        st.experimental_rerun()

with btn_translate:
    translate_clicked = st.button("Translate", key="translate", help="Translate text")

# --------- Translation Logic ---------
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

# --------- Outputs ---------
if st.session_state.translated_text:
    st.markdown(
        f'<div class="pro-out-card">'
        f'<div class="pro-out-title">🌐 Translation</div>'
        f'<div>{st.session_state.translated_text}</div>'
        f'</div>', unsafe_allow_html=True)

if st.session_state.phonetic_text:
    st.markdown(
        f'<div class="pro-out-card">'
        f'<div class="pro-out-title">🔤 Phonetic</div>'
        f'<div>{st.session_state.phonetic_text}</div>'
        f'</div>', unsafe_allow_html=True)

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
