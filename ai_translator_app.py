import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------------- Streamlit Page Config ----------------
st.set_page_config(page_title="🌍 AI Translator", page_icon="🤖", layout="centered")

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
body {
    background: #0F0F1F;
    color: #ECF0F1;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Header */
.app-header {
    text-align: center;
    font-size: 3rem;
    font-weight: 900;
    color: #FF6B00;
    margin-bottom: 5px;
    font-family: 'Lucida Console', Courier, monospace;
}

/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 1.3rem;
    font-weight: 600;
    color: #FFFFFF;
    margin-bottom: 20px;
}

/* Text Area with Scroll */
.stTextArea>div>textarea {
    background-color: #1E1E2F;
    color: #ECF0F1;
    font-size: 16px;
    border-radius: 12px;
    padding: 10px;
    max-height: 200px;
    overflow-y: auto;
}

/* Buttons */
.stButton>button {
    background: #FF6B00;
    color: #FFFFFF;
    font-weight: bold;
    border-radius: 12px;
    height: 40px;
    width: 100%;
    font-size: 16px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
    transition: all 0.2s ease;
}
.stButton>button:hover {
    transform: scale(1.05);
}

/* Swap Button smaller */
.swap-button {
    background: #FF1D75;
    color: #FFFFFF;
    font-size: 14px;
    height: 35px;
}

/* Clear Button smaller */
.clear-button {
    background: #555555;
    color: #FFFFFF;
    font-size: 14px;
    height: 30px;
    width: 100px;
    float: right;
    margin-top: 5px;
}

/* Output Boxes */
.output-box {
    backdrop-filter: blur(10px);
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0px 8px 30px rgba(0,0,0,0.6);
    margin-bottom: 20px;
}

/* Output Headings */
.output-heading {
    font-weight: 700;
    font-size: 20px;
    color: #FF6B00;
    margin-bottom: 10px;
}

/* Output Text */
.output-text {
    font-size: 18px;
    color: #ECF0F1;
    max-height: 150px;
    overflow-y: auto;
}

/* Copy Buttons */
.copy-button {
    font-size: 14px;
    margin-top: 5px;
    margin-bottom: 10px;
}

/* Audio Title */
.audio-title {
    font-weight: bold;
    font-size: 18px;
    margin-bottom: 10px;
    color: #FF6B00;
}
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
text_input = st.text_area("Enter your text:", height=150)

col1, col2, col3 = st.columns([1,1,0.3])
with col1:
    source_lang = st.selectbox("Input Language:", list(lang_map.keys()), index=list(lang_map.keys()).index("English"))
with col2:
    target_lang = st.selectbox("Output Language:", list(lang_map.keys()), index=list(lang_map.keys()).index("Hindi"))
with col3:
    if st.button("🔄 Swap", key="swap", help="Swap languages and input text"):
        # Swap languages
        source_lang, target_lang = target_lang, source_lang
        # Swap text input with translated output if available
        try:
            text_input, translated_text = translated_text, text_input
        except NameError:
            pass
        st.experimental_rerun()

# ---------------- Clear Button under Input Box ----------------
clear_col1, clear_col2 = st.columns([0.85,0.15])
with clear_col2:
    if st.button("Clear", key="clear", help="Clear input text"):
        text_input = ""
        st.experimental_rerun()

# ---------------- Translate ----------------
if st.button("Translate"):
    if text_input.strip() == "":
        st.warning("⚠️ Please enter some text.")
    else:
        with st.spinner("Translating..."):
            # Translation
            translate_prompt = f"Translate the following text from {source_lang} to {target_lang}. Only provide the translated sentence:\n{text_input}"
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": translate_prompt}]
            )
            translated_text = response.choices[0].message.content.strip()

            # Phonetic
            phonetic_prompt = f"Provide only the phonetic (romanized) transcription of this {target_lang} text:\n{translated_text}"
            phonetic_resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": phonetic_prompt}]
            )
            phonetic_text = phonetic_resp.choices[0].message.content.strip()

        # ---------------- Display Outputs ----------------
        # Translated text with copy
        st.markdown('<div class="output-box">'
                    '<div class="output-heading">🌐 Translated ({})</div>'
                    '<div class="output-text">{}</div></div>'.format(target_lang, translated_text),
                    unsafe_allow_html=True)
        if st.button("📋 Copy Translated", key="copy1"):
            st.experimental_set_clipboard(translated_text)

        # Phonetic with copy
        st.markdown('<div class="output-box">'
                    '<div class="output-heading">🔤 Phonetic</div>'
                    '<div class="output-text">{}</div></div>'.format(phonetic_text),
                    unsafe_allow_html=True)
        if st.button("📋 Copy Phonetic", key="copy2"):
            st.experimental_set_clipboard(phonetic_text)

        # Audio playback with title
        st.markdown('<div class="audio-title">🔊 Play Translated Audio</div>', unsafe_allow_html=True)
        try:
            tts_lang = lang_map.get(target_lang, "en")
            tts = gTTS(text=translated_text, lang=tts_lang)
            tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(tts_file.name)
            st.audio(tts_file.name, format="audio/mp3")
        except Exception as e:
            st.error(f"❌ Speech generation failed: {e}")
