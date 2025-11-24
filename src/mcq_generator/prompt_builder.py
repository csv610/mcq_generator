"""
Prompt Builder - Generates prompts for LLM question generation

Creates formatted prompts for various question types including multiple-choice questions,
translations, explanations, prerequisites, and similar questions. Supports dynamic option
generation and multiple correct answers.
"""


class PromptBuilder:
    """Builder for generating prompts to send to LLM for various tasks."""

    def get_mcq_generation_prompt(self, field: str, difficulty: str, num_questions: int,
                                  num_options: int, num_correct_answers: int = 1) -> str:
        """Generate a prompt for creating multiple-choice questions.

        Creates a detailed prompt with quality requirements and competitive exam standards
        for the LLM to generate unambiguous, unbiased questions.

        Args:
            field: Subject field for questions
            difficulty: Difficulty level (Easy, Medium, Hard)
            num_questions: Number of questions to generate
            num_options: Number of options per question
            num_correct_answers: Number of correct answers per question (default: 1)

        Returns:
            Formatted prompt string for LLM consumption
        """
        # Generate option letters dynamically
        option_letters = [chr(65 + i) for i in range(num_options)]  # A, B, C, D, E, ...
        option_format = "\n        ".join([f"{letter}. [Option {letter}]" for letter in option_letters])
        correct_answer_format = "/".join(option_letters)

        # Determine correct answer instruction based on num_correct_answers
        if num_correct_answers == 0:
            correct_answer_instruction = "with 'None of the Above' as the only correct answer"
            answer_format = f"Correct Answer: ['None of the Above']"
        elif num_correct_answers == 1:
            correct_answer_instruction = "with only one correct answer"
            answer_format = f"Correct Answer: [{correct_answer_format}]"
        elif num_correct_answers == num_options:
            correct_answer_instruction = "with 'All of the Above' as the only correct answer"
            answer_format = f"Correct Answer: ['All of the Above']"
        else:
            correct_answer_instruction = f"with {num_correct_answers} correct answer(s) (can include 'All of the Above' or 'None of the Above')"
            answer_format = f"Correct Answer: [One or more from {correct_answer_format}, or 'All of the Above', or 'None of the Above']"

        new_prompt  = f"""Generate {num_questions} unambiguous, unbiased, and verifiable multiple-choice questions about {field} at a {difficulty} difficulty level in English for competitive exams.

QUALITY REQUIREMENTS:
- Cover a wide range of subtopics within the field, including both theoretical concepts and practical real-world applications
- Base each question on factual information verifiable from textbooks, academic papers, or reliable websites
- Use clear language with no room for misinterpretation
- Ensure no cultural, racial, or gender bias; appropriate for diverse audiences
- Each question must be unique (no duplicates)

COMPETITIVE EXAM STANDARDS:
- Match the difficulty level: Easy (recall/simple application), Medium (analysis/application), Hard (critical thinking/synthesis)
- Follow competitive exam format and style
- Align with standard exam syllabus and learning objectives
- Make each question solvable within 1-3 minutes
- Ensure correct answer is clearly distinguishable from incorrect options
- Create plausible distractors that are logical but definitively wrong
- Distribute questions across different topics to avoid repetition
- Avoid trick questions or misleading wording
- Use current and updated information/examples
- Employ standard technical language consistent with exam conventions
- Avoid or clearly mark negative questions (EXCEPT, NOT, NEVER)
- Avoid double negatives
- Ensure each option is distinct and non-overlapping
- Randomize the position of correct answers (avoid patterns)

FORMAT:
Each question MUST have exactly {num_options} options ({", ".join(option_letters)}), {correct_answer_instruction}.

Question: [Question text]
{option_format}
{answer_format}

Each question should be solvable independently and represent diverse aspects of {field}."""

        return new_prompt
    
    def get_text_translation_prompt(self, text: str, language: str) -> str:
        """Generate a prompt for text translation.

        Args:
            text: Text to translate
            language: Target language for translation

        Returns:
            Formatted prompt string for LLM consumption
        """
        new_prompt = f"Translate the following text to {language}:\n\n{text}"
        return new_prompt

    def get_explain_answer_prompt(self, question: str, options, correct_answer: str) -> str:
        """Generate a prompt for explaining question answers.

        Args:
            question: The question text
            options: Question options (dict or list) or None
            correct_answer: The correct answer letter(s)

        Returns:
            Formatted prompt string for LLM consumption
        """
        if options:
            new_prompt = f"""Explain the following multiple-choice question and why the correct answer is {correct_answer} in English:

            {question}

            {options}

            Please provide a detailed explanation, including any background information or context relevant to the question."""
        else:
            new_prompt = f"""Explain the following question and why the correct answer is {correct_answer} in English:

            {question}

            Please provide a detailed explanation, including any background information or context relevant to the question."""

        return new_prompt
    
    def get_prerequisites_prompt(self, question: str, options) -> str:
        """Generate a prompt for explaining prerequisites and background.

        Args:
            question: The question text
            options: Question options (dict or list) or None

        Returns:
            Formatted prompt string for LLM consumption
        """
        if options:
            new_prompt = f"""Provide detailed background material that would help a student understand the following question and its options.
            The material should cover fundamental concepts, definitions, and any necessary background knowledge related to the question and its options.

            Question: {question}

            {options}

            The explanation should be detailed, yet clear and beginner-friendly, aimed at a student who is not familiar with the topic."""

        else:
            new_prompt = f"""Provide detailed background material that would help a student understand the following question.
            The material should cover fundamental concepts, definitions, and any necessary background knowledge related to the question.

            Question: {question}

            The explanation should be detailed, yet clear and beginner-friendly, aimed at a student who is not familiar with the topic."""

        return new_prompt
    
    def get_similar_question_generation_prompt(self, question: str, num_questions: int = 1,
                                               with_options: bool = True) -> str:
        """Generate a prompt for creating similar questions.

        Args:
            question: The original question to base similar questions on
            num_questions: Number of similar questions to generate (default: 1)
            with_options: Whether to generate multiple-choice options (default: True)

        Returns:
            Formatted prompt string for LLM consumption
        """
        if with_options:
            new_prompt = f"""Generate {num_questions} unique, unambiguous, and unbiased multiple-choice questions based on the following question.
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
        else:
            new_prompt = f"""Generate {num_questions} unique, unambiguous, and unbiased questions based on the following question.
            The new question should cover a similar topic or idea but must not be a duplicate or semantically similar to the original question.
            It should enhance the user's understanding of the topic.

            Original Question: {question}"""

        return new_prompt
    
    def get_true_false_question_generation_prompt(self, field: str, num_questions: int = 1, difficulty: str = "Medium") -> str:
        """Generate a prompt for creating True/False questions.

        Args:
            field: Subject field for question generation
            num_questions: Number of questions to generate (default: 1)
            difficulty: Difficulty level (Easy, Medium, Hard) (default: Medium)

        Returns:
            Formatted prompt string for LLM consumption
        """
        new_prompt = f"""Generate {num_questions} unique, unambiguous, and unbiased True/False questions about {field} at a {difficulty} difficulty level.
