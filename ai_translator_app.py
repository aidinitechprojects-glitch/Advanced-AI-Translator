import streamlit as st
import openai
from gtts import gTTS
import tempfile
from streamlit_mic_recorder import mic_recorder

# Set your OpenAI API key (replace with your actual key or env variable)
openai.api_key = "YOUR_OPENAI_API_KEY"

# ----------------- Streamlit Page Config -----------------
st.set_page_config(page_title="AI Translator", page_icon="🌍", layout="wide")

st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    .title {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
        color: #ffffff;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .subtitle {
        font-size: 18px;
        text-align: center;
        margin-bottom: 40px;
        color: #f0f0f0;
    }
    .section-box {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #FFD700;
    }
    .output-text {
        font-size: 20px;
        font-weight: bold;
        color: #00FFCC;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------- Header -----------------
st.markdown('<div class="title">🌍 AI Translator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Speak in any language, translate instantly</div>', unsafe_allow_html=True)

# ----------------- Sidebar Controls -----------------
st.sidebar.header("🌐 Translation Settings")

input_lang = st.sidebar.selectbox(
    "🎤 Input Language",
    ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam", "French", "Spanish", "German", "Chinese", "Japanese"]
)

output_lang = st.sidebar.selectbox(
    "🔊 Target Language",
    ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam", "French", "Spanish", "German", "Chinese", "Japanese"]
)

# ----------------- Voice Input -----------------
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🎤 Speak Now</div>', unsafe_allow_html=True)

voice_input = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", just_once=True)

if voice_input:
    with open("temp.wav", "wb") as f:
        f.write(voice_input["bytes"])

    # Transcribe audio
    with open("temp.wav", "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )
    transcribed_text = transcript.text

    # ----------------- Display Transcription -----------------
    st.markdown('<div class="section-title">📝 Transcribed Text</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="output-text">{transcribed_text}</div>', unsafe_allow_html=True)

    # ----------------- Translation -----------------
    prompt = f"Translate the following {input_lang} text to {output_lang}, provide only the translated sentence without explanation:\n\n{transcribed_text}"
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    translated_text = response.choices[0].message.content.strip()

    # ----------------- Display Translation -----------------
    st.markdown('<div class="section-title">🌐 Translated Text</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="output-text">{translated_text}</div>', unsafe_allow_html=True)

    # ----------------- Phonetic Output -----------------
    phonetic_prompt = f"Provide only the phonetic transcription of this {output_lang} sentence:\n\n{translated_text}"
    phonetic_resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": phonetic_prompt}]
    )
    phonetic_text = phonetic_resp.choices[0].message.content.strip()

    st.markdown('<div class="section-title">🔤 Phonetic Text</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="output-text">{phonetic_text}</div>', unsafe_allow_html=True)

    # ----------------- Audio Output -----------------
    tts = gTTS(translated_text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tts.save(tmp_file.name)
        st.markdown('<div class="section-title">🔊 Output Audio</div>', unsafe_allow_html=True)
        st.audio(tmp_file.name, format="audio/mp3")

st.markdown('</div>', unsafe_allow_html=True)
