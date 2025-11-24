import streamlit as st
import logging
import os
import json
import re
from openai import OpenAI

# Initialize logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenAI client (API key fetched from environment variable)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Ensure your API key is stored in the environment
if not OPENAI_API_KEY:
    st.error("OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# Cache for storing explanations and references to avoid redundant API calls
if "explanation_cache" not in st.session_state:
    st.session_state.explanation_cache = {}

if "reference_cache" not in st.session_state:
    st.session_state.reference_cache = {}

# Store original questions in English
if "original_questions" not in st.session_state:
    st.session_state.original_questions = []

# Handle errors and logs
def log_and_notify_user(message, log_level="error"):
    """ Logs the message and notifies the user with a formatted error/warning. """
    if log_level == "error":
        logging.error(message)
        st.error(f"Error: {message}")
    elif log_level == "warning":
        logging.warning(message)
        st.warning(f"Warning: {message}")
    else:
        logging.info(message)

# Parse the response to extract question and options
def parse_question(response_text):
    """
    Parse the response from OpenAI API and extract the question, options, and correct answer.
    """
    try:
        # Extract the question text
        question_match = re.search(r'Question: (.*?)\n', response_text, re.DOTALL)
        question_text = question_match.group(1) if question_match else None
        
        # Extract options
        options = re.findall(r'[A-D]\. (.*?)\n', response_text)

        # Extract the correct answer
        correct_answer_match = re.search(r'Correct Answer: ([A-D])', response_text)
        correct_answer = correct_answer_match.group(1) if correct_answer_match else None
        
        return question_text, options, correct_answer
    except Exception as e:
        log_and_notify_user(f"Error parsing question: {str(e)}")
        return None, None, None

# Generate questions using OpenAI API, initially in English
def generate_mcq(model, specialization, difficulty, num_questions=5, max_tokens=3000):
    """
    Generates multiple-choice questions using OpenAI API in English.
    """
    try:
        prompt = f"""Generate {num_questions} unambiguous, unbiased, and verifiable multiple-choice questions about {specialization} at a {difficulty} difficulty level in English. 
        Cover a wide range of subtopics within the specialization, including both theoretical concepts and practical real-world applications.
        The questions should reflect the variety of topics that may appear in competitive examinations and educational assessments.
        
        Ensure that each question is based on factual information that can be verified using reliable sources such as textbooks, academic papers, or well-known websites (e.g., government or university websites). Avoid speculative or opinion-based content.
        
        All questions must be unambiguous, with clear language that leaves no room for misinterpretation.
        
        Ensure the questions and options are unbiased, free from any cultural, racial, or gender bias, and are appropriate for diverse audiences.

        Each question MUST be unique, and have exactly 4 options (A, B, C, D), with only one correct answer. Format each question as follows:

        Question: [Question text]
        A. [Option A]
        B. [Option B]
        C. [Option C]
        D. [Option D]
        Correct Answer: [A/B/C/D]

        Ensure that the options are plausible, and avoid trivial or obviously incorrect answers. Include real-world context where relevant, and ensure that all questions are diverse, covering different aspects of {specialization}."""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates factual, diverse, unambiguous, and unbiased multiple-choice questions in English. Always provide exactly 4 options for each question with meaningful content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            n=1,
            temperature=0.7,
        )

        # Log the response for debugging
        logging.info(f"Response from OpenAI: {response}")

        # Split the response into individual questions
        questions = response.choices[0].message.content.strip().split("\n\n")

        # Raise an error if no questions were generated
        if not questions or len(questions) < num_questions:
            raise ValueError(f"Failed to generate the requested number of questions. Only {len(questions)} questions generated.")

        return questions
    
    except Exception as e:
        log_and_notify_user(f"Error generating MCQ: {str(e)}")
        return []

# Translate text from English to the chosen language
def translate_text(text, language):
    """
    Translates the given text from English to the chosen language using OpenAI API.
    Supports Hindi translation for now.
    """
    if language == "English":
        return text  # No translation needed

    try:
        if language == "Hindi":
            prompt = f"Translate the following text to Hindi:\n\n{text}"
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a translator who accurately translates text from English to Hindi."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5,
        )
        translated_text = response.choices[0].message.content.strip()
        return translated_text
    
    except Exception as e:
        log_and_notify_user(f"Error translating text: {str(e)}")
        return text

