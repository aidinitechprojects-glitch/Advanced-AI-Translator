import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------------- Streamlit Page Config ----------------
st.set_page_config(page_title="🌍 AI Translator", page_icon="🤖", layout="centered")

# ---------------- Custom CSS for modern UI ----------------
st.markdown("""
<style>
body {
    background-color: #121212;
    color: #ECF0F1;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
h1 {
    font-weight: 800;
    font-size: 2.5rem;
    color: #FFFFFF;
    display: flex;
    align-items: center;
}
.output-box {
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    margin-bottom: 20px;
}
.stButton>button {
    background: linear-gradient(90deg, #FF8C00, #FF2D95);
    color: white;
    font-weight: bold;
    border-radius: 12px;
    height: 50px;
    width: 100%;
}
.stTextArea>div>textarea {
    background-color: #1E1E2F;
    color: #ECF0F1;
    font-size: 16px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Page Header with AI Logo ----------------
st.markdown("""
<h1 style="text-align:center;">
    🤖 AI Translator
</h1>
<p style="text-align:center; font-size:18px; color:#AAB2BD;">
Translate your text across languages with phonetics & audio playback
</p>
""", unsafe_allow_html=True)

# ---------------- OpenAI API Key ----------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ---------------- Supported Languages ----------------
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

# ---------------- Input Fields ----------------
text_input = st.text_area("Enter your text:", height=150)

col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox("Input Language:", list(lang_map.keys()), index=list(lang_map.keys()).index("English"))
with col2:
    target_lang = st.selectbox("Output Language:", list(lang_map.keys()), index=list(lang_map.keys()).index("Hindi"))

# ---------------- Translate Button ----------------
if st.button("Translate"):
    if text_input.strip() == "":
        st.warning("⚠️ Please enter some text.")
    else:
        with st.spinner("Translating..."):
            # Translation
            translate_prompt = f"Translate the following text from {source_lang} to {target_lang}. Only provide the translated sentence:\n{text_input}"
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": translate_prompt}]
            )
            translated_text = response.choices[0].message.content.strip()

            # Phonetic transcription
            phonetic_prompt = f"Provide only the phonetic (romanized) transcription of this {target_lang} text:\n{translated_text}"
            phonetic_resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": phonetic_prompt}]
            )
            phonetic_text = phonetic_resp.choices[0].message.content.strip()

        # ---------------- Display Outputs ----------------
        st.markdown(f"<div class='output-box' style='background: linear-gradient(135deg, #1E3C72, #2A5298);'>"
                    f"<b style='color:#FFD700; font-size:18px;'>🌐 Translated ({target_lang}):</b><br>"
                    f"<span style='color:#ECF0F1; font-size:20px;'>{translated_text}</span></div>",
                    unsafe_allow_html=True)

        st.markdown(f"<div class='output-box' style='background: linear-gradient(135deg, #6A11CB, #2575FC);'>"
                    f"<b style='color:#00CED1; font-size:18px;'>🔤 Phonetic:</b><br>"
                    f"<span style='color:#ECF0F1; font-size:18px;'>{phonetic_text}</span></div>",
                    unsafe_allow_html=True)

        # ---------------- Generate Audio ----------------
        try:
            tts_lang = lang_map.get(target_lang, "en")
            tts = gTTS(text=translated_text, lang=tts_lang)
            tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(tts_file.name)
            st.audio(tts_file.name, format="audio/mp3")
        except Exception as e:
            st.error(f"❌ Speech generation failed: {e}")
