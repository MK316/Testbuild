import streamlit as st
import pandas as pd
import random

# ---------- Load data ----------
@st.cache_data
def load_data():
    # Change this to your file name / path
    df = pd.read_csv("https://raw.githubusercontent.com/MK316/Testbuild/refs/heads/main/pages/questions.csv")
    return df

df = load_data()

st.title("Interactive Quiz App")

# ---------- Choose chapter ----------
chapters = df["Chapter"].unique()
selected_chapter = st.sidebar.selectbox("Choose a chapter", chapters)

chapter_df = df[df["Chapter"] == selected_chapter].reset_index(drop=True)
total_questions = len(chapter_df)

# ---------- Initialize / reset session state when chapter changes ----------
if "current_chapter" not in st.session_state:
    st.session_state.current_chapter = selected_chapter

if (
    "order" not in st.session_state
    or st.session_state.current_chapter != selected_chapter
):
    st.session_state.current_chapter = selected_chapter

    # random order of questions (list of row indices)
    indices = list(range(total_questions))
    random.shuffle(indices)
    st.session_state.order = indices

    # position in the shuffled list
    st.session_state.q_index = 0

    # feedback text
    st.session_state.feedback = ""

    # score tracking
    st.session_state.score = 0
    # whether each question has already been answered correctly
    st.session_state.answered_correctly = {i: False for i in indices}

# ---------- Current question ----------
current_shuffled_idx = st.session_state.order[st.session_state.q_index]
st.session_state.current_question_idx = current_shuffled_idx  # for callbacks
q = chapter_df.iloc[current_shuffled_idx]

# Progress bar (position in quiz)
progress_ratio = (st.session_state.q_index + 1) / total_questions
st.progress(progress_ratio)
st.caption(f"Question {st.session_state.q_index + 1} / {total_questions}")

st.markdown("### " + q["Question"])

# ---------- Answer checking ----------
def check_answer(choice):
    idx = st.session_state.current_question_idx
    correct_letter = q["Answer"]  # should be "A", "B", "C", or "D"

    if choice == correct_letter:
        # Only add to score the first time this question is answered correctly
        if not st.session_state.answered_correctly[idx]:
            st.session_state.score += 1
            st.session_state.answered_correctly[idx] = True
        st.session_state.feedback = "✅ Correct!"
    else:
        st.session_state.feedback = "❌ Try again"

# Option buttons
st.button(q["OptionA"], on_click=check_answer, args=("A",))
st.button(q["OptionB"], on_click=check_answer, args=("B",))
st.button(q["OptionC"], on_click=check_answer, args=("C",))
st.button(q["OptionD"], on_click=check_answer, args=("D",))

# Feedback
st.markdown(st.session_state.feedback)

# ---------- Navigation ----------
col1, col2 = st.columns(2)

with col1:
    if st.button("Previous"):
        if st.session_state.q_index > 0:
            st.session_state.q_index -= 1
            st.session_state.feedback = ""

with col2:
    if st.button("Next"):
        if st.session_state.q_index < total_questions - 1:
            st.session_state.q_index += 1
            st.session_state.feedback = ""
        else:
            st.session_state.feedback = "🎉 You reached the end of this chapter!"

# ---------- Score display ----------
st.markdown(
    f"**Score:** {st.session_state.score} / {total_questions} "
    f"({st.session_state.score / total_questions * 100:.1f}%)"
)
