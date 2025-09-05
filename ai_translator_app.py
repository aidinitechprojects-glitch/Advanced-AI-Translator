import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------- Page Config ----------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")

# ---------- Custom CSS ----------
st.markdown("""
<style>
body, [data-testid="stAppViewContainer"] {background:linear-gradient(120deg,#ece9f3 60%,#fff8ed 115%);}
.pro-glass {background:rgba(255,255,255,0.91);border-radius:28px;box-shadow:0 12px 56px 0 #bf7cf328,0 0.5px 2px #00000012;padding:38px;margin:28px 0;}
.pro-header {display:flex;align-items:center;justify-content:space-between;margin-bottom:0;}
.pro-title {font-size:2.4rem;font-weight:900;letter-spacing:.03em;background:linear-gradient(90deg,#ff7a18,#af002d 70%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.pro-badge {font-size:1.05rem;background:linear-gradient(90deg,#af002d,#ff7a18 95%);color:#fff;border-radius:8px;padding:4px 20px;margin-left:16px;font-weight:500;box-shadow:0 1px 7px #af002d22;}
.pro-subtitle {font-size:1.13rem;color:#2b2542;font-weight:500;text-align:left;margin-bottom:24px;margin-top:4px;}
textarea {background:rgba(255,245,230,0.97)!important;border-radius:19px!important;font-size:1.11rem;color:#222!important;border:2px solid #ffd6b7!important;box-shadow:0 4px 24px #ff7a1812;max-height:150px;overflow-y:auto;}
textarea:focus {border:2.5px solid #ff7a18!important;background:#fff9f0!important;}
.pro-swap-btn {width:44px;height:44px;background:linear-gradient(90deg,#3a86ff,#ff7a18);color:#fff;border-radius:50%;font-size:1.25rem;border:none;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 20px #ff7a1810;transition:filter .2s;}
.pro-swap-btn:hover {filter:brightness(1.13);}
.pro-btn {width:320px;padding:.7em 0;margin-top:15px;background:linear-gradient(90deg,#af002d,#ff7a18 75%);color:#fff;border:none;border-radius:13px;font-size:1.17rem;font-weight:bold;box-shadow:0 5px 18px #ff7a1825;transition:filter .18s,box-shadow .13s;margin:auto;display:block;}
.pro-btn:hover {filter:brightness(1.13);}
.clear-btn {background:#857fa4cc!important;color:#fff!important;border-radius:11px;font-size:14px;margin-top:6px;float:right;width:80px;}
.pro-out-card {background:rgba(255,245,230,0.98);border-radius:17px;padding:16px 14px 12px 14px;box-shadow:0 3px 13px #ff7a1817;margin-bottom:17px;max-height:160px;overflow-y:auto;}
.pro-out-title {font-weight:700;font-size:1.05rem;letter-spacing:.01em;color:#af002d;margin-bottom:4px;}
.pro-out {font-size:1.05rem;color:#1d1728;}
.audio-title {font-weight:700;font-size:1.11rem;color:#ff7a18;text-align:center;margin-bottom:8px;}
.upgrade-cta {margin-top:13px;text-align:center;background:linear-gradient(90deg,#ff7a18,#af002d 85%);color:#fff;font-size:1.09rem;font-weight:700;border-radius:13px;padding:8px 0 7px 0;box-shadow:0 4px 14px #ff7a1817;}
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
st.markdown("<div class='pro-subtitle'>Premium AI translation—text, phonetic & audio in one click.</div>", unsafe_allow_html=True)
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

col1, col2, col3 = st.columns([3.5,1,3.5])
with col1:
    st.session_state.source_lang = st.selectbox("From", sorted_langs, index=sorted_langs.index(st.session_state.source_lang))
with col2:
    st.markdown('<div style="height:38px;"></div>', unsafe_allow_html=True)
    if st.button("⇆", key="swap"):
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
with col3:
    st.session_state.target_lang = st.selectbox("To", sorted_langs, index=sorted_langs.index(st.session_state.target_lang))

# ---------- Input Text Area ----------
st.session_state.text_input = st.text_area("Text to translate", value=st.session_state.text_input, height=120, placeholder="Type or paste text...")

# ---------- Clear + Translate Buttons ----------
btn_col1, btn_col2 = st.columns([1,5])
with btn_col1:
    if st.button("Clear", key="clear", use_container_width=True):
        st.session_state.text_input = ""
        st.session_state.translated_text = ""
        st.session_state.phonetic_text = ""
        st.experimental_rerun()
with btn_col2:
    translate_clicked = st.button("Translate", key="translate", use_container_width=True)

# ---------- OpenAI Translation ----------
openai.api_key = st.secrets["OPENAI_API_KEY"]
if translate_clicked:
    if st.session_state.text_input.strip() == "":
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

# ---------- Output ----------
if st.session_state.translated_text:
    st.markdown(f"<div class='pro-out-card'><span class='pro-out-title'>🌐
