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
        /* Title styling */
        .main-title {
            font-size: 3rem;
            font-weight: 900;
            text-align: center;
            margin-bottom: 0.2rem;
            background: linear-gradient(90deg, #06b6d4, #3b82f6, #9333ea);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .logo {
            font-size: 3.2rem;
            display: inline-block;
            margin-right: 0.5rem;
        }
        .sub-title {
            text-align: center;
            font-size: 1.2rem;
            color: #6b7280;
            margin-bottom: 2rem;
        }

        /* Input box */
        textarea {
            border-radius: 14px !important;
            border: 1px solid #d1d5db !important;
            font-size: 1rem !important;
            padding: 0.8rem !important;
        }

        /* Section card */
        .section-card {
            background: #ffffff;
            border-radius: 14px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.1);
            margin-top: 1.5rem;
            padding: 0;
            overflow: hidden;
        }
        .section-header {
            padding: 0.8rem 1rem;
            font-size: 1.1rem;
            font-weight: 700;
            color: #ffffff;
        }
        .section-body {
            padding: 1.2rem;
        }

        /* Gradient headers */
        .header-translate { background: linear-gradient(90deg, #3b82f6, #06b6d4); }
        .header-phonetic { background: linear-gradient(90deg, #10b981, #84cc16); }
        .header-audio { background: linear-gradient(90deg, #9333ea, #ec4899); }

        /* Text styles */
        .translated-text {
            font-size: 1.8rem;
            font-weight: 900;
            background: linear-gradient(90deg, #2563eb, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.15);
            margin-bottom: 1rem;
        }
        .phonetic-text {
            font-size: 1.3rem;
            font-weight: 700;
            color: #047857;
            line-height: 1.6;
        }
        .stAudio {
            margin-top: 0.5rem;
        }

        /* Translate button */
        .translate-btn button {
            background: linear-gradient(90deg, #2563eb, #06b6d4) !important;
            color: white !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            padding: 0.6rem 1.4rem !important;
            transition: all 0.3s ease-in-out;
        }
        .translate-btn button:hover {
            transform: scale(1.05);
            box-shadow: 0px 4px 14px rgba(0,0,0,0.15);
        }
    </style>
""", unsafe_allow_html=True)

# Title with emoji logo
st.markdown("<div class='logo'>🌍</div><div class='main-title'>AI Translator</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Your multilingual companion with phonetics & speech playback ✨</div>", unsafe_allow_html=True)

# OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Supported languages for gTTS
lang_map = {
    # Indian Languages
    "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Kannada": "kn",
    "Malayalam": "ml", "Gujarati": "gu", "Marathi": "mr", "Punjabi": "pa",
    "Bengali": "bn", "Urdu": "ur", "Odia": "or",

    # Foreign Languages
    "English": "en", "French": "fr", "Spanish": "es", "German": "de",
    "Italian": "it", "Portuguese": "pt", "Russian": "ru", "Japanese": "ja",
    "Korean": "ko", "Chinese (Mandarin)": "zh-cn", "Arabic": "ar",
    "Turkish": "tr", "Dutch": "nl", "Greek": "el", "Polish": "pl", "Swedish": "sv",
}

# Input fields
text_input = st.text_area("✍️ Enter text:", height=150)

col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox("🌐 Input Language:", list(lang_map.keys()), index=list(lang_map.keys()).index("English"))
with col2:
    target_lang = st.selectbox("🎯 Output Language:", list(lang_map.keys()), index=list(lang_map.keys()).index("Hindi"))

# Translate button
st.markdown("<div class='translate-btn'>", unsafe_allow_html=True)
if st.button("🚀 Translate"):
    if text_input.strip() == "":
        st.warning("⚠️ Please enter some text.")
    else:
        with st.spinner("Translating..."):
            # Translation prompt
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

        # Section 1: Translated Text
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header header-translate'>📝 Translated Text</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='section-body'><div class='translated-text'>{translated_text}</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Section 2: Phonetic
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header header-phonetic'>🔤 Phonetic (Romanized)</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='section-body'><div class='phonetic-text'>{phonetic_text}</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Section 3: Audio
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header header-audio'>🔊 Listen</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-body'>", unsafe_allow_html=True)
        try:
            tts_lang = lang_map.get(target_lang, "en")
            tts = gTTS(text=translated_text, lang=tts_lang)
            tts.save("output.mp3")
            st.audio("output.mp3", format="audio/mp3")
        except Exception as e:
            st.error(f"❌ Speech generation failed: {e}")
        st.markdown("</div></div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
