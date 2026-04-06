import streamlit as st
import google.generativeai as genai
import json
import time

# --- CONFIGURATION ---
# Replace 'YOUR_API_KEY' with your actual Gemini API Key
genai.configure(api_key="AIzaSyCh1gJhW2I3pD8orXXKbWHGconB09-mbc4")
# Option A: Fastest and Free (Best for Quizzes)
model = genai.GenerativeModel('gemini-3-flash-preview')


# Initialize Session States
if 'page' not in st.session_state:
    st.session_state.page = "SETUP"
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0
if 'score' not in st.session_state:
    st.session_state.score = 0


# --- FUNCTIONS ---
def generate_quiz(topic, count, difficulty, options_count):
    prompt = f"""
    Generate a quiz about {topic}. 
    Difficulty: {difficulty}. 
    Number of questions: {count}. 
    Each question must have {options_count} options.
    Return ONLY a JSON list of objects. Each object must have keys:
    "question" (string), "options" (list of strings), "answer" (string matching one of the options).
    """
    response = model.generate_content(prompt)
    # Clean response text to ensure it's valid JSON
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)


# --- PAGE 1: SETUP ---
if st.session_state.page == "SETUP":
    st.title("🧠 AI Quiz Generator")
    st.write("Configure your quiz below:")

    with st.form("quiz_form"):
        topic = st.text_input("Enter Topic", "Space Exploration")
        count = st.slider("Number of Questions", 1, 10, 5)
        diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        opt_count = st.number_input("Options per Question", 2, 5, 4)
        timer_val = st.number_input("Seconds per Question", 5, 60, 15)

        submitted = st.form_submit_button("Start Quiz")

        if submitted:
            with st.spinner("Generating questions..."):
                try:
                    st.session_state.questions = generate_quiz(topic, count, diff, opt_count)
                    st.session_state.time_limit = timer_val
                    st.session_state.page = "QUIZ"
                    st.session_state.current_idx = 0
                    st.session_state.score = 0
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating quiz: {e}")

# --- PAGE 2: QUIZ ---
elif st.session_state.page == "QUIZ":
    q_list = st.session_state.questions
    idx = st.session_state.current_idx

    if idx < len(q_list):
        st.subheader(f"Question {idx + 1} of {len(q_list)}")
        curr_q = q_list[idx]

        # Timer logic
        timer_placeholder = st.empty()

        # Display Question
        st.write(f"### {curr_q['question']}")

        # User selection
        answer = st.radio("Choose one:", curr_q['options'], key=f"q_{idx}")

        if st.button("Submit Answer"):
            if answer == curr_q['answer']:
                st.session_state.score += 1
            st.session_state.current_idx += 1
            st.rerun()

    else:
        st.session_state.page = "RESULT"
        st.rerun()

# --- PAGE 3: RESULT ---
elif st.session_state.page == "RESULT":
    st.title("🏁 Quiz Finished!")
    total = len(st.session_state.questions)
    score = st.session_state.score

    st.metric("Final Score", f"{score} / {total}")

    percent = (score / total) * 100
    if percent >= 70:
        st.success(f"Great job! You got {percent}%")
        st.balloons()
    else:
        st.warning(f"Keep practicing! You got {percent}%")

    if st.button("Restart"):
        st.session_state.page = "SETUP"
        st.rerun()