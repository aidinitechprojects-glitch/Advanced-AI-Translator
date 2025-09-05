import streamlit as st
from gtts import gTTS
import openai
import tempfile

# ---------- Page Config ----------
st.set_page_config(page_title="AI Translator Pro", page_icon="🌐", layout="centered")

# ---------- Session State ----------
for key in ["source_lang","target_lang","text_input","translated_text","phonetic_text","copy_feedback_translation","copy_feedback_phonetic"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# ---------- Header ----------
st.markdown("## AI Translator Pro 🌐")
st.markdown("Translate across languages with phonetics & audio playback.")

# ---------- Language Selection ----------
lang_map = {"English":"en","Hindi":"hi"}
col1,col_swap,col3 = st.columns([3.7,0.5,3.7])
with col1:
    st.session_state.source_lang = st.selectbox("From", list(lang_map.keys()), index=list(lang_map.keys()).index(st.session_state.source_lang))
with col_swap:
    if st.button("⇆"):
        st.session_state.source_lang, st.session_state.target_lang = st.session_state.target_lang, st.session_state.source_lang
        st.experimental_rerun()
with col3:
    st.session_state.target_lang = st.selectbox("To", list(lang_map.keys()), index=list(lang_map.keys()).index(st.session_state.target_lang))

# ---------- Text Input ----------
st.session_state.text_input = st.text_area("Text to translate", value=st.session_state.text_input, height=100)

# ---------- Action Buttons ----------
clear_col, translate_col = st.columns([1,5])
with clear_col:
    if st.button("Clear"):
        for key in ["text_input","translated_text","phonetic_text"]:
            st.session_state[key] = ""
        st.experimental_rerun()
with translate_col:
    translate_clicked = st.button("Translate")

# ---------- Translation Logic ----------
openai.api_key = st.secrets["OPENAI_API_KEY"]
if translate_clicked and st.session_state.text_input.strip():
    with st.spinner("Translating…"):
        # Translation
        translate_prompt = f"Translate this text from {st.session_state.source_lang} to {st.session_state.target_lang}. ONLY raw output:\n{st.session_state.text_input}"
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":translate_prompt}]
        )
        st.session_state.translated_text = response.choices[0].message.content.strip()

        # Phonetic
        phonetic_prompt = f"Provide phonetic (romanized) transcription of this {st.session_state.target_lang} text. ONLY raw output:\n{st.session_state.translated_text}"
        phonetic_resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":phonetic_prompt}]
        )
        st.session_state.phonetic_text = phonetic_resp.choices[0].message.content.strip()

# ---------- Output Box with Copy ----------
def output_box(title, text, feedback_key):
    if text:
        st.markdown(f"**{title}**")
        st.text_area("", value=text, height=80, key=f"{feedback_key}_textarea")
        col1,col2 = st.columns([4,1])
        with col2:
            if st.button("Copy", key=f"{feedback_key}_btn"):
                st.session_state[feedback_key] = text
        if st.session_state[feedback_key]:
            st.success("Copied!")

output_box("🌐 Translation", st.session_state.translated_text, "copy_feedback_translation")
output_box("🔤 Phonetic", st.session_state.phonetic_text, "copy_feedback_phonetic")

# ---------- Audio ----------
if st.session_state.translated_text:
    st.markdown("🔊 Audio Playback")
    try:
        tts_lang = lang_map.get(st.session_state.target_lang,"en")
        tts = gTTS(text=st.session_state.translated_text,lang=tts_lang)
        tts_file = tempfile.NamedTemporaryFile(delete=False,suffix=".mp3")
        tts.save(tts_file.name)
        st.audio(tts_file.name,format="audio/mp3")
    except Exception as e:
        st.error(f"❌ Speech generation failed: {e}")
