import streamlit as st
import openai
from gtts import gTTS
import tempfile
import base64
import io
from pydub import AudioSegment

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

# --- Mic Recorder (JS frontend) ---
st.markdown("### 🎙️ Record your voice")

# Inject custom mic recorder
st.markdown(
    """
    <script>
    let recorder, gumStream;
    let chunks = [];
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    
    async function record() {
        gumStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        recorder = new MediaRecorder(gumStream);
        chunks = [];
        recorder.ondataavailable = e => chunks.push(e.data);
        recorder.start();
        window.streamlitAudioRec = "recording";
    }

    async function stop() {
        recorder.stop();
        await sleep(200);
        let blob = new Blob(chunks, { type: 'audio/wav' });
        let reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = () => {
            let base64data = reader.result.split(',')[1];
            const streamlitEvent = new Event("streamlit_audio_recorder");
            streamlitEvent.data = base64data;
            document.dispatchEvent(streamlitEvent);
        };
        window.streamlitAudioRec = "stopped";
    }
    </script>

    <style>
    .mic-btn {
        background: linear-gradient(90deg, #2563eb, #06b6d4);
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 16px;
        border-radius: 50px;
        cursor: pointer;
        font-weight: bold;
    }
    </style>

    <button class="mic-btn" onclick="record()">🎤 Start Recording</button>
    <button class="mic-btn" onclick="stop()">🛑 Stop Recording</button>
    """,
    unsafe_allow_html=True,
)

# Capture base64 audio from JS
def get_audio_data():
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    ctx = get_script_run_ctx()
    if ctx is None:
        return None
    import streamlit as st2
    return st2.session_state.get("audio_data")

# JS → Streamlit listener
if "audio_data" not in st.session_state:
    st.session_state["audio_data"] = None

def audio_listener():
    import streamlit.components.v1 as components
    components.html(
        """
        <script>
        document.addEventListener("streamlit_audio_recorder", (e) => {
            const base64data = e.data;
            fetch("/_stcore/stream", {
                method: "POST",
                body: JSON.stringify({ "audio_data": base64data }),
                headers: { "Content-Type": "application/json" }
            });
        });
        </script>
        """,
        height=0,
    )

audio_listener()

# Processing audio if captured
if st.session_state.get("audio_data"):
    with st.spinner("🎧 Processing your voice..."):
        # Decode base64 to wav
        audio_bytes = base64.b64decode(st.session_state["audio_data"])
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            audio.export(tmpfile.name, format="wav")
            audio_path = tmpfile.name

        # Step 1: Transcribe
        with open(audio_path, "rb") as f:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        transcribed_text = transcript.text
        st.success("✅ Transcribed Text:")
        st.markdown(f"<div style='color:#2C3E50;font-size:18px;font-weight:600'>{transcribed_text}</div>", unsafe_allow_html=True)

        # Step 2: Translate
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

        # Step 4: Output audio
        try:
            tts_lang = lang_map.get(target_lang, "en")
            tts = gTTS(text=translated_text, lang=tts_lang)
            tts.save("output.mp3")
            st.audio("output.mp3", format="audio/mp3")
        except Exception as e:
            st.error(f"❌ Speech generation failed: {e}")
