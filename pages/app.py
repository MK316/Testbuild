import streamlit as st
import pandas as pd
import random
from datetime import datetime
from fpdf import FPDF  # ensure fpdf2 is in requirements.txt

st.set_page_config(page_title="Quiz App", layout="centered")


# --------------------------
# Load CSV
# --------------------------
@st.cache_data
def load_data():
    # Change this to your own path or raw GitHub link
    df = pd.read_csv("https://raw.githubusercontent.com/MK316/Testbuild/refs/heads/main/pages/questions.csv")
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
    st.session_state.chapter_stats = {}   # store each chapter's stats

if "order" not in st.session_state:
    st.session_state.order = []

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "feedback" not in st.session_state:
    st.session_state.feedback = ""


# --------------------------
# Sidebar
# --------------------------
st.sidebar.header("Settings")

# Username field
st.session_state.user_name = st.sidebar.text_input(
    "Your name",
    value=st.session_state.user_name,
    placeholder="Type your name",
)

# Choose chapter
chapters = df["Chapter"].unique()
selected_chapter = st.sidebar.selectbox("Choose a chapter", chapters)

# Filter data for chapter
chapter_df = df[df["Chapter"] == selected_chapter].reset_index(drop=True)
total_questions = len(chapter_df)

# Create chapter stats if missing
if selected_chapter not in st.session_state.chapter_stats:
    st.session_state.chapter_stats[selected_chapter] = {
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": None,
        "score": 0,
        "total_questions": total_questions,
        "completed": False,
    }

stats = st.session_state.chapter_stats[selected_chapter]


# --------------------------
# Reset state if chapter changed
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
# Main Title
# --------------------------
st.title("Interactive Quiz App")

# Current question
current_idx = st.session_state.order[st.session_state.q_index]
q = chapter_df.iloc[current_idx]


# --------------------------
# Progress bar
# --------------------------
progress_ratio = (st.session_state.q_index + 1) / total_questions
st.progress(progress_ratio)
st.caption(f"Question {st.session_state.q_index + 1} / {total_questions}")

st.markdown(f"### {q['Question']}")


# --------------------------
# Answer checking
# --------------------------
def check_answer(choice_letter):
    correct_letter = str(q["Answer"]).strip()

    if choice_letter == correct_letter:
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
    use_container_width=True
)

st.button(
    q["OptionB"],
    key=f"B_{selected_chapter}_{current_idx}",
    on_click=check_answer,
    args=("B",),
    use_container_width=True
)

st.button(
    q["OptionC"],
    key=f"C_{selected_chapter}_{current_idx}",
    on_click=check_answer,
    args=("C",),
    use_container_width=True
)

st.button(
    q["OptionD"],
    key=f"D_{selected_chapter}_{current_idx}",
    on_click=check_answer,
    args=("D",),
    use_container_width=True
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
        stats["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stats["score"] = st.session_state.score
        stats["completed"] = True


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
        use_container_width=True
    )

with col2:
    st.button(
        "Next",
        key="next_btn",
        on_click=go_next,
        type="primary",
        use_container_width=True
    )


# --------------------------
# Score display
# --------------------------
st.markdown(
    f"**Score:** {st.session_state.score} / {total_questions} "
    f"({st.session_state.score / total_questions * 100:.1f}%)"
)


# --------------------------
# PDF generation
# --------------------------
def generate_pdf():
    if not st.session_state.user_name:
        return None

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Quiz Practice Report", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Name: {st.session_state.user_name}", ln=True)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(4)

    for chap, info in st.session_state.chapter_stats.items():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Chapter: {chap}", ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 6, f"Completed: {'Yes' if info['completed'] else 'No'}", ln=True)
        pdf.cell(0, 6, f"Score: {info['score']} / {info['total_questions']}", ln=True)
        pdf.cell(0, 6, f"Start: {info['start_time']}", ln=True)
        pdf.cell(0, 6, f"End: {info['end_time']}", ln=True)
        pdf.ln(4)

    return pdf.output(dest="S").encode("latin-1")


# Sidebar PDF section
st.sidebar.markdown("---")
st.sidebar.subheader("PDF Report")

if st.session_state.user_name:
    pdf_bytes = generate_pdf()
    if pdf_bytes:
        st.sidebar.download_button(
            "Download Report PDF",
            data=pdf_bytes,
            file_name=f"{st.session_state.user_name}_quiz_report.pdf",
            mime="application/pdf"
        )
else:
    st.sidebar.info("Enter your name above to enable PDF download.")