# Translate all questions and options to the selected language
def translate_questions(language):
    """
    Translates the stored questions and options to the selected language, with a spinner.
    """
    translated_questions = []
    with st.spinner(f"Translating questions to {language}..."):
        for q in st.session_state.original_questions:
            translated_question = translate_text(q['question'], language)
            translated_options = [translate_text(opt, language) for opt in q['options']]
            translated_questions.append({
                "question": translated_question,
                "options": translated_options,
                "correct_answer": q['correct_answer']  # No need to translate the correct answer key
            })
    st.session_state.questions = translated_questions

# Explanation for correct answer in English, then translate if needed
def explain_answer(model, question, correct_answer, options, language, max_tokens=1500):
    """
    Uses OpenAI to explain the correct answer, its background, and related information in English, then translates if necessary.
    Caches the response to avoid repeated API calls.
    """
    if question in st.session_state.explanation_cache:
        logging.info(f"Fetching explanation from cache for question: {question}")
        return st.session_state.explanation_cache[question]

    try:
        # Include the options in the prompt
        options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])

        prompt = f"""Explain the following multiple-choice question and why the correct answer is {correct_answer} in English:
        
        {question}

        {options_text}
        
        Please provide a detailed explanation, including any background information or context relevant to the question."""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert assistant providing detailed explanations for multiple-choice questions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        explanation = response.choices[0].message.content.strip()

        # Cache the explanation in English
        st.session_state.explanation_cache[question] = explanation

        # Translate explanation if needed
        return translate_text(explanation, language)
    
    except Exception as e:
        log_and_notify_user(f"Error explaining answer: {str(e)}")
        return "Explanation not available due to an error."

# Fetch prerequisite background material
def fetch_prerequisite(model, question, options, max_tokens=1500):
    """
    Uses OpenAI to fetch prerequisite background material for a given question and its options.
    Caches the response to avoid repeated API calls.
    """
    if question in st.session_state.reference_cache:
        logging.info(f"Fetching prerequisite from cache for question: {question}")
        return st.session_state.reference_cache[question]

    try:
        options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])

        prompt = f"""Provide a detailed background material that would help a student understand the following question and its options. 
        The material should cover fundamental concepts, definitions, and any necessary background knowledge related to the question and its options.

        Question: {question}

        {options_text}
        
        The explanation should be detailed, yet clear and beginner-friendly, aimed at a student who is not familiar with the topic."""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert teacher providing detailed prerequisite background material for a question."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        prerequisite_material = response.choices[0].message.content.strip()

        # Cache the prerequisite material
        st.session_state.reference_cache[question] = prerequisite_material

        return prerequisite_material
    
    except Exception as e:
        log_and_notify_user(f"Error fetching prerequisite material: {str(e)}")
        return "Prerequisite material not available due to an error."

# Save questions to JSON file in English
def save_to_json_in_english(filename):
    """
    Saves the list of questions to a JSON file in English.
    """
    with open(filename, 'w') as f:
        json.dump(st.session_state.original_questions, f, indent=2)

# Generate similar questions using OpenAI API
def generate_similar_question(model, question, num_questions=1, max_tokens=1500):
    """
    Generates a similar but unique question on the same topic as the provided question using OpenAI API.
    Ensures the new question is not a duplicate or semantically identical to the original.
    """
    try:
        prompt = f"""Generate {num_questions} unique, unambiguous, and unbiased multiple-choice questions based on the following question. 
        The new question should cover a similar topic or idea but must not be a duplicate or semantically similar to the original question.
        It should enhance the user's understanding of the topic.

        Original Question: {question}
        
        Each question MUST have exactly 4 options (A, B, C, D), with only one correct answer. 
        Format the output strictly as follows:

        Question: [Question text]
        A. [Option A]
        B. [Option B]
        C. [Option C]
        D. [Option D]
        Correct Answer: [A/B/C/D]

        Ensure the correct answer is only a letter (A, B, C, D) and no explanation is included."""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates unique and valuable multiple-choice questions on similar topics."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            n=1,
            temperature=0.7,
        )

        # Extract the generated question and return it
        generated_question = response.choices[0].message.content.strip()
        return generated_question
    
    except Exception as e:
        log_and_notify_user(f"Error generating similar question: {str(e)}")
        return "Similar question not available due to an error."



