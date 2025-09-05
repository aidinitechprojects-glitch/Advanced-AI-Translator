import streamlit as st
from gtts import gTTS
import openai
import tempfile
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase, RTCConfiguration
import av

# Page config
st.set_page_config(page_title="🎤 AI Voice Translator", page_icon="🌍", layout="centered")

st.title("🌍 AI Voice Translator")

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

# WebRTC config
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.frames.append(frame.to_ndarray().tobytes())
        return frame

st.markdown("### 🎙️ Record your voice")
webrtc_ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"audio": True, "video": False},
)

if webrtc_ctx.audio_processor:
    if st.button("🔴 Stop & Transcribe"):
        # Save audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            for chunk in webrtc_ctx.audio_processor.frames:
                f.write(chunk)
            audio_path = f.name

        # Step 1: Transcribe
        with st.spinner("🎧 Transcribing..."):
            with open(audio_path, "rb") as audio_file:
                transcript = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            transcribed_text = transcript.text
            st.success("✅ Transcribed Text:")
            st.markdown(f"<div style='color:#2C3E50;font-size:18px;font-weight:600'>{transcribed_text}</div>", unsafe_allow_html=True)

        # Step 2: Translate
        with st.spinner("🌍 Translating..."):
            translate_prompt = f"Translate from {source_lang} to {target_lang}. Only return the translated text:\n\n{transcribed_text}"
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": translate_prompt}]
            )
            translated_text = response.choices[0].message.content.strip()
            st.markdown(f"### 📝 Translated Text:\n<div style='color:#1A5276;font-size:22px;font-weight:900'>{translated_text}</div>", unsafe_allow_html=True)

        # Step 3: Phonetic
        phonetic_prompt = f"Provide the phonetic (romanized) transcription of this {target_lang} text: {translated_text}"
        phonetic_resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": phonetic_prompt}]
        )
        phonetic_text = phonetic_resp.choices[0].message.content.strip()
        st.markdown(f"### 🔤 Phonetic:\n<div style='color:#7D3C98;font-size:20px;font-weight:bold'>{phonetic_text}</div>", unsafe_allow_html=True)

        # Step 4: Audio Output
        try:
            tts_lang = lang_map.get(target_lang, "en")
            tts = gTTS(text=translated_text, lang=tts_lang)
            tts.save("output.mp3")
            st.audio("output.mp3", format="audio/mp3")
        except Exception as e:
            st.error(f"❌ Speech generation failed: {e}")