Each question should clearly indicate whether the statement is true or false, and provide a detailed explanation for the answer.

QUALITY REQUIREMENTS:
- Cover a wide range of subtopics within {field}
- Use clear language with no room for misinterpretation
- Ensure no cultural, racial, or gender bias
- Each question must be unique (no duplicates)
- Match the difficulty level: Easy (recall), Medium (understanding), Hard (critical thinking)

Format the output strictly as follows:

Question: [True/False statement]
Answer: [True/False]
Explanation: [Detailed explanation of why the answer is correct]"""

        return new_prompt
    
    def get_yes_no_question_generation_prompt(self, field: str, num_questions: int = 1, difficulty: str = "Medium") -> str:
        """Generate a prompt for creating Yes/No questions.

        Args:
            field: Subject field for question generation
            num_questions: Number of questions to generate (default: 1)
            difficulty: Difficulty level (Easy, Medium, Hard) (default: Medium)

        Returns:
            Formatted prompt string for LLM consumption
        """
        new_prompt = f"""Generate {num_questions} unique, unambiguous, and unbiased Yes/No questions about {field} at a {difficulty} difficulty level.
Each question should clearly indicate whether the answer is yes or no, and provide a detailed explanation for the answer.

QUALITY REQUIREMENTS:
- Cover a wide range of subtopics within {field}
- Use clear language with no room for misinterpretation
- Ensure no cultural, racial, or gender bias
- Each question must be unique (no duplicates)
- Match the difficulty level: Easy (recall), Medium (understanding), Hard (critical thinking)

Format the output strictly as follows:

Question: [Yes/No question]
Answer: [Yes/No]
Explanation: [Detailed explanation of why the answer is correct]"""

        return new_prompt
    
if __name__ == "__main__":
    prompt_builder = PromptBuilder()
    
    # Build a multiple-choice question prompt
    prompt = prompt_builder.get_mcq_generation_prompt("Physics", "Medium", 5)
    print("MCQ Prompt:\n", prompt_builder)
    
    # Build a translation prompt
    prompt = prompt_builder.get_text_translation_prompt("Hello, how are you?", "Hindi")
    print("\nTranslation Prompt:\n", prompt_builder)
    
    # Build an explanation prompt
    prompt = prompt_builder.get_explain_answer_prompt("What is the force of gravity?", ["9.8 m/s²", "9.81 m/s²", "10 m/s²", "8.5 m/s²"], "B")
    print("\nExplanation Prompt:\n", prompt)
    
    # Build a prerequisite prompt
    prompt = prompt_builder.get_prerequisites_prompt("What is Newton's second law?", ["F=ma", "E=mc²", "F=mv", "F=mg"])
    print("\nPrerequisite Prompt:\n", prompt)
    
    # Build a similar question prompt
    prompt = prompt_builder.get_similar_question_generation_prompt("What is the speed of light?")
    print("\nSimilar Question Prompt:\n", prompt)
