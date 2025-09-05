import streamlit as st
from gtts import gTTS
import openai
import tempfile

# --------------- Pro UI Styling -----------------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")
st.markdown("""
<style>
body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg,#23252680 0%,#f5eeee 100%);
}
.pro-glass {
    background: rgba(225, 220, 249, 0.84);
    border-radius: 28px;
    box-shadow: 0 12px 44px 0 #8371FFAA, 0 0.5px 1.5px #00000011;
    padding: 40px 44px 34px 44px; margin: 25px 0 0 0;
}
.pro-header {
    display:flex;align-items:center;justify-content:space-between;margin-bottom:0;
}
.pro-title {
    font-size:2.7rem; font-weight:900; letter-spacing:0.05em;
    background: linear-gradient(90deg,#FF6B00 25%,#7E3AF2 70%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.pro-badge {
    font-size:0.98rem;background:linear-gradient(90deg,#7E3AF2,#FF6B00 75%);
    color:#fff;border-radius:8px;padding:4px 16px 4px 16px;margin-left:16px; font-weight:500;box-shadow:0 1px 6px #7E3AF233;
}
.pro-subtitle {
    font-size:1.17rem; color:#292744; font-weight:500;
    text-align:left; margin-bottom:32px; margin-top:3px;
}
.lock-icon {
    display:inline-block; color:#FF6B00; vertical-align:middle; font-size:1.2em; margin-left:5px;
}
textarea {
    background: rgba(255,255,255,0.92)!important;
    border-radius:25px !important;
    font-size: 1.17rem; color: #312833 !important;
    border: 2px solid #f0e7ff !important;
    box-shadow: 0 4px 26px #7E3AF222;
}
textarea:focus {border:2.5px solid #7E3AF2 !important;}
.pro-row {display:flex; gap:14px;}
.pro-select label {font-weight:550; color:#483d6c;}
.pro-select div[data-baseweb="select"] {font-size:1.07rem;}
.pro-swap-btn {
    width:45px;height:45px;background:linear-gradient(90deg,#4DFEFD,#7E3AF2);
    color:#fff;border-radius:50%;font-size:1.35rem;border:none;
    display:flex;align-items:center;justify-content:center;
    box-shadow:0 4px 16px #7E3AF280;transition: filter .2s;
}
.pro-swap-btn:hover {filter:brightness(1.13);}
.pro-btn {
    width:100%; padding: 0.7em 0; margin-top:15px;
    background:linear-gradient(90deg,#7E3AF2,#FF6B00 70%);
    color:#fff; border:none; border-radius:16px;
    font-size:1.27rem;font-weight:bold;box-shadow:0 5px 16px #7E3AF230;
    transition:filter .19s,box-shadow .16s;
}
.pro-btn:hover {filter:brightness(1.13);}
.pro-clear-btn {background:#857fa4cc!important;color:#fff!important;border-radius:10px;font-size:15px;margin-top:0;}
.pro-out-card {
    background:rgba(246,244,255,0.97);border-radius:20px;padding:22px 19px 12px 21px;box-shadow:0 4px 20px #ff6b0022;margin-bottom:17px;
}
.pro-out-card.vip {border:2px solid #7E3AF2;}
.pro-out-title {
    font-weight:700;font-size:1.07rem;letter-spacing:0.02em; color:#7E3AF2;
}
.pro-out-vip-label {
    display:inline-block;background:#7E3AF2;color:#fff;
    border-radius:8px;padding:2px 8px;margin-left:9px;font-size:0.95rem;
    vertical-align:middle;font-weight:500;letter-spacing:0.01em;
}
.pro-out {font-size:1.09rem;color:#1d1728;}
.audio-title {font-weight:700;font-size:1.13rem;color:#FF6B00;text-align:center;margin-bottom:5px;}
.upgrade-cta {
    margin-top:16px; text-align:center;
    background:linear-gradient(90deg,#FF6B00,#7E3AF2 80%);
    color:#fff;font-size:1.2rem; font-weight:700;border-radius:16px;padding:9px 0 8px 0;box-shadow: 0 4px 18px #ff6b0025;}
</style>
""", unsafe_allow_html=True)

