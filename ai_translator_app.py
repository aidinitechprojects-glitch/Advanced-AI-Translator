import streamlit as st
from gtts import gTTS
import openai

# Configure Streamlit page
st.set_page_config(page_title="AI Translator", page_icon="🌍", layout="centered")

st.title("🌍 AI Translator")
st.write("Translate text into different languages and listen to the result.")

# OpenAI API key (from Streamlit secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Input area
text_input = st.text_area("Enter text to translate:", height=150)
target_lang = st.selectbox(
    "Choose target language:",
    ["French", "Spanish", "German", "Hindi", "Tamil", "Japanese"]
)

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
            # NOTE: gTTS lang parameter must be an ISO code (not full name).
            # Map supported languages manually if needed.
            lang_map = {
                "French": "fr",
                "Spanish": "es",
                "German": "de",
                "Hindi": "hi",
                "Tamil": "ta",
                "Japanese": "ja"
            }
            tts_lang = lang_map.get(target_lang, "en")
            tts = gTTS(text=translated_text, lang=tts_lang)
            tts.save("output.mp3")

            st.audio("output.mp3", format="audio/mp3")
        except Exception as e:
            st.error(f"❌ Speech generation failed: {e}")
