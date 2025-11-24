"""
Question Generator - Parses LLM responses and generates MCQ questions

Handles LLM API calls using LiteLLM and parses responses into structured
multiple-choice question format with support for variable number of options
and multiple correct answers.
"""

import re
import logging
from dataclasses import dataclass
import litellm
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from prompt_builder import PromptBuilder

# Configure logging for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.FileHandler("mcq_generate.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@dataclass
class QuestionConfig:
    """Configuration for MCQ question generation."""

    field: str
    difficulty: str
    num_questions: int
    num_options: int
    num_correct_answers: int = 1
    max_tokens: int = 3000
    subfield: str = None


class QuestionGenerator:
    """Generator for creating MCQ questions from LLM responses."""

    def __init__(self, model: str):
        """Initialize with an LLM model.

        Args:
            model: Model identifier for LiteLLM (e.g., 'openai/gpt-4', 'claude/claude-3-opus')
        """
        self.model = model
        self.prompt_builder = PromptBuilder()

    def parse_question(self, response_text: str, num_options: int) -> dict:
        """Parse LLM response into structured question format.

        Dynamically builds regex pattern based on the number of options to extract
        question text, options, and correct answer(s) from LLM response.

        Args:
            response_text: Raw text response from LLM
            num_options: Number of options per question

        Returns:
            Dictionary containing 'question', 'options', and 'correct_answer' keys,
            or empty dict if parsing fails
        """
        # Dynamically generate option letters based on num_options
        option_letters = [chr(65 + i) for i in range(num_options)]  # A, B, C, D, E, ...

        # Build pattern to extract question and options
        option_pattern_parts = [
            f"{letter}\\.\\s*(.+?)(?=\\n[A-Z]\\.|\\nCorrect Answer:|$)" for letter in option_letters
        ]
        option_pattern = r"\s*".join(option_pattern_parts)
        pattern = f"Question:\\s*(.+?)\\n{option_pattern}\\s*Correct Answer:\\s*([^\n]+)"

        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            options = {}
            for i, letter in enumerate(option_letters):
                # Extract and clean the option text
                option_text = match.group(i + 2).strip()
                # Remove trailing whitespace and any special characters like trailing spaces
                options[letter] = option_text.rstrip()

            # Extract the correct answer, handling the line ending
            correct_answer_str = match.group(len(option_letters) + 2).strip()
            # Remove anything after the first newline (like rationale or source)
            correct_answer_str = correct_answer_str.split("\n")[0].strip()

            # Parse multiple answers: "A", "A and B", "A, B, C", "All of the Above",
            # "None of the Above"
            correct_answers = self._parse_correct_answers(correct_answer_str)

            return {
                "question": match.group(1).strip(),
                "options": options,
                "correct_answer": correct_answers,
            }
        return {}

    def _parse_correct_answers(self, answer_str: str) -> list:
        """Parse correct answer string into a list.

        Handles multiple answer formats including single letters (A), multiple letters
        separated by 'and' (A and B) or commas (A, B, C), and special cases like
        'All of the Above' and 'None of the Above'.

        Args:
            answer_str: Raw answer string from LLM response

        Returns:
            List of uppercase answer letters or special answer strings
        """
        answer_str = answer_str.strip()

        if answer_str.lower() in ["all of the above", "all of above"]:
            return ["All of the Above"]
        if answer_str.lower() in ["none of the above", "none of above"]:
            return ["None of the Above"]

        answers = re.split(r"\s+and\s+|,\s*", answer_str)
        return [ans.strip().upper() for ans in answers if ans.strip()]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )

    def _call_llm(self, prompt: str, max_tokens: int) -> str:
        """Call LLM API with retry logic.

        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens for LLM response

        Returns:
            The LLM response content

        Raises:
            Exception: If LLM call fails after retries
        """
        response = litellm.completion(
            model=self.model, messages=[{"role": "user", "content": prompt}], max_tokens=max_tokens
        )
        return response.choices[0].message.content

    def generate_questions(
        self,
        field: str,
        difficulty: str,
        num_questions: int,
        max_tokens: int,
        num_options: int,
        num_correct_answers: int = 1,
    ) -> list:
        """Generate MCQ questions using LLM.

        Calls LiteLLM API with a formatted prompt, parses the response, and returns
        structured question data. Includes retry logic for transient failures.

        Args:
            field: Subject field for question generation
            difficulty: Difficulty level (Easy, Medium, Hard)
            num_questions: Number of questions to generate
            max_tokens: Maximum tokens for LLM response
            num_options: Number of options per question
            num_correct_answers: Number of correct answers per question (default: 1)

        Returns:
            List of question dictionaries with 'question', 'options', and 'correct_answer' keys.
            Returns empty list if generation fails after retries.
        """
        prompt = self.prompt_builder.get_mcq_generation_prompt(
            field, difficulty, num_questions, num_options, num_correct_answers
        )
        logger.info("Generating questions with prompt: %s", prompt)

        try:
            content = self._call_llm(prompt, max_tokens)
            response_list = content.strip().split("\n\n")
        except Exception as e:
            logger.error("Error generating questions after retries: %s", e)
            return []  # Return an empty list on error

        questions = []
        with tqdm(total=len(response_list), desc="Parsing questions", unit="q") as pbar:
            for choice in response_list:
                parsed = self.parse_question(choice, num_options)
                if parsed:
                    questions.append(parsed)
                pbar.update(1)

        logger.info("Generated %d questions", len(questions))
        return questions


if __name__ == "__main__":
    # Example usage
    model = "openai/gpt-4o-mini"
    generator = QuestionGenerator(model)
    questions = generator.generate_questions("History", "Easy", 4, 1000)
    print(questions)
