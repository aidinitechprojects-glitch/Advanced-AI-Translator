import streamlit as st
import openai
from gtts import gTTS
import tempfile
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av

# Configure Streamlit page
st.set_page_config(page_title="🌍 AI Translator", page_icon="🎤", layout="centered")

st.markdown(
    """
    <h1 style="text-align:center; color:#4CAF50;">
        🎤 AI Voice Translator
    </h1>
    <p style="text-align:center; font-size:18px; color:#888;">
        Speak in your language → Translated instantly with phonetics + audio
    </p>
    """,
    unsafe_allow_html=True,
)

# OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Supported languages for gTTS
lang_map = {
    # Indian
    "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Kannada": "kn",
    "Malayalam": "ml", "Gujarati": "gu", "Marathi": "mr", "Punjabi": "pa",
    "Bengali": "bn", "Urdu": "ur", "Odia": "or",

    # Foreign
    "English": "en", "French": "fr", "Spanish": "es", "German": "de",
    "Italian": "it", "Portuguese": "pt", "Russian": "ru", "Japanese": "ja",
    "Korean": "ko", "Chinese (Mandarin)": "zh-cn", "Arabic": "ar",
    "Turkish": "tr", "Dutch": "nl", "Greek": "el", "Polish": "pl",
    "Swedish": "sv",
}

# --- UI selections ---
col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox("🎙️ Input Language", list(lang_map.keys()), index=list(lang_map.keys()).index("English"))
with col2:
    target_lang = st.selectbox("🌐 Output Language", list(lang_map.keys()), index=list(lang_map.keys()).index("Hindi"))

# --- Mic Recorder ---
st.subheader("🎤 Record Your Voice")
st.write("Click **Start** and speak in your input language, then stop recording.")

class AudioProcessor(AudioProcessorBase):
    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        return frame

webrtc_ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDRECV,
    audio_receiver_size=256,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

# --- Process Recorded Audio ---
if webrtc_ctx.audio_receiver:
    audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
    if audio_frames:
        audio = audio_frames[0].to_ndarray().flatten().tobytes()

        # Save temp WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
            tmp_wav.write(audio)
            wav_path = tmp_wav.name

        # Send to OpenAI for transcription
        with open(wav_path, "rb") as af:
            transcript = openai.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=af
            )

        raw_text = transcript.text.strip()

        if raw_text:
            st.markdown(
                f"<div style='background:#1E1E1E; padding:12px; border-radius:10px;'><b style='color:#00FFAA;'>📝 Transcribed:</b><br><span style='color:white; font-size:18px;'>{raw_text}</span></div>",
                unsafe_allow_html=True
            )

            # Translation
            translate_prompt = f"Translate the following text from {source_lang} to {target_lang}. Only give the translated sentence:\n{raw_text}"
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": translate_prompt}]
            )
            translated_text = response.choices[0].message.content.strip()

            st.markdown(
                f"<div style='background:#2C2C54; padding:12px; border-radius:10px;'><b style='color:#FFD700;'>🌍 Translated ({target_lang}):</b><br><span style='color:#FFFFFF; font-size:20px;'>{translated_text}</span></div>",
                unsafe_allow_html=True
            )

            # Phonetic
            phonetic_prompt = f"Provide the phonetic (romanized) transcription of this {target_lang} text: {translated_text}"
            phonetic_resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": phonetic_prompt}]
            )
            phonetic_text = phonetic_resp.choices[0].message.content.strip()

            st.markdown(
                f"<div style='background:#34495E; padding:12px; border-radius:10px;'><b style='color:#00CED1;'>🔤 Phonetic:</b><br><span style='color:#ECF0F1; font-size:18px;'>{phonetic_text}</span></div>",
                unsafe_allow_html=True
            )

            # TTS
            try:
                tts_lang = lang_map.get(target_lang, "en")
                tts = gTTS(text=translated_text, lang=tts_lang)
                tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tts.save(tts_file.name)

                st.audio(tts_file.name, format="audio/mp3")
            except Exception as e:
                st.error(f"❌ Speech generation failed: {e}")
