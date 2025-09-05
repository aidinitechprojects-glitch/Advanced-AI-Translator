import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------------- Page Config ----------------
st.set_page_config(page_title="🌍 AI Translator", page_icon="🤖", layout="centered")

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

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
body { background-color: #0F0F1F; color: #ECF0F1; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.app-header { text-align: center; font-size: 2.5rem; font-weight: 800; color: #FF6B00; margin-bottom: 5px; }
.subtitle { text-align: center; font-size: 1.2rem; font-weight: 500; color: #FFFFFF; margin-bottom: 20px; }
.stTextArea>div>textarea { background-color: #1E1E2F; color: #ECF0F1; font-size: 16px; border-radius: 10px; padding: 10px; max-height: 200px; overflow-y: auto; }
.stButton>button { font-weight: bold; border-radius: 10px; height: 40px; font-size: 16px; }
.translate-button { background: #FF6B00; color: #FFFFFF; width: 100%; }
.swap-button { background: #FF1D75; color: #FFFFFF; font-size: 14px; height: 35px; margin-top: 23px; }
.clear-button { background: #555555; color: #FFFFFF; font-size: 14px; height: 30px; width: 90px; float: right; margin-top: 5px; }
.output-box { background: #1E1E2F; border-radius: 10px; padding: 15px; margin-bottom: 15px; }
.output-heading { font-weight: 700; font-size: 16px; color: #FF6B00; margin-bottom: 5px; }
.output-text { font-size: 14px; color: #ECF0F1; max-height: 150px; overflow-y: auto; }
.audio-title { font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #FF6B00; }
</style>
""", unsafe_allow_html=True)

# ---------------- Header ----------------
st.markdown('<div class="app-header">🤖 AI Translator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Translate text across languages with phonetics & audio playback</div>', unsafe_allow_html=True)

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

# ---------------- Input Section ----------------
st.session_state.text_input = st.text_area("Enter your text:", value=st.session_state.text_input, height=150)

# ---------------- Languages with Swap ----------------
col1, col2, col3 = st.columns([4,1,4])
with col1:
    st.session_state.source_lang = st.selectbox("Input Language:", list(lang_map.keys()), index=list(lang_map.keys()).index(st.session_state.source_lang))
with col2:
    if st.button("🔄", key="swap", help="Swap languages"):
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
with col3:
    st.session_state.target_lang = st.selectbox("Output Language:", list(lang_map.keys()), index=list(lang_map.keys()).index(st.session_state.target_lang))

# ---------------- Clear Button ----------------
col_clear = st.container()
with col_clear:
    if st.button("Clear", key="clear", help="Clear input and outputs"):
        st.session_state.text_input = ""
        st.session_state.translated_text = ""
        st.session_state.phonetic_text = ""
        st.experimental_rerun()

# ---------------- Translate ----------------
if st.button("Translate", key="translate"):
    if st.session_state.text_input.strip() == "":
        st.warning("⚠️ Please enter some text.")
    else:
        with st.spinner("Translating..."):
            # Translation
            translate_prompt = f"Translate the following text from {st.session_state.source_lang} to {st.session_state.target_lang}. Only provide the translated sentence:\n{st.session_state.text_input}"
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": translate_prompt}]
            )
            st.session_state.translated_text = response.choices[0].message.content.strip()

            # Phonetic
            phonetic_prompt = f"Provide only the phonetic (romanized) transcription of this {st.session_state.target_lang} text:\n{st.session_state.translated_text}"
            phonetic_resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": phonetic_prompt}]
            )
            st.session_state.phonetic_text = phonetic_resp.choices[0].message.content.strip()

        # ---------------- Display Outputs ----------------
        st.markdown(f'''
        <div class="output-box">
            <div class="output-heading">🌐 Translated ({st.session_state.target_lang})</div>
            <div class="output-text">{st.session_state.translated_text}</div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown(f'''
        <div class="output-box">
            <div class="output-heading">🔤 Phonetic</div>
            <div class="output-text">{st.session_state.phonetic_text}</div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('<div class="audio-title">🔊 Play Translated Audio</div>', unsafe_allow_html=True)
        try:
            tts_lang = lang_map.get(st.session_state.target_lang, "en")
            tts = gTTS(text=st.session_state.translated_text, lang=tts_lang)
            tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(tts_file.name)
            st.audio(tts_file.name, format="audio/mp3")
        except Exception as e:
            st.error(f"❌ Speech generation failed: {e}")
