import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Quiz App", layout="centered")

# ---------- Load data ----------
@st.cache_data
def load_data():
    # use your raw csv link or path here
    url = "https://raw.githubusercontent.com/MK316/Testbuild/refs/heads/main/pages/questions.csv"
    df = pd.read_csv(url)
    return df

df = load_data()

st.title("Interactive Quiz App")

# ---------- Choose chapter ----------
chapters = df["Chapter"].unique()
selected_chapter = st.sidebar.selectbox("Choose a chapter", chapters)

chapter_df = df[df["Chapter"] == selected_chapter].reset_index(drop=True)
total_questions = len(chapter_df)

# ---------- Init / reset state when chapter changes ----------
if "current_chapter" not in st.session_state:
    st.session_state.current_chapter = None

if st.session_state.current_chapter != selected_chapter:
    st.session_state.current_chapter = selected_chapter

    indices = list(range(total_questions))
    random.shuffle(indices)
    st.session_state.order = indices

    st.session_state.q_index = 0
    st.session_state.feedback = ""
    st.session_state.score = 0
    st.session_state.answered_correctly = {i: False for i in indices}

# ---------- Current question ----------
current_idx = st.session_state.order[st.session_state.q_index]
q = chapter_df.iloc[current_idx]

progress_ratio = (st.session_state.q_index + 1) / total_questions
st.progress(progress_ratio)
st.caption(f"Question {st.session_state.q_index + 1} / {total_questions}")

st.markdown(f"### {q['Question']}")

# ---------- Answer checking ----------
def check_answer(choice_letter: str):
    correct = str(q["Answer"]).strip()  # "A" / "B" / "C" / "D"
    if choice_letter == correct:
        if not st.session_state.answered_correctly[current_idx]:
            st.session_state.score += 1
            st.session_state.answered_correctly[current_idx] = True
        st.session_state.feedback = "✅ Correct!"
    else:
        st.session_state.feedback = "❌ Try again"

# ---------- Option buttons ----------
# use_container_width=True → all same width
st.button(
    q["OptionA"],
    key=f"optA_{current_idx}",
    on_click=check_answer,
    args=("A",),
    use_container_width=True,
)

st.button(
    q["OptionB"],
    key=f"optB_{current_idx}",
    on_click=check_answer,
    args=("B",),
    use_container_width=True,
)

st.button(
    q["OptionC"],
    key=f"optC_{current_idx}",
    on_click=check_answer,
    args=("C",),
    use_container_width=True,
)

st.button(
    q["OptionD"],
    key=f"optD_{current_idx}",
    on_click=check_answer,
    args=("D",),
    use_container_width=True,
)

# default Streamlit button style already gives gray boxes for these

st.markdown(st.session_state.feedback)

# ---------- Navigation handlers (fix double-click issue) ----------
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

col1, col2 = st.columns(2)
with col1:
    st.button(
        "Previous",
        key="prev_btn",
        on_click=go_prev,
        type="primary",            # blue button
        use_container_width=True,
    )

with col2:
    st.button(
        "Next",
        key="next_btn",
        on_click=go_next,
        type="primary",            # blue button
        use_container_width=True,
    )

# ---------- Score ----------
st.markdown(
    f"**Score:** {st.session_state.score} / {total_questions} "
    f"({st.session_state.score / total_questions * 100:.1f}%)"
)
