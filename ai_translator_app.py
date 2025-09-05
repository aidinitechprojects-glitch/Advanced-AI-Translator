import streamlit as st
import openai
from gtts import gTTS
import tempfile
from st_mic_recorder import mic_recorder
import wave

# Streamlit page
st.set_page_config(page_title="AI Translator", page_icon="🌍", layout="wide")

st.markdown(
    "<h1 style='text-align:center;color:#4CAF50'>🌍 AI Translator</h1>", unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;color:#888'>Speak or type → Translate instantly with phonetics & audio</p>",
    unsafe_allow_html=True
)

# OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Supported languages
lang_map = {
    "English":"en", "Hindi":"hi", "Tamil":"ta", "Telugu":"te", "Kannada":"kn",
    "Malayalam":"ml", "French":"fr", "Spanish":"es", "German":"de", "Chinese":"zh-cn",
    "Japanese":"ja"
}

# ----------------- Controls -----------------
col1, col2 = st.columns(2)
with col1:
    input_lang = st.selectbox("Input Language", list(lang_map.keys()), index=list(lang_map.keys()).index("English"))
with col2:
    output_lang = st.selectbox("Target Language", list(lang_map.keys()), index=list(lang_map.keys()).index("Hindi"))

# ----------------- Text input -----------------
st.markdown("### 📝 Type your text")
text_input = st.text_area("Enter text (optional):", height=100)

# ----------------- Voice input -----------------
st.markdown("### 🎤 Record your voice")
voice_input = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", just_once=True)

# Decide source text
source_text = None
if voice_input:
    # Save raw bytes to temporary WAV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        with wave.open(f.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(voice_input["bytes"])
        wav_file_path = f.name
    # Transcribe
    with open(wav_file_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )
    source_text = transcript.text
elif text_input.strip() != "":
    source_text = text_input.strip()
else:
    source_text = None

if source_text:
    st.markdown(f"**📝 Transcribed / Input Text:** {source_text}")

    # Translation
    translate_prompt = f"Translate the following {input_lang} text to {output_lang}. Only give the translated sentence:\n\n{source_text}"
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": translate_prompt}]
    )
    translated_text = response.choices[0].message.content.strip()
    st.markdown(f"**🌐 Translated Text:** {translated_text}")

    # Phonetic
    phonetic_prompt = f"Provide only the phonetic transcription of this {output_lang} sentence:\n{translated_text}"
    phonetic_resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": phonetic_prompt}]
    )
    phonetic_text = phonetic_resp.choices[0].message.content.strip()
    st.markdown(f"**🔤 Phonetic:** {phonetic_text}")

    # TTS
    tts = gTTS(translated_text, lang=lang_map.get(output_lang, "en"))
    tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tts_file.name)
    st.audio(tts_file.name, format="audio/mp3")
