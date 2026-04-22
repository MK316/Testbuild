import streamlit as st
import re
import io
import html
from gtts import gTTS

st.set_page_config(page_title="Sentence TTS Highlighter", layout="wide")

st.title("Sentence TTS Highlighter")
st.caption("Paste a passage, select a sentence, play its audio, and see where it appears in the full text.")

# ---------- Functions ----------
def split_into_sentences(text: str):
    text = text.strip()
    if not text:
        return []

    # Split by sentence-ending punctuation while keeping the punctuation
    parts = re.split(r'(?<=[.!?])\s+', text)
    sentences = [p.strip() for p in parts if p.strip()]
    return sentences

def make_label(idx: int, sentence: str, max_words: int = 5):
    words = sentence.split()
    preview = " ".join(words[:max_words])
    if len(words) > max_words:
        preview += " ..."
    return f"{idx + 1}. {preview}"

def highlight_selected_sentence(full_text: str, selected_sentence: str):
    escaped_full = html.escape(full_text)
    escaped_selected = html.escape(selected_sentence)

    highlighted = escaped_full.replace(
        escaped_selected,
        f"<mark style='background-color: #fff3a3; padding: 0.1em 0.2em; border-radius: 4px;'>{escaped_selected}</mark>",
        1
    )

    highlighted = highlighted.replace("\n", "<br>")
    return highlighted

def generate_tts_bytes(text: str, lang: str = "en", tld: str = "com"):
    audio_buffer = io.BytesIO()
    tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.getvalue()

# ---------- Input ----------
text_input = st.text_area(
    "Paste your text here:",
    height=220,
    placeholder="Paste a passage here. The app will split it into sentences."
)

col1, col2 = st.columns([2, 1])

with col2:
    language_option = st.selectbox(
        "TTS language",
        ["English (American)", "English (British)", "Korean", "French", "Spanish", "Japanese"]
    )

lang_settings = {
    "English (American)": ("en", "com"),
    "English (British)": ("en", "co.uk"),
    "Korean": ("ko", None),
    "French": ("fr", None),
    "Spanish": ("es", None),
    "Japanese": ("ja", None),
}

# ---------- Main ----------
if text_input.strip():
    sentences = split_into_sentences(text_input)

    if sentences:
        labels = [make_label(i, s) for i, s in enumerate(sentences)]
        label_to_sentence = dict(zip(labels, sentences))

        with col1:
            selected_label = st.selectbox(
                "Select a sentence:",
                labels
            )

        selected_sentence = label_to_sentence[selected_label]

        st.markdown("### Selected sentence")
        st.write(selected_sentence)

        lang_code, tld = lang_settings[language_option]

        try:
            if tld:
                audio_bytes = generate_tts_bytes(selected_sentence, lang=lang_code, tld=tld)
            else:
                audio_bytes = generate_tts_bytes(selected_sentence, lang=lang_code)

            st.audio(audio_bytes, format="audio/mp3")
        except Exception as e:
            st.error(f"Audio generation failed: {e}")

        st.markdown("### Full passage")
        highlighted_html = highlight_selected_sentence(text_input, selected_sentence)
        st.markdown(
            f"""
            <div style="
                border: 1px solid #ddd;
                padding: 16px;
                border-radius: 10px;
                line-height: 1.8;
                font-size: 1.05rem;
                background-color: #fafafa;">
                {highlighted_html}
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("Show sentence list"):
            for i, s in enumerate(sentences, start=1):
                st.write(f"{i}. {s}")

    else:
        st.warning("No sentences were detected. Please check the text.")
else:
    st.info("Paste a passage above to begin.")