# --------------- Session State ---------------
if "source_lang" not in st.session_state: st.session_state.source_lang = "English"
if "target_lang" not in st.session_state: st.session_state.target_lang = "Hindi"
if "text_input" not in st.session_state: st.session_state.text_input = ""
if "translated_text" not in st.session_state: st.session_state.translated_text = ""
if "phonetic_text" not in st.session_state: st.session_state.phonetic_text = ""

# --------------- App Header & PRO Badge ---------------
st.markdown("""
<div class='pro-header'>
  <span class='pro-title'>AI Translator</span>
  <span class='pro-badge'>PRO</span>
</div>
""", unsafe_allow_html=True)
st.markdown("<div class='pro-subtitle'>Premium AI translations—text, phonetic, and audio. Secure. Lightning fast. <span style='color:#7E3AF2'>Unlock the world.</span></div>", unsafe_allow_html=True)

st.markdown('<div class="pro-glass">', unsafe_allow_html=True)

# --------------- Language Selection and Swap ---------------
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

col1, col2, col3 = st.columns([3.3,1,3.3])
with col1:
    st.session_state.source_lang = st.selectbox("From", sorted_langs, index=sorted_langs.index(st.session_state.source_lang), key="src_lang", help="Input Language")
with col2:
    st.markdown('<div style="height:38px;"></div>', unsafe_allow_html=True)
    if st.button("⇆", key="swap", help="Swap languages", use_container_width=True):
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
with col3:
    st.session_state.target_lang = st.selectbox("To", sorted_langs, index=sorted_langs.index(st.session_state.target_lang), key="tgt_lang", help="Output Language")

# --------------- Input Row with Clear ---------------
st.session_state.text_input = st.text_area("Type or paste your text...", value=st.session_state.text_input, height=108, key="txt_input", placeholder="Enter text for translation...")

clear_col, submit_col = st.columns([1,5])
with clear_col:
    if st.button("Clear", key="clear", use_container_width=True):
        st.session_state.text_input, st.session_state.translated_text, st.session_state.phonetic_text = "", "", ""
        st.experimental_rerun()

with submit_col:
    translate_clicked = st.button("Translate", key="translate", help="Translate now", use_container_width=True)

# --------------- Translation ---------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

if translate_clicked:
    if st.session_state.text_input.strip() == "":
        st.warning("⚠️ Please enter text to translate.")
    else:
        with st.spinner("Translating with AI..."):
            translate_prompt = f"Translate this text from {st.session_state.source_lang} to {st.session_state.target_lang}:\n{st.session_state.text_input}"
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": translate_prompt}]
            )
            st.session_state.translated_text = response.choices.message.content.strip()

            phonetic_prompt = f"Provide phonetic (romanized) transcription of this {st.session_state.target_lang} text:\n{st.session_state.translated_text}"
            phonetic_resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": phonetic_prompt}]
            )
            st.session_state.phonetic_text = phonetic_resp.choices.message.content.strip()

# --------------- Output (Translated, Phonetic, Audio) ---------------
if st.session_state.translated_text:
    st.markdown(
        f"""<div class="pro-out-card vip">
                <span class="pro-out-title">🌐 Translation <span class="pro-out-vip-label">PRO</span></span>
                <div class="pro-out">{st.session_state.translated_text}</div>
           </div>
        """,
        unsafe_allow_html=True
    )
if st.session_state.phonetic_text:
    st.markdown(
        f"""<div class="pro-out-card">
                <span class="pro-out-title">🔤 Phonetic</span>
                <div class="pro-out">{st.session_state.phonetic_text}</div>
           </div>
        """,
        unsafe_allow_html=True
    )

if st.session_state.translated_text:
    st.markdown('<div class="audio-title">🔊 Play Audio <span style="color:#7E3AF2">PRO</span></div>', unsafe_allow_html=True)
    try:
        tts_lang = lang_map.get(st.session_state.target_lang, "en")
        tts = gTTS(text=st.session_state.translated_text, lang=tts_lang)
        tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tts_file.name)
        st.audio(tts_file.name, format="audio/mp3")
    except Exception as e:
        st.error(f"❌ Speech generation failed: {e}")

# Pro Upsell CTA
st.markdown(
    "<div class='upgrade-cta'>✨ Upgrade to PRO for unlimited translation history, PDF & file translation, advanced voice options, and priority support!</div>",
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)
