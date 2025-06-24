import streamlit as st
import pandas as pd
import random

CSV_PATH = "questions.csv"
QUESTIONS_PER_SESSION = 36
SEED = 42

# ---------- Load data ----------
@st.cache_data
def load_df(path):
    return pd.read_csv(path)

df = load_df(CSV_PATH)
n_rows = len(df)

# ---------- Init session ----------
if "history" not in st.session_state:
    st.session_state.history = []          # stores dicts per answered question
    st.session_state.used   = set()        # indices already shown
    random.seed(SEED)

# ---------- Game finished? ----------
if len(st.session_state.history) >= QUESTIONS_PER_SESSION:
    score = sum(h["is_correct"] for h in st.session_state.history)
    st.title("🏁 Game over!")
    st.write(f"**{score}/{QUESTIONS_PER_SESSION} correct** "
             f"({100*score/QUESTIONS_PER_SESSION:.1f}%).")

    with st.expander("Review your answers"):
        recap = pd.DataFrame(st.session_state.history).drop(columns="is_correct")
        st.dataframe(recap, use_container_width=True)

    if st.button("Play again"):
        st.session_state.history.clear()
        st.session_state.used.clear()
        st.rerun()

    st.stop()

# ---------- Select an unused question ----------
if len(st.session_state.used) == n_rows:
    # We've shown everything; reshuffle and continue
    st.session_state.used.clear()

while True:
    idx = random.randrange(n_rows)
    if idx not in st.session_state.used:
        st.session_state.used.add(idx)
        break

row = df.iloc[idx]

# ---------- Display ----------
st.title("Human vs AI – Guess the Source!")
st.write(f"### Concept: **{row.concept}** Level: **{int(row.difficulty)}**")
st.markdown(f"**Problem:**\n{row.question}")

choice = st.radio(
    "Is this problem AI-generated?",
    ("Yes", "No"),
    key=f"choice_{len(st.session_state.history)}"
)

if st.button("Submit answer"):
    user_ai = 1 if choice == "Yes" else 0
    st.session_state.history.append({
        "concept":    row.concept,
        "difficulty": int(row.difficulty),
        "question":   row.question,
        "answer":     row.answer,
        "your_guess": choice,
        "truth":      "Yes" if row.is_generated_by_ai else "No",
        "is_correct": user_ai == row.is_generated_by_ai
    })
    st.rerun()
