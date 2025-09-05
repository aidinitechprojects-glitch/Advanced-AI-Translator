import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------------- Streamlit Page Config ----------------
st.set_page_config(page_title="🌍 AI Translator", page_icon="🤖", layout="centered")

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
/* Body & Font */
body {
    background: #0F0F1F;
    color: #ECF0F1;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Header */
.app-header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15px;
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(90deg, #FF6B00, #FF1D75);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}

/* Subtitle - Gradient & Glow Animation */
.subtitle {
    text-align: center;
    font-size: 1.2rem;
    font-weight: 600;
    background: linear-gradient(90deg, #00F0FF, #FF00FF, #FF8C00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: glow 3s ease-in-out infinite alternate;
    margin-bottom: 20px;
}

@keyframes glow {
    0% { text-shadow: 0 0 5px #00F0FF, 0 0 10px #FF00FF; }
    50% { text-shadow: 0 0 10px #FF8C00, 0 0 20px #FF00FF; }
    100% { text-shadow: 0 0 5px #00F0FF, 0 0 15px #FF8C00; }
}

/* Text Area with Scroll */
.stTextArea>div>textarea {
    background-color: #1E1E2F;
    color: #ECF0F1;
    font-size: 16px;
    border-radius: 12px;
    padding: 10px;
    max-height: 200px;
    overflow-y: scroll;
}

/* Gradient Button */
.stButton>button {
    background: linear-gradient(90deg, #FF6B00, #FF1D75);
    color: #FFFFFF;
    font-weight: bold;
    border-radius: 15px;
    height: 50px;
    width: 100%;
    font-size: 18px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
    transition: all 0.3s ease;
    box-shadow: 0px 4px 15px rgba(255,107,0,0.5);
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0px 6px 25px rgba(255,107,0,0.7);
}

/* Output Boxes - Glassmorphism */
.output-box {
    backdrop-filter: blur(10px);
    background: rgba(255,255,255,0.05);
    border-radius: 25px;
    padding: 20px;
    box-shadow: 0px 8px 30px rgba(0,0,0,0.6);
    margin-bottom: 20px;
}

/* Output Headings */
.output-heading {
    font-weight: 700;
    font-size: 20px;
    background: linear-gradient(90deg, #FF6B00, #FF1D75);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

/* Output Text */
.output-text {
    font-size: 18px;
    color: #ECF0F1;
    max-height: 150px;
    overflow-y: auto;
}

/* Swap & Copy buttons */
.swap-button, .copy-button {
    margin-top: 5px;
    margin-bottom: 10px;
    font-size: 14px;
    font-weight: bold;
}

/* Divider Line */
.divider {
    height: 2px;
    background: linear-gradient(90deg, #FF6B00, #FF1D75);
    margin: 20px 0;
    border-radius: 2px;
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
st.markdown('<div class="subtitle">🌐 AI-powered multilingual translator with phonetic transcription and natural speech playback</div>', unsafe_allow_html=True)

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
    if st.button("🔄 Swap", key="swap"):
        source_lang, target_lang = target_lang, source_lang

# Clear button
if st.button("Clear"):
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

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

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
