import os
import io
import tempfile
import streamlit as st
from gtts import gTTS
from pydub import AudioSegment
import openai

# -------- Helpers --------

def set_openai_api_key(key: str):
    openai.api_key = key

def save_uploaded_audio(uploaded_file) -> str:
    suffix = os.path.splitext(uploaded_file.name)[1].lower()
    data = uploaded_file.read()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(data)
    tmp.flush()
    tmp.close()

    wav_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio = AudioSegment.from_file(tmp.name)
    audio.export(wav_tmp.name, format="wav")
    return wav_tmp.name

def transcribe_audio(wav_path: str, model: str = "whisper-1") -> str:
    with open(wav_path, "rb") as f:
        transcription = openai.Audio.transcribe(model=model, file=f)
        return transcription.get("text", "") if isinstance(transcription, dict) else str(transcription)

def translate_text(text: str, target_language: str, model: str = "gpt-3.5-turbo") -> str:
    prompt = f"Translate the following text into {target_language}:\n\n{text}"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful translator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
    )
    return response["choices"][0]["message"]["content"].strip()

def text_to_speech(text: str, lang_code: str = "en") -> bytes:
    tts = gTTS(text=text, lang=lang_code, slow=False)
    tmp = io.BytesIO()
    tts.write_to_fp(tmp)
    tmp.seek(0)
    return tmp.read()

# -------- Streamlit UI --------

st.set_page_config(page_title="AI Translator", layout="centered")

st.title("🌍 AI Translator")
st.write("Translate text or audio using OpenAI. Play results as speech with gTTS.")

# Sidebar
st.sidebar.header("⚙️ Settings")
api_key_input = st.sidebar.text_input("OpenAI API Key", type="password")
if api_key_input:
    set_openai_api_key(api_key_input)
elif os.getenv("OPENAI_API_KEY"):
    set_openai_api_key(os.getenv("OPENAI_API_KEY"))

openai_model = st.sidebar.selectbox("Model for translation", ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"])
whisper_model = "whisper-1"

target_language = st.selectbox("Translate to", ["English", "Hindi", "Spanish", "French", "German", "Chinese (Simplified)", "Japanese"])
language_code_map = {"English": "en", "Hindi": "hi", "Spanish": "es", "French": "fr", "German": "de", "Chinese (Simplified)": "zh-cn", "Japanese": "ja"}
tts_lang = language_code_map.get(target_language, "en")

mode = st.radio("Input type", ["Text", "Upload audio"])

original_text, translated_text = "", ""

if mode == "Text":
    text_input = st.text_area("Enter text to translate", height=150)
    if st.button("Translate"):
        if not openai.api_key:
            st.error("Set your OpenAI API key in sidebar or secrets.")
        elif not text_input.strip():
            st.warning("Enter some text first.")
        else:
            original_text = text_input.strip()
            with st.spinner("Translating..."):
                translated_text = translate_text(original_text, target_language, openai_model)

elif mode == "Upload audio":
    uploaded_file = st.file_uploader("Upload audio (mp3/wav/m4a/webm)", type=["mp3", "wav", "m4a", "webm"])
    if uploaded_file and st.button("Transcribe & Translate"):
        if not openai.api_key:
            st.error("Set your OpenAI API key in sidebar or secrets.")
        else:
            with st.spinner("Processing audio..."):
                wav_path = save_uploaded_audio(uploaded_file)
                original_text = transcribe_audio(wav_path, whisper_model)
                translated_text = translate_text(original_text, target_language, openai_model)

if translated_text:
    st.markdown("### ✅ Translation Result")
    st.write("**Original:**", original_text)
    st.write("**Translated:**", translated_text)

    if st.button("🔊 Play Translation"):
        with st.spinner("Generating speech..."):
            try:
                audio_bytes = text_to_speech(translated_text, tts_lang)
                st.audio(audio_bytes, format="audio/mp3")
            except Exception as e:
                st.error(f"TTS failed: {e}")

st.sidebar.markdown("---")
st.sidebar.info("💡 Add your OpenAI API key in **Secrets** when deploying on Streamlit Cloud.")
