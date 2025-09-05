import streamlit as st
from gtts import gTTS
import openai
import tempfile
from st_audiorec import st_audiorec  # pip install streamlit-audiorec

# Streamlit page config
st.set_page_config(page_title="AI Translator with Mic", page_icon="🎤", layout="centered")

st.title("🎤 AI Translator with Voice Input")

openai.api_key = st.secrets["OPENAI_API_KEY"]

# Supported languages
lang_map = {
    "English": "en", "Hindi": "hi", "Tamil": "ta", "French": "fr",
    "Spanish": "es", "German": "de", "Japanese": "ja", "Chinese (Mandarin)": "zh-cn"
}

# Language selectors
col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox("🌐 Input Language:", list(lang_map.keys()), index=0)
with col2:
    target_lang = st.selectbox("🎯 Output Language:", list(lang_map.keys()), index=1)

# Mic input
st.markdown("### 🎙️ Record your voice")
wav_audio_data = st_audiorec()  # Returns .wav bytes

if wav_audio_data is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(wav_audio_data)
        audio_path = tmpfile.name

    # Step 1: Transcribe audio
    with st.spinner("🎧 Transcribing..."):
        audio_file = open(audio_path, "rb")
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        transcribed_text = transcript.text
        st.success(f"✅ Transcribed: {transcribed_text}")

    # Step 2: Translate
    with st.spinner("🌍 Translating..."):
        translate_prompt = f"""
        Translate the following text from {source_lang} to {target_lang}.
        Return ONLY the translated text:

        Input: {transcribed_text}
        """
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": translate_prompt}]
        )
        translated_text = response.choices[0].message.content.strip()
        st.markdown(f"### 📝 Translated Text:\n**{translated_text}**")

    # Step 3: Phonetic
    phonetic_prompt = f"Provide the phonetic (romanized) transcription of this {target_lang} text: {translated_text}"
    phonetic_resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": phonetic_prompt}]
    )
    phonetic_text = phonetic_resp.choices[0].message.content.strip()
    st.markdown(f"### 🔤 Phonetic: {phonetic_text}")

    # Step 4: Audio Output
    try:
        tts_lang = lang_map.get(target_lang, "en")
        tts = gTTS(text=translated_text, lang=tts_lang)
        tts.save("output.mp3")
        st.audio("output.mp3", format="audio/mp3")
    except Exception as e:
        st.error(f"❌ Speech generation failed: {e}")
