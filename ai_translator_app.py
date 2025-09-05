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
    margin-bottom: 30px;
}

@keyframes glow {
    0% { text-shadow: 0 0 5px #00F0FF, 0 0 10px #FF00FF; }
    50% { text-shadow: 0 0 10px #FF8C00, 0 0 20px #FF00FF; }
    100% { text-shadow: 0 0 5px #00F0FF, 0 0 15px #FF8C00; }
}

/* Text Area */
.stTextArea>div>textarea {
    background-color: #1E1E2F;
    color: #ECF0F1;
    font-size: 16px;
    border-radius: 12px;
    padding: 10px;
}

/* Gradient Button */
.stButton>button {
    background: linear-gradient(90deg, #FF6B00, #FF1D75);
    color: #FFFFFF;
    font-weight: bold;
    border-radius: 15px;
    height: 55px;
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
    padding: 25px;
    box-shadow: 0px 8px 30px rgba(0,0,0,0.6);
    margin-bottom: 25px;
    transition: all 0.3s ease;
}
.output-box:hover {
    transform: translateY(-3px);
    box-shadow: 0px 10px 40px rgba(255,255,255,0.1);
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
}

/* Divider Line */
.divider {
    height: 2px;
    background: linear-gradient(90deg, #FF6B00, #FF1D75);
    margin: 25px 0;
    border-radius: 2px;
    animation: slideIn 0.6s ease-in-out;
}

@keyframes slideIn {
    from { width: 0%; opacity:0; }
    to { width: 100%; opacity:1; }
}
</style>
""", unsafe_allow_html=True)

# ---------------- Page Header ----------------
st.markdown('<div class="app-header">🤖 AI Translator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">🌐 AI-powered multilingual translator with phonetic transcription and natural speech playback</div>', unsafe_allow_html=True)

# ---------------- OpenAI API Key ----------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ---------------- Supported Languages ----------------
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

# ---------------- Input Fields ----------------
text_input = st.text_area("Enter your text:", height=150)
col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox("Input Language:", list(lang_map.keys()), index=list(lang_map.keys()).index("English"))
with col2:
    target_lang = st.selectbox("Output Language:", list(lang_map.keys()), index=list(lang_map.keys()).index("Hindi"))

# ---------------- Translate Button ----------------
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

            # Phonetic transcription
            phonetic_prompt = f"Provide only the phonetic (romanized) transcription of this {target_lang} text:\n{translated_text}"
            phonetic_resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": phonetic_prompt}]
            )
            phonetic_text = phonetic_resp.choices[0].message.content.strip()

        # ---------------- Display Outputs ----------------
        st.markdown('<div class="output-box">'
                    '<div class="output-heading">🌐 Translated ({})</div>'
                    '<div class="output-text">{}</div></div>'.format(target_lang, translated_text),
                    unsafe_allow_html=True)

        st.markdown('<div class="output-box">'
                    '<div class="output-heading">🔤 Phonetic</div>'
                    '<div class="output-text">{}</div></div>'.format(phonetic_text),
                    unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # ---------------- Generate Audio ----------------
        try:
            tts_lang = lang_map.get(target_lang, "en")
            tts = gTTS(text=translated_text, lang=tts_lang)
            tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(tts_file.name)
            st.audio(tts_file.name, format="audio/mp3")
        except Exception as e:
            st.error(f"❌ Speech generation failed: {e}")
