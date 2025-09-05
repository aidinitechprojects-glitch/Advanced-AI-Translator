import streamlit as st
from gtts import gTTS
import openai

# Configure Streamlit page
st.set_page_config(page_title="AI Translator", page_icon="🌍", layout="centered")

# Inject custom CSS
st.markdown("""
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
        .main-title {
            font-size: 2.5rem;
            font-weight: 800;
            color: #2563eb;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .sub-title {
            text-align: center;
            font-size: 1.1rem;
            color: #6b7280;
            margin-bottom: 2rem;
        }
        textarea {
            border-radius: 12px !important;
            border: 1px solid #d1d5db !important;
        }
        .result-card {
            background: #f3f4f6; /* light gray background */
            padding: 1.8rem;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            margin-top: 1.8rem;
        }
        .translated-text {
            font-size: 1.35rem;
            color: #111827; /* dark text */
            font-weight: 700;
            margin-bottom: 1rem;
        }
        .phonetic {
            font-size: 1.1rem;
            color: #374151;
            font-style: italic;
        }
        .stAudio {
            margin-top: 1rem;
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

# Translate
if st.button("🚀 Translate"):
    if text_input.strip() == "":
        st.warning("⚠️ Please enter some text.")
    else:
        with st.spinner("Translating..."):
            # Translation prompt (strict to avoid explanations)
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

        # Show results inside styled card
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
