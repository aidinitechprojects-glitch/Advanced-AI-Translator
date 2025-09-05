import streamlit as st
from gtts import gTTS
import os
from pydub import AudioSegment
import openai

# Use Streamlit secrets for API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="AI Translator", page_icon="🌍", layout="centered")

st.title("🌍 AI Translator")
st.write("Translate text into different languages and listen to it.")

# Input
text_input = st.text_area("Enter text to translate:", height=150)
target_lang = st.selectbox("Choose target language:", ["French", "Spanish", "German", "Hindi", "Tamil", "Japanese"])

if st.button("Translate"):
    if text_input.strip() == "":
        st.warning("Please enter some text.")
    else:
        with st.spinner("Translating..."):
            # Call OpenAI for translation
            prompt = f"Translate the following text into {target_lang}: {text_input}"
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            translated_text = response.choices[0].message.content

        st.success(f"**Translated ({target_lang}):**")
        st.write(translated_text)

        # Generate speech
        tts = gTTS(text=translated_text, lang="en")  # gTTS auto-detects, but "en" is fallback
        tts.save("output.mp3")

        # Convert MP3 to WAV for Streamlit playback
        sound = AudioSegment.from_mp3("output.mp3")
        sound.export("output.wav", format="wav")

        st.audio("output.wav", format="audio/wav")