# Main Streamlit Application
def main():
    """
    Main Streamlit app logic.
    """
    st.sidebar.title("MCQ Generator")

    # Model selection
    model = st.sidebar.selectbox("Select Model", ["gpt-4o-mini", "gpt-4o", "gpt-4"])

    language = st.sidebar.selectbox("Select Language", ["English", "Hindi"])
    
    # User inputs
    specialization = st.sidebar.text_input("Enter the specialization:")
    difficulty = st.sidebar.selectbox("Select difficulty level:", ["Easy", "Medium", "Hard"])
    num_questions = st.sidebar.number_input("Number of questions:", min_value=1, max_value=100, value=5)
    max_tokens_question = st.sidebar.number_input("Max Tokens for Question Generation", min_value=100, max_value=4000, value=3000)
    max_tokens_explanation = st.sidebar.number_input("Max Tokens for Explanation", min_value=100, max_value=4000, value=1500)

    # Generate Questions
    if st.sidebar.button("Generate Questions"):
        if not specialization or not difficulty or not language:
            st.sidebar.error("Please fill out all fields.")
        else:
            st.session_state.questions = []
            st.session_state.original_questions = []  # Clear previous questions

            with st.spinner("Generating questions..."):
                raw_questions = generate_mcq(model, specialization, difficulty, num_questions, max_tokens_question)
                if raw_questions:
                    st.session_state.questions = []
                    st.session_state.original_questions = []  # Store questions in English
                    for raw_q in raw_questions:
                        question_text, options, correct_answer = parse_question(raw_q)
                        if question_text and options:
                            # Store the original English questions
                            st.session_state.original_questions.append({
                                "question": question_text,
                                "options": options,
                                "correct_answer": correct_answer
                            })

                    # Immediately translate to the selected language
                    translate_questions(language)
                    logging.info(f"{num_questions} questions generated.")
                else:
                    st.error("Failed to generate questions.")

    # Automatically translate questions when language is changed
    if st.session_state.get("original_questions"):
        translate_questions(language)

    # Save to JSON (always in English)
    if st.sidebar.button("Save Questions to JSON"):
        if st.session_state.get("original_questions"):
            filename = "questions.json"  # Updated to remove timestamp
            save_to_json_in_english(filename)
            st.sidebar.success(f"Questions saved as {filename}.")
        else:
            st.sidebar.error("No questions to save.")

    # Display Questions and Check Answer
    if st.session_state.get("questions"):
        for i, q in enumerate(st.session_state.questions, start=1):
            st.subheader(f"Question {i}")
            st.write(q["question"])

            # Display options using radio buttons
            user_answer = st.radio("Options", q["options"], key=f"q{i}")

            # Check Answer
            if st.button(f"Check Answer for Question {i}"):
                if user_answer == q["options"][ord(q["correct_answer"]) - ord("A")]:
                    st.success("Correct!")
                else:
                    st.error(f"Incorrect. The correct answer is {q['correct_answer']}: {q['options'][ord(q['correct_answer']) - ord('A')]}")

            # Explain Answer
            if st.button(f"Explain Answer for Question {i}"):
                with st.spinner(f"Explaining answer for Question {i}..."):
                    explanation = explain_answer(model, q["question"], q["correct_answer"], q["options"], language, max_tokens=max_tokens_explanation)
                    st.write(explanation)

            # Prerequisite Background Material
            if st.button(f"Prerequisite for Question {i}"):
                with st.spinner(f"Fetching prerequisite material for Question {i}..."):
                    prerequisite_material = fetch_prerequisite(model, q["question"], q["options"], max_tokens=max_tokens_explanation)
                    st.write(prerequisite_material)

            # Generate Similar Question
            if st.button(f"Generate Similar Question for Question {i}"):
                with st.spinner(f"Generating similar question for Question {i}..."):
                    similar_question = generate_similar_question(model, q["question"], num_questions=1, max_tokens=max_tokens_explanation)
                    st.write(similar_question)

if __name__ == "__main__":
    main()
