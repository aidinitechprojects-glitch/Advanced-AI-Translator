import streamlit as st
from gtts import gTTS
import openai

# Configure Streamlit page
st.set_page_config(page_title="AI Translator", page_icon="🌍", layout="centered")

# Modern CSS styling
st.markdown("""
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
        .main-title {
            font-size: 2.8rem;
            font-weight: 900;
            text-align: center;
            background: linear-gradient(90deg, #2563eb, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.3rem;
        }
        .sub-title {
            text-align: center;
            font-size: 1.1rem;
            color: #6b7280;
            margin-bottom: 2rem;
        }
        textarea {
            border-radius: 14px !important;
            border: 1px solid #d1d5db !important;
            font-size: 1rem !important;
            padding: 0.8rem !important;
        }
        .result-card {
            background: linear-gradient(135deg, #f9fafb, #e0f2fe);
            padding: 2rem;
            border-radius: 18px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
            margin-top: 2rem;
            transition: all 0.3s ease-in-out;
        }
        .result-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }
        .translated-text {
            font-size: 1.6rem;
            color: #111827;
            font-weight: 800;
            margin-bottom: 1rem;
            text-align: center;
        }
        .phonetic {
            font-size: 1.15rem;
            color: #0f766e;
            font-style: italic;
            text-align: center;
        }
        .stAudio {
            margin-top: 1.2rem;
        }
        .translate-btn button {
            background: linear-gradient(90deg, #2563eb, #06b6d4) !important;
            color: white !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            padding: 0.6rem 1.4rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<div class='main-title'>🌍 AI Translator</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Translate between multiple languages with phonetics and speech playback.</div>", unsafe_allow_html=True)

# OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Supported languages for gTTS
lang_map = {
    # Indian Languages
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Gujarati": "gu",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Bengali": "bn",
    "Urdu": "ur",
    "Odia": "or",

    # Foreign Languages
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese (Mandarin)": "zh-cn",
    "Arabic": "ar",
    "Turkish": "tr",
    "Dutch": "nl",
    "Greek": "el",
    "Polish": "pl",
    "Swedish": "sv",
}

# Input fields
text_input = st.text_area("✍️ Enter text:", height=150)

col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox("🌐 Input Language:", list(lang_map.keys()), index=list(lang_map.keys()).index("English"))
with col2:
    target_lang = st.selectbox("🎯 Output Language:", list(lang_map.keys()), index=list(lang_map.keys()).index("Hindi"))

# Translate button with style
st.markdown("<div class='translate-btn'>", unsafe_allow_html=True)
if st.button("🚀 Translate"):
    if text_input.strip() == "":
        st.warning("⚠️ Please enter some text.")
    else:
        with st.spinner("Translating..."):
            # Translation prompt (strict output)
            translate_prompt = f"""
            Translate the following text from {source_lang} to {target_lang}.
            Return ONLY the translated text, nothing else:

            Input: {text_input}
            Output:
            """
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": translate_prompt}]
            )
            translated_text = response.choices[0].message.content.strip()

            # Phonetic transcription
            phonetic_prompt = f"Provide the phonetic (romanized) transcription of this {target_lang} text: {translated_text}"
            phonetic_resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": phonetic_prompt}]
            )
            phonetic_text = phonetic_resp.choices[0].message.content.strip()

        # Results in modern card
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='translated-text'>{translated_text}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='phonetic'>🔤 {phonetic_text}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Speech synthesis
        try:
            tts_lang = lang_map.get(target_lang, "en")
            tts = gTTS(text=translated_text, lang=tts_lang)
            tts.save("output.mp3")
            st.audio("output.mp3", format="audio/mp3")
        except Exception as e:
            st.error(f"❌ Speech generation failed: {e}")
st.markdown("</div>", unsafe_allow_html=True)
