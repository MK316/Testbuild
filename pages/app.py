import streamlit as st
import pandas as pd
import random
from datetime import datetime
from fpdf import FPDF  # pip install fpdf2

st.set_page_config(page_title="Quiz App", layout="centered")

# ---------- Load data ----------
@st.cache_data
def load_data():
    # use your raw csv link or path here
    url = "https://raw.githubusercontent.com/MK316/Testbuild/refs/heads/main/pages/questions.csv"   # or your GitHub raw link
    df = pd.read_csv(url)
    return df

df = load_data()

# ---------- SESSION STATE ----------
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "current_chapter" not in st.session_state:
    st.session_state.current_chapter = None

if "chapter_stats" not in st.session_state:
    # {chapter: {"start_time":..., "end_time":..., "score":..., "total_questions":..., "completed":bool}}
    st.session_state.chapter_stats = {}

# ---------- SIDEBAR ----------
st.sidebar.header("Settings")

# 1. user name
st.session_state.user_name = st.sidebar.text_input(
    "Your name",
    value=st.session_state.user_name,
    placeholder="Type your name",
)

# 2. choose chapter
chapters = df["Chapter"].unique()
selected_chapter = st.sidebar.selectbox("Choose a chapter", chapters)

chapter_df = df[df["Chapter"] == selected_chapter].reset_index(drop=True)
total_questions = len(chapter_df)

# register chapter in stats if not present
stats = st.session_state.chapter_stats
if selected_chapter not in stats:
    stats[selected_chapter] = {
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": None,
        "score": 0,
        "total_questions": total_questions,
        "completed": False,
    }

# ---------- INITIALIZE / RESET STATE WHEN CHAPTER CHANGES ----------
if (
    "order" not in st.session_state
    or st.session_state.current_chapter != selected_chapter
):
    st.session_state.current_chapter = selected_chapter

    indices = list(range(total_questions))
    random.shuffle(indices)
    st.session_state.order = indices

    st.session_state.q_index = 0
    st.session_state.feedback = ""
    st.session_state.score = 0

# ---------- MAIN TITLE ----------
st.title("Interactive Quiz App")

# ---------- CURRENT QUESTION ----------
current_idx = st.session_state.order[st.session_state.q_index]
q = chapter_df.iloc[current_idx]

progress_ratio = (st.session_state.q_index + 1) / total_questions
st.progress(progress_ratio)
st.caption(f"Question {st.session_state.q_index + 1} / {total_questions}")

st.markdown(f"### {q['Question']}")

# ---------- ANSWER CHECKING ----------
def check_answer(choice_letter: str):
    correct = str(q["Answer"]).strip()  # "A","B","C","D"
    if choice_letter == correct:
        if st.session_state.feedback != "✅ Correct!":
            st.session_state.score += 1
        st.session_state.feedback = "✅ Correct!"
    else:
        st.session_state.feedback = "❌ Try again"

# ---------- OPTION BUTTONS (equal width, gray boxes) ----------
st.button(
    q["OptionA"],
    key=f"optA_{selected_chapter}_{current_idx}",
    on_click=check_answer,
    args=("A",),
    use_container_width=True,
)
st.button(
    q["OptionB"],
    key=f"optB_{selected_chapter}_{current_idx}",
    on_click=check_answer,
    args=("B",),
    use_container_width=True,
)
st.button(
    q["OptionC"],
    key=f"optC_{selected_chapter}_{current_idx}",
    on_click=check_answer,
    args=("C",),
    use_container_width=True,
)
st.button(
    q["OptionD"],
    key=f"optD_{selected_chapter}_{current_idx}",
    on_click=check_answer,
    args=("D",),
    use_container_width=True,
)

st.markdown(st.session_state.feedback)

# ---------- NAVIGATION (no double-click) ----------
def go_prev():
    if st.session_state.q_index > 0:
        st.session_state.q_index -= 1
        st.session_state.feedback = ""

def go_next():
    if st.session_state.q_index < total_questions - 1:
        st.session_state.q_index += 1
        st.session_state.feedback = ""
    else:
        st.session_state.feedback = "🎉 You reached the end of this chapter!"
        # mark chapter as completed
        s = st.session_state.chapter_stats[selected_chapter]
        s["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s["score"] = st.session_state.score
        s["total_questions"] = total_questions
        s["completed"] = True

col1, col2 = st.columns(2)
with col1:
    st.button(
        "Previous",
