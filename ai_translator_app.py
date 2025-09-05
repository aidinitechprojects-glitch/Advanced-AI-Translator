import streamlit as st
from gtts import gTTS
import openai

# Configure Streamlit page
st.set_page_config(page_title="AI Translator", page_icon="🌍", layout="centered")

st.title("🌍 AI Translator")
st.write("Translate text into different languages and listen to the result.")

# OpenAI API key (from Streamlit secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Full language map for gTTS (common Indian + foreign languages)
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

    # Popular Foreign Languages
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

# Input area
text_input = st.text_area("Enter text to translate:", height=150)
target_lang = st.selectbox("Choose target language:", list(lang_map.keys()))

if st.button("Translate"):
    if text_input.strip() == "":
        st.warning("⚠️ Please enter some text.")
    else:
        with st.spinner("Translating..."):
            # Ask OpenAI for translation
            prompt = f"Translate the following text into {target_lang}: {text_input}"
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            translated_text = response.choices[0].message.content

        st.success(f"**Translated ({target_lang}):**")
        st.write(translated_text)

        # Generate TTS with gTTS
        try:
            tts_lang = lang_map.get(target_lang, "en")
            tts = gTTS(text=translated_text, lang=tts_lang)
            tts.save("output.mp3")

            st.audio("output.mp3", format="audio/mp3")

            # Optional: download button
            with open("output.mp3", "rb") as file:
                st.download_button(
                    label="⬇️ Download Audio",
                    data=file,
                    file_name=f"translation_{tts_lang}.mp3",
                    mime="audio/mp3"
                )
        except Exception as e:
            st.error(f"❌ Speech generation failed: {e}")
