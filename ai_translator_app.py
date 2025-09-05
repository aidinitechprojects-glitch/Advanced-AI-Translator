import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------------- Page Config ----------------
st.set_page_config(page_title="🌍 AI Translator", page_icon="🤖", layout="centered")

# ---------------- Initialize Session State ----------------
if "source_lang" not in st.session_state:
    st.session_state.source_lang = "English"
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Hindi"
if "text_input" not in st.session_state:
    st.session_state.text_input = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "phonetic_text" not in st.session_state:
    st.session_state.phonetic_text = ""

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
/* General body */
body {background-color: #F5F5F5; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}

/* Header */
.app-header {text-align: center; font-size: 3rem; font-weight: 900; color: #FF6B00; margin-bottom: 5px;}
.subtitle {text-align: center; font-size: 1.4rem; font-weight: 500; color: #444444; margin-bottom: 25px;}

/* Input text area */
.stTextArea>div>textarea {
    background-color: #FFFFFF; color: #333333; font-size: 16px; border-radius: 12px; padding: 10px; max-height: 200px; overflow-y: auto;
    transition: all 0.3s ease;
}
.stTextArea>div>textarea:focus {
    border: 2px solid #FF6B00; background-color: #FFF7EE;
}

/* Buttons */
.stButton>button {font-weight: bold; border-radius: 12px; cursor:pointer; transition: all 0.3s ease;}
.translate-button {
    background: linear-gradient(90deg,#FF6B00,#FF3C00); color: #FFFFFF; width: 250px; height: 50px; font-size:18px; margin:auto; display:block;
}
.translate-button:hover {
    filter: brightness(1.2);
    box-shadow: 0 4px 15px rgba(255,107,0,0.6);
}
.swap-button {background: #00BFFF; color: #FFFFFF; font-size:16px; height:40px; width:40px;}
.clear-button {background: #555555; color: #FFFFFF; font-size:14px; height:35px; width:80px; float:right; margin-top:5px;}

/* Output Boxes */
.output-box {
    background: #FFFFFF; border-radius: 12px; padding: 15px; margin-bottom: 15px; transition: all 0.3s ease;
}
.output-box:hover {background-color: #FFF7EE;}
.output-heading {font-weight: 700; font-size: 16px; color: #FF6B00; margin-bottom: 5px;}
.output-text {font-size: 14px; color: #333333; max-height: 150px; overflow-y: auto;}

/* Audio Section */
.audio-title {font-weight: 700; font-size: 16px; margin-bottom: 10px; color: #FF6B00; text-align:center;}
</style>
""", unsafe_allow_html=True)

# ---------------- Header ----------------
st.markdown('<div class="app-header">🤖 AI Translator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Translate text across languages with phonetics & audio playback</div>', unsafe_allow_html=True)

# ---------------- OpenAI API Key ----------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ---------------- Languages ----------------
lang_map = {
    "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Kannada": "kn",
    "Malayalam": "ml", "Gujarati": "gu", "Marathi": "mr", "Punjabi": "pa",
    "Bengali": "bn", "Urdu": "ur", "Odia": "or",
    "English": "en", "French": "fr", "Spanish": "es", "German": "de",
    "Italian": "it", "Portuguese": "pt", "Russian": "ru", "Japanese": "ja",
    "Korean": "ko", "Chinese (Mandarin)": "zh-cn", "Arabic": "ar",
    "Turkish": "tr", "Dutch": "nl", "Greek": "el", "Polish": "pl",
    "Swedish": "sv",
}

# ---------------- Input Section ----------------
st.session_state.text_input = st.text_area("Enter your text:", value=st.session_state.text_input, height=150)

# ---------------- Clear Button (Bottom Right of Input) ----------------
if st.button("Clear", key="clear"):
    st.session_state.text_input = ""
    st.session_state.translated_text = ""
    st.session_state.phonetic_text = ""
    st.experimental_rerun()

# ---------------- Language Selection and Swap ----------------
col1, col2, col3 = st.columns([4,1,4])
with col1:
    st.session_state.source_lang = st.selectbox("Input Language:", list(lang_map.keys()), index=list(lang_map.keys()).index(st.session_state.source_lang))
with col2:
    if st.button("⇄", key="swap", help="Swap languages"):
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
with col3:
    st.session_state.target_lang = st.selectbox("Output Language:", list(lang_map.keys()), index=list(lang_map.keys()).index(st.session_state.target_lang))

# ---------------- Translate Button (Center, Pro UI) ----------------
translate_clicked = st.button("Translate", key="translate", help="Translate text", args=None)
if translate_clicked:
    if st.session_state.text_input.strip() == "":
        st.warning("⚠️ Please enter some text.")
    else:
        with st.spinner("Translating..."):
            # Translation
            translate_prompt = f"Translate the following text from {st.session_state.source_lang} to {st.session_state.target_lang}. Only provide the translated sentence:\n{st.session_state.text_input}"
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": translate_prompt}]
            )
            st.session_state.translated_text = response.choices[0].message.content.strip()

            # Phonetic
            phonetic_prompt = f"Provide only the phonetic (romanized) transcription of this {st.session_state.target_lang} text:\n{st.session_state.translated_text}"
            phonetic_resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": phonetic_prompt}]
            )
            st.session_state.phonetic_text = phonetic_resp.choices[0].message.content.strip()

# ---------------- Display Outputs ----------------
if st.session_state.translated_text:
    st.markdown(f'''
    <div class="output-box">
        <div class="output-heading">🌐 Translated ({st.session_state.target_lang})</div>
        <div class="output-text">{st.session_state.translated_text}</div>
    </div>
    ''', unsafe_allow_html=True)

if st.session_state.phonetic_text:
    st.markdown(f'''
    <div class="output-box">
        <div class="output-heading">🔤 Phonetic</div>
        <div class="output-text">{st.session_state.phonetic_text}</div>
    </div>
    ''', unsafe_allow_html=True)

# ---------------- Play Audio ----------------
if st.session_state.translated_text:
    st.markdown('<div class="audio-title">🔊 Play Translated Audio</div>', unsafe_allow_html=True)
    try:
        tts_lang = lang_map.get(st.session_state.target_lang, "en")
        tts = gTTS(text=st.session_state.translated_text, lang=tts_lang)
        tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tts_file.name)
        st.audio(tts_file.name, format="audio/mp3")
    except Exception as e:
        st.error(f"❌ Speech generation failed: {e}")
