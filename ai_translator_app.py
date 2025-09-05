import streamlit as st
from gtts import gTTS
import openai

# Configure Streamlit page
st.set_page_config(page_title="AI Translator", page_icon="🌍", layout="centered")

# ---------- Custom CSS for Modern Look ----------
st.markdown("""
    <style>
    body {
        background-color: #f9fafb;
    }
    .main-title {
        font-size: 2.3rem;
        font-weight: bold;
        text-align: center;
        color: #2563eb;
        margin-bottom: 0.3rem;
    }
    .sub-title {
        text-align: center;
        color: #4b5563;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }
    .stTextArea textarea {
        border-radius: 12px;
        border: 1px solid #d1d5db;
        font-size: 1rem;
        padding: 12px;
    }
    .stSelectbox [data-baseweb="select"] {
        border-radius: 12px;
    }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 12px;
        padding: 0.7rem 1.4rem;
        font-size: 1rem;
        font-weight: 500;
        border: none;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        transform: translateY(-2px);
    }
    .result-card {
        background: white;
        padding: 1.8rem;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin-top: 1.8rem;
    }
    .result-title {
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.6rem;
        font-size: 1.2rem;
    }
    .translated-text {
        font-size: 1.25rem;
        color: #111827;
        margin-bottom: 0.8rem;
        font-weight: 500;
    }
    .phonetic {
        font-size: 1rem;
        color: #10b981; /* green accent */
        font-style: italic;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Page Content ----------
st.markdown("<div class='main-title'>🌍 AI Translator</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Translate across languages with phonetics and audio playback</div>", unsafe_allow_html=True)

# OpenAI API key (from Streamlit secrets)
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
text_input = st.text_area("✍️ Enter text:", height=120)

col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox("🌐 Input Language", list(lang_map.keys()), index=list(lang_map.keys()).index("English"))
with col2:
    target_lang = st.selectbox("🎯 Output Language", list(lang_map.keys()), index=list(lang_map.keys()).index("Hindi"))

# ---------- Translation Workflow ----------
if st.button("🚀 Translate"):
    if text_input.strip() == "":
        st.warning("⚠️ Please enter some text.")
    else:
        with st.spinner("🔄 Translating..."):
            # Strict translation prompt
            translate_prompt = f"""
            Translate the following text from {source_lang} to {target_lang}.
            Return ONLY the translated text, no explanations, no extra words.

            Input: {text_input}
            Output:
            """
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": translate_prompt}]
            )
            translated_text = response.choices[0].message.content.strip()

            # Phonetic transcription
            phonetic_prompt = f"""
            Provide ONLY the phonetic (romanized) transcription of this {target_lang} text.
            No translations, no explanations. Just the phonetic string.

            Text: {translated_text}
            Phonetic:
            """
            phonetic_resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": phonetic_prompt}]
            )
            phonetic_text = phonetic_resp.choices[0].message.content.strip()

        # ---------- Result Card (Only After Translation) ----------
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-title'>✅ Translated to {target_lang}:</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='translated-text'>{translated_text}</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='phonetic'>🔤 {phonetic_text}</div>", unsafe_allow_html=True)

        try:
            tts_lang = lang_map.get(target_lang, "en")
            tts = gTTS(text=translated_text, lang=tts_lang)
            tts.save("output.mp3")
            st.audio("output.mp3", format="audio/mp3")
        except Exception as e:
            st.error(f"❌ Speech generation failed: {e}")

        st.markdown("</div>", unsafe_allow_html=True)  # Close result card
