import streamlit as st

# UI configuration settings
st.set_page_config(page_title="Medical Symptom Checker", layout="centered")

# Custom CSS for a high-end, attractive UI
st.markdown("""
    <style>
        /* Page title styling */
        .title {
            font-size: 3em;
            font-weight: bold;
            color: #2E8B57;
            text-align: center;
            margin-bottom: 0.2em;
        }
        
        /* Subtitle styling */
        .subtitle {
            font-size: 1.2em;
            color: #4F4F4F;
            text-align: center;
            margin-top: 0;
            margin-bottom: 2em;
        }

        /* Question box styling */
        .question-box {
            padding: 20px;
            border-radius: 8px;
            background-color: #f5f5f5;
            color: #333;
            font-size: 1.2em;
            font-weight: 500;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        
        /* Styling the input box */
        .stTextInput > div > input {
            border: 2px solid #2E8B57;
            padding: 10px;
            border-radius: 8px;
            font-size: 1.1em;
            background-color: #FFF;
            transition: all 0.3s ease;
        }
        
        /* Button styling */
        .stButton button {
            background-color: #2E8B57;
            color: #FFF;
            font-size: 1.1em;
            font-weight: bold;
            padding: 0.6em 2em;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.1s ease;
        }
        
        /* Hover effect for buttons */
        .stButton button:hover {
            background-color: #1E6A43;
            transform: scale(1.05);
        }
        
        /* Centering the button container */
        .button-container {
            display: flex;
            justify-content: space-around;
            margin-top: 2em;
        }
        
        /* Success message styling */
        .stAlert {
            background-color: #D4EDDA;
            color: #155724;
            font-size: 1.2em;
            border-radius: 8px;
            padding: 1em;
            text-align: center;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Check if success message should be displayed
if "show_success" in st.session_state and st.session_state.show_success:
    st.success("Primary symptom saved to primary_symptom.txt and other symptoms saved to other_symptoms.txt")
    # Reset the flag after displaying the message
    st.session_state.show_success = False

# Title and description
st.markdown('<p class="title">Comprehensive Medical Symptom Checker</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Answer the questions about your health and medical history to help us understand your symptoms better.</p>', unsafe_allow_html=True)

# Questions for a broad range of diseases and medical history
questions = [
    "What is your primary symptom or reason for the visit?",
    "How long have you been experiencing these symptoms?",
    "Do you have a history of chronic conditions (e.g., diabetes, hypertension)?",
    "Have you undergone any surgeries or medical procedures in the past?",
    "Are you currently taking any medications or supplements?",
    "Have you recently experienced any loss of appetite, nausea, or vomiting?",
    "Do you have a fever or have you recently experienced any sudden weight loss?",
    "Are you experiencing any pain? If yes, please describe its location and severity.",
    "Do you have a family history of any specific diseases?",
    "Are there any other symptoms or information you'd like to share?"
]

# Initialize session state for question navigation and responses
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "responses" not in st.session_state:
    st.session_state.responses = [""] * len(questions)  # Empty responses for each question

# Display current question based on index and its response field
current_question_text = questions[st.session_state.current_question]
st.markdown(f'<div class="question-box">{current_question_text}</div>', unsafe_allow_html=True)
current_answer = st.session_state.responses[st.session_state.current_question] if st.session_state.responses[st.session_state.current_question] else ""
response = st.text_input("Your Answer", value=current_answer, key=st.session_state.current_question)

# Button logic with container for styling
st.markdown('<div class="button-container">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    if st.button("Previous") and st.session_state.current_question > 0:
        # Save current response and move to the previous question
        st.session_state.responses[st.session_state.current_question] = response
        st.session_state.current_question -= 1

with col2:
    if st.button("Next"):
        # Check if response is empty
        if response.strip() == "":
            st.warning("Please provide an answer before moving to the next question.")
        else:
            # Save current response before moving to the next question
            st.session_state.responses[st.session_state.current_question] = response
            # Move to next question or save responses if at the last question
            if st.session_state.current_question < len(questions) - 1:
                st.session_state.current_question += 1
            else:
                # Save responses to separate files
                with open("primary_symptom.txt", "w") as f_primary:
                    f_primary.write(st.session_state.responses[0] + "\n")
                with open("other_symptoms.txt", "w") as f_others:
                    for answer in st.session_state.responses[1:]:
                        f_others.write(answer + "\n")
                # Set success message flag
                st.session_state.show_success = True
                # Reset for a new session if needed
                st.session_state.current_question = 0
                st.session_state.responses = [""] * len(questions)
                # Rerun to display the success message at the top
                st.experimental_rerun()
st.markdown('</div>', unsafe_allow_html=True)
