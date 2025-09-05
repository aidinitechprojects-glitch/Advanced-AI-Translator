import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------------- Page Config ----------------
st.set_page_config(page_title="🤖 AI Translator", page_icon="🌐", layout="wide")

# ---------------- Initialize Session State ----------------
if "source_lang" not in st.session_state:
    st.session_state.source_lang = "English"
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Hindi"
if "text_input" not in st.session_state:
    st.session_state.text_input = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "phonetic_text" not in st.session_state:
    st.session_state.phonetic_text = ""

# ---------------- Enhanced Custom CSS ----------------
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(120deg,#f9fafc 70%,#ffe7d1 100%);
    }
    .glass-bg {
        background: rgba(255,255,255,0.92);
        border-radius: 22px;
        box-shadow: 0 12px 36px 4px rgba(255,107,0,0.07);
        padding: 36px 32px 32px 32px;
        margin-bottom: 20px;
    }
    .big-header {
        text-align:center;
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(90deg,#FF6B00,#FF3C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 0.07em;
        margin-bottom: -12px;
    }
    .subtitle {
        text-align: center; 
        font-size: 1.2rem; 
        color: #555555; 
        margin-bottom: 35px;
    }
    textarea {
        background: rgba(253,242,236,0.94) !important;
        border-radius:22px !important;
        font-size: 17px;
        color: #2d2d2f !important;
        border:1.5px solid #ffdabf !important;
        transition:all 0.3s;
    }
    textarea:focus {
        border:2.5px solid #FF6B00 !important;
        background: #fff9f5 !important;
    }
    div[data-testid="stForm"] {
        background: rgba(244,157,81,0.03);
        border-radius: 20px;
        padding: 12px 0;
        margin-bottom: 28px;
        box-shadow: 0 4px 24px rgba(31,38,135,0.06);
    }
    .row-ctr {
        display: flex;width:100%;justify-content:center;align-items: center;margin-bottom:20px;
    }
    .custom-selectbox > div {
        font-size:15.5px !important; 
        color:#312b2d !important;
    }
    .swap-btn {
        border-radius: 50%;
        background: linear-gradient(90deg,#55c7f0,#468dbb);
        color: #fff;
        border: none;
        width: 44px;
        height: 44px;
        font-size: 24px;
        box-shadow: 0 3px 9px rgba(71,181,255,0.12);
        cursor: pointer;
        display:flex;align-items:center;justify-content:center;
        margin:10px 0 0 0;
        transition: filter .2s, box-shadow .2s;
    }
    .swap-btn:hover {filter: brightness(1.22);box-shadow: 0 6px 16px #3cb2ff18;}
    .translate-btn {
        background: linear-gradient(90deg,#FF6B00,#FF3C00);
        color: #fff !important;
        font-size: 1.2rem;
        font-weight: bold;
        padding: 0.7em 2.5em;
        border: none;
        border-radius: 16px;
        width: 100%;
        margin-top: 13px;
        transition: transform .18s, box-shadow .18s, filter .16s;
        box-shadow: 0 7px 22px #FFBA7E30;
        letter-spacing: 0.05em;
    }
    .translate-btn:hover {transform: scale(1.04); filter:brightness(1.07);}
    .clear-btn {
        background: #808080dd !important;
        color: #fff !important;
        font-size: 15px;
        border-radius: 10px;
        padding: 0.4em 1.5em;
        border: none;
        float: right;
        margin-top: 7px;
        margin-bottom: 12px;
        transition: filter .17s;
    }
    .clear-btn:hover {filter: brightness(1.18);}
    .output-card {
        background: rgba(255,255,255,0.93);
        border-radius: 20px;
        padding: 22px 26px 15px 26px;
        margin-top: 10px;
        margin-bottom: 20px;
        box-shadow: 0 6px 20px #ff6b001f;
        transition: background .2s;
    }
    .output-card:hover {background: #fff9f1;}
    .output-heading {
        color: #FF6B00;
        font-weight: 700;
        font-size: 1.07rem;
        margin-bottom: 0;
        font-family: 'Inter',sans-serif;
    }
    .output-text {font-size: 1.04rem; color: #1d1728; font-family: 'Inter',sans-serif;}
    .audio-title {
        font-weight:700; font-size:1.11rem; margin-bottom:9px; color:#FF6B00; text-align:center;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- Header ----------------
st.markdown('<div class="big-header">🤖 AI Translator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Translate text across languages—with phonetics & audio. Delightfully easy.</div>', unsafe_allow_html=True)

# ---------------- OpenAI API Key ----------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ---------------- Languages ----------------
lang_map = {
    "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Kannada": "kn",
    "Malayalam": "ml", "Gujarati": "gu", "Marathi": "mr", "Punjabi": "pa",
    "Bengali": "bn", "Urdu": "ur", "Odia": "or",
    "English": "en", "French": "fr", "Spanish": "es", "German": "de",
    "Italian": "it", "Portuguese": "pt", "Russian": "ru", "Japanese": "ja",
    "Korean": "ko", "Chinese (Mandarin)": "zh-cn", "Arabic": "ar",
    "Turkish": "tr", "Dutch": "nl", "Greek": "el", "Polish": "pl",
    "Swedish": "sv",
}
sorted_langs = sorted(lang_map.keys())

# ---------------- Layout Wrapper ----------------
with st.container():
    st.markdown('<div class="glass-bg">', unsafe_allow_html=True)
    
    # Row 1: Text Input with Clear Button
    col_left, col_right = st.columns([7,1])
    with col_left:
        st.session_state.text_input = st.text_area(
            "Enter text to translate",
            value=st.session_state.text_input,
            height=140,
            key="txt_input",
            placeholder="Type your message...",
        )
    with col_right:
        st.write("")  # space
        if st.button("Clear", key="clear", use_container_width=True):
            st.session_state.text_input = ""
            st.session_state.translated_text = ""
            st.session_state.phonetic_text = ""
            st.experimental_rerun()
    
    st.write("")  # space

    # Row 2: Language selectors and swap
    col_a, col_swap, col_b = st.columns([3.6,1,3.6])
    with col_a:
        st.session_state.source_lang = st.selectbox(
            "From:",
            sorted_langs,
            index=sorted_langs.index(st.session_state.source_lang),
            key="src_lang",
        )
    with col_swap:
        st.markdown('<div class="row-ctr">', unsafe_allow_html=True)
        if st.button("⇆", key="swap", help="Swap languages", type="secondary"):
            st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.session_state.target_lang = st.selectbox(
            "To:",
            sorted_langs,
            index=sorted_langs.index(st.session_state.target_lang),
            key="tgt_lang",
        )
    st.write("")  # space

    # Row 3: Translate button full width
    translate_clicked = st.button("Translate", key="translate", help="Translate text", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Translation Logic ----------------
if translate_clicked:
    if st.session_state.text_input.strip() == "":
        st.warning("⚠️ Please enter some text.")
    else:
        with st.spinner("Translating..."):
            # Translation
            translate_prompt = (
                f"Translate this text from {st.session_state.source_lang} to {st.session_state.target_lang}:\n"
                f"{st.session_state.text_input}"
            )
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": translate_prompt}]
            )
            st.session_state.translated_text = response.choices[0].message.content.strip()
            
            # Phonetic
            phonetic_prompt = (
                f"Provide phonetic (romanized) transcription of this {st.session_state.target_lang} text:\n"
                f"{st.session_state.translated_text}"
            )
            phonetic_resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": phonetic_prompt}]
            )
            st.session_state.phonetic_text = phonetic_resp.choices[0].message.content.strip()

# ---------------- Output ----------------
if st.session_state.translated_text:
    st.markdown(f'''
    <div class="output-card">
        <div class="output-heading">🌐 Translated ({st.session_state.target_lang})</div>
        <div class="output-text">{st.session_state.translated_text}</div>
    </div>
    ''', unsafe_allow_html=True)
if st.session_state.phonetic_text:
    st.markdown(f'''
    <div class="output-card">
        <div class="output-heading">🔤 Phonetic</div>
        <div class="output-text">{st.session_state.phonetic_text}</div>
    </div>
    ''', unsafe_allow_html=True)

# ---------------- Audio Playback ----------------
if st.session_state.translated_text:
    st.markdown('<div class="audio-title">🔊 Play Translated Audio</div>', unsafe_allow_html=True)
    try:
        tts_lang = lang_map.get(st.session_state.target_lang, "en")
        tts = gTTS(text=st.session_state.translated_text, lang=tts_lang)
        tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tts_file.name)
        st.audio(tts_file.name, format="audio/mp3")
    except Exception as e:
        st.error(f"❌ Speech generation failed: {e}")
