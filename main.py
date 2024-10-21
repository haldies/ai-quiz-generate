import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.sidebar.title("Quiz")
st.sidebar.file_uploader("Upload a file", type=["png", "jpg", "pdf"])
st.sidebar.text_input("Link")
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

def generate_quiz_with_groq(num_questions):
    prompt = (
        f"Generate {num_questions} multiple-choice questions about android studio knowledge."
        "Each question should have exactly 4 options labeled A, B, C, and D. "
        "Include the correct answer at the end of each question in the format 'Correct answer: [A/B/C/D]'. "
        "Make sure the questions are clear and concise."
    )
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    quiz_content = chat_completion.choices[0].message.content
    st.write("Output dari Groq:", quiz_content)
    questions = parse_groq_output(quiz_content)
    return questions

def parse_groq_output(quiz_content):
    questions = []
    lines = quiz_content.strip().split("\n")
    question = {}

    for line in lines:
        line = line.strip()
        if line.startswith("Question"):
            if question:
                questions.append(question)
            question = {'soal': line, 'options': [], 'correct_answer': ''}
        elif line.startswith(("A)", "B)", "C)", "D)")):
            question['options'].append(line)
        elif line.startswith("Correct answer:"):
            question['correct_answer'] = line.split(":")[-1].strip()

    if question:
        questions.append(question)

    return questions

st.title("Quiz generate Ai")


num_questions = st.number_input("Masukkan jumlah soal:", min_value=1, max_value=10, value=5)

if 'quiz' not in st.session_state:
    st.session_state['quiz'] = []

if 'user_answers' not in st.session_state:
    st.session_state['user_answers'] = [None] * num_questions

# Tombol untuk generate quiz
if st.button("Generate Quiz"):
    st.session_state['quiz'] = generate_quiz_with_groq(num_questions)
    st.write("Generated Quiz:", st.session_state['quiz'])  
    st.session_state['user_answers'] = [None] * num_questions  


if st.session_state['quiz']:
    for i, question in enumerate(st.session_state['quiz']):
        st.subheader(question['soal'])
      
        answer = st.radio(f"Pilih jawaban untuk soal {i + 1}:", question['options'], key=f"q{i}")
        st.session_state['user_answers'][i] = answer.split(".")[0].strip().upper()  
        

if st.button("Submit Jawaban"):
    score = 0
    for i, (question, user_answer) in enumerate(zip(st.session_state['quiz'], st.session_state['user_answers'])):
    
        correct_answer = question['correct_answer'].strip().upper()  
        
        
        if user_answer == correct_answer: 
            score += 1
            st.success(f"Soal {i + 1}: Benar!")
        else:
            st.error(f"Soal {i + 1}: Salah! Jawaban yang benar adalah {correct_answer}.")
        
        # st.write(f"Debug: Correct Answer = '{correct_answer}' | User Answer = '{user_answer}'")

  
    st.write(f"Skor kamu: {score}/{num_questions}")
