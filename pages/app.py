import streamlit as st
import pandas as pd
import random
from datetime import datetime
from fpdf import FPDF  # make sure `fpdf2` is in requirements.txt

st.set_page_config(page_title="Quiz App", layout="centered")

# --------------------------
# Load CSV
# --------------------------
@st.cache_data
def load_data():
    # If your CSV is in pages/questions.csv
    df = pd.read_csv("https://raw.githubusercontent.com/MK316/Testbuild/refs/heads/main/pages/questions.csv")
    # If you instead use a GitHub raw link, replace line above with:
    # df = pd.read_csv("https://raw.githubusercontent.com/USER/REPO/BRANCH/questions.csv")
    return df

df = load_data()

# --------------------------
# Initialize session state
# --------------------------
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "current_chapter" not in st.session_state:
    st.session_state.current_chapter = None

if "chapter_stats" not in st.session_state:
    # chapter_stats = {
    #   chapter: {
    #       "start_time": str,
    #       "end_time": str,
    #       "score": int,
    #       "total_questions": int,
    #       "completed": bool
    #   }
    # }
    st.session_state.chapter_stats = {}

if "order" not in st.session_state:
    st.session_state.order = []

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "feedback" not in st.session_state:
    st.session_state.feedback = ""

if "score" not in st.session_state:
    st.session_state.score = 0

# --------------------------
# Sidebar – user & chapter
# --------------------------
st.sidebar.header("Settings")

# 1. User name
st.session_state.user_name = st.sidebar.text_input(
    "Your name",
    value=st.session_state.user_name,
    placeholder="Type your name",
)

# 2. Chapter selection
chapters = df["Chapter"].unique()
selected_chapter = st.sidebar.selectbox("Choose a chapter", chapters)

# Filter data for selected chapter
chapter_df = df[df["Chapter"] == selected_chapter].reset_index(drop=True)
total_questions = len(chapter_df)

# Register stats for this chapter if first time
if selected_chapter not in st.session_state.chapter_stats:
    st.session_state.chapter_stats[selected_chapter] = {
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": "",
        "score": 0,
        "total_questions": total_questions,
        "completed": False,
    }

chapter_info = st.session_state.chapter_stats[selected_chapter]

# --------------------------
# Reset question state when chapter changes
# --------------------------
if st.session_state.current_chapter != selected_chapter:
    st.session_state.current_chapter = selected_chapter

    indices = list(range(total_questions))
    random.shuffle(indices)
    st.session_state.order = indices

    st.session_state.q_index = 0
    st.session_state.feedback = ""
    st.session_state.score = 0

# --------------------------
# Main title & question
# --------------------------
st.title("🍰 Phonetics Chapter Quiz App")

if total_questions == 0:
    st.warning("No questions found for this chapter.")
else:
    current_idx = st.session_state.order[st.session_state.q_index]
    q = chapter_df.iloc[current_idx]

    # Progress bar
    progress_ratio = (st.session_state.q_index + 1) / total_questions
    st.progress(progress_ratio)
    st.caption(f"Question {st.session_state.q_index + 1} / {total_questions}")

    st.markdown(f"### {q['Question']}")

    # --------------------------
    # Answer checking
    # --------------------------
    def check_answer(choice_letter: str):
        correct_letter = str(q["Answer"]).strip()
        if choice_letter == correct_letter:
            # Simple score logic: count how many times the user eventually got items correct
            # (If you want per-question uniqueness, we can add a dict later.)
            if st.session_state.feedback != "✅ Correct!":
                st.session_state.score += 1
            st.session_state.feedback = "✅ Correct!"
        else:
            st.session_state.feedback = "❌ Try again"

    # --------------------------
    # Option buttons (equal width)
    # --------------------------
    st.button(
        q["OptionA"],
        key=f"A_{selected_chapter}_{current_idx}",
        on_click=check_answer,
        args=("A",),
        use_container_width=True,
    )

    st.button(
        q["OptionB"],
        key=f"B_{selected_chapter}_{current_idx}",
        on_click=check_answer,
        args=("B",),
        use_container_width=True,
    )

    st.button(
        q["OptionC"],
        key=f"C_{selected_chapter}_{current_idx}",
        on_click=check_answer,
        args=("C",),
        use_container_width=True,
    )

    st.button(
        q["OptionD"],
        key=f"D_{selected_chapter}_{current_idx}",
        on_click=check_answer,
        args=("D",),
        use_container_width=True,
    )

    st.markdown(st.session_state.feedback)

    # --------------------------
    # Navigation functions
    # --------------------------
    def go_prev():
        if st.session_state.q_index > 0:
            st.session_state.q_index -= 1
            st.session_state.feedback = ""

    def go_next():
        if st.session_state.q_index < total_questions - 1:
            st.session_state.q_index += 1
            st.session_state.feedback = ""
        else:
            st.session_state.feedback = "🎉 You completed this chapter!"
            # Mark chapter completion
            chapter_info["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            chapter_info["score"] = st.session_state.score
            chapter_info["total_questions"] = total_questions
            chapter_info["completed"] = True

    # --------------------------
    # Navigation buttons (blue)
    # --------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.button(
            "Previous",
            key="prev_btn",
            on_click=go_prev,
            type="primary",
            use_container_width=True,
        )

    with col2:
        st.button(
            "Next",
            key="next_btn",
            on_click=go_next,
            type="primary",
            use_container_width=True,
        )

    # --------------------------
    # Score display
    # --------------------------
    if total_questions > 0:
        percentage = st.session_state.score / total_questions * 100
    else:
        percentage = 0.0

    st.markdown(
        f"**Score:** {st.session_state.score} / {total_questions} "
        f"({percentage:.1f}%)"
    )

# --------------------------
# PDF generation
# --------------------------
def generate_pdf_bytes():
    """Return PDF as bytes for download_button."""
    if not st.session_state.user_name:
        return None

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Quiz Practice Report", ln=True)

    # User info
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Name: {st.session_state.user_name}", ln=True)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(4)

    # Chapter info
    for chap, info in st.session_state.chapter_stats.items():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Chapter: {chap}", ln=True)

        pdf.set_font("Arial", "", 11)
        completed = "Yes" if info.get("completed") else "No"
        score = info.get("score", 0)
        total = info.get("total_questions", 0)
        start = info.get("start_time") or "N/A"
        end = info.get("end_time") or "N/A"

        pdf.cell(0, 6, f"Completed: {completed}", ln=True)
        pdf.cell(0, 6, f"Score: {score} / {total}", ln=True)
        pdf.cell(0, 6, f"Start: {start}", ln=True)
        pdf.cell(0, 6, f"End: {end}", ln=True)
        pdf.ln(4)

    # Get raw output from FPDF
    out = pdf.output(dest="S")

    # fpdf2 usually returns bytes; older versions may return str.
    if isinstance(out, bytes):
        pdf_bytes = out
    elif isinstance(out, bytearray):
        pdf_bytes = bytes(out)
    else:
        # Assume str; encode to bytes
        pdf_bytes = str(out).encode("latin-1", errors="ignore")

    return pdf_bytes

# --------------------------
# Sidebar – PDF download
# --------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("PDF Report")

if st.session_state.user_name:
    pdf_bytes = generate_pdf_bytes()
    if pdf_bytes is not None:
        st.sidebar.download_button(
            "Download Report PDF",
            data=pdf_bytes,  # guaranteed bytes
            file_name=f"{st.session_state.user_name}_quiz_report.pdf",
            mime="application/pdf",
        )
else:
    st.sidebar.info("Enter your name above to enable PDF download.")
