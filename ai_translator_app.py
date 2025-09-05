# ---------- Output ----------
if st.session_state.translated_text:
    # Translation Box with Copy
    col = st.columns([1, 8, 1])
    with col[1]:
        st.markdown(f"""
        <div class="output-card">
            <div class="output-title">🌐 Translation</div>
            {st.session_state.translated_text}
        </div>
        """, unsafe_allow_html=True)
        if st.button("Copy Translation", key="copy_translation"):
            st.experimental_set_query_params()  # Clears URL query params
            st.clipboard_set(st.session_state.translated_text)
            st.toast("✅ Translation copied to clipboard!")

if st.session_state.phonetic_text:
    col = st.columns([1, 8, 1])
    with col[1]:
        st.markdown(f"""
        <div class="output-card">
            <div class="output-title">🔤 Phonetic</div>
            {st.session_state.phonetic_text}
        </div>
        """, unsafe_allow_html=True)
        if st.button("Copy Phonetic", key="copy_phonetic"):
            st.experimental_set_query_params()
            st.clipboard_set(st.session_state.phonetic_text)
            st.toast("✅ Phonetic copied to clipboard!")

# ---------- Audio ----------
if st.session_state.translated_text:
    st.markdown('<div class="audio-title">🔊 Audio Playback</div>', unsafe_allow_html=True)
    try:
        tts_lang = lang_map.get(st.session_state.target_lang, "en")
        tts = gTTS(text=st.session_state.translated_text, lang=tts_lang)
        tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tts_file.name)
        st.audio(tts_file.name, format="audio/mp3")
    except Exception as e:
        st.error(f"❌ Speech generation failed: {e}")
