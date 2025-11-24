"""
MCQ Generator - Core MCQ generation engine and configuration

Provides the MCQGenerator class for creating, validating, saving, and
displaying multiple-choice questions using AI-powered question generation.
Also includes QuestionGenerator for LLM API calls and question parsing.
Questions are always stored in JSON format.
"""

import re
import json
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import litellm
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from prompt_builder import PromptBuilder


# Constants
LOG_FILE = "mcq_generate.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


def setup_logger():
    """Setup logging configuration."""
    logger = logging.getLogger(__name__)
    if logger.handlers:
        return logger

    try:
        handler = logging.FileHandler(LOG_FILE)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
    except IOError as e:
        print(f"Warning: Could not create log file: {e}")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    return logger


logger = setup_logger()

# Configure logging for this module
if not logger.handlers:
    handler = logging.FileHandler(LOG_FILE)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
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


class MCQGenerator:
    """Engine for creating MCQ questions"""

    def __init__(self, model: str):
        """Initialize with an LLM model."""
        self.model = model
        self.generator = QuestionGenerator(model)
        logger.info(f"Engine initialized: {model}")

    def _validate_params(self, num_options: int, num_correct_answers: int) -> None:
        """Validate input parameters.

        Args:
            num_options: Number of options per question
            num_correct_answers: Number of correct answers (0 means 'None of the Above')

        Raises:
            ValueError: If parameters are invalid
        """
        if num_options < 2:
            raise ValueError("Number of options must be > 1")
        if num_correct_answers < 0:
            raise ValueError("Number of correct answers must be >= 0")

    def generate(self, config: QuestionConfig, filename: str = None) -> str:
        """Create MCQ questions and save to JSON file.

        Args:
            config: QuestionConfig dataclass with generation parameters
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to the saved JSON file

        Raises:
            ValueError: If parameters are invalid
            Exception: If question generation fails
        """
        self._validate_params(config.num_options, config.num_correct_answers)
        topic = f"{config.field} - {config.subfield}" if config.subfield else config.field

        print(
            f"\n📚 Creating {config.num_questions} {config.difficulty} "
            f"questions on '{topic}' ({config.num_options} options)..."
        )
        logger.info(
            f"Starting creation: {config.num_questions} {config.difficulty} "
            f"questions on {topic}"
        )

        questions = self.generator.generate_questions(
            config.field,
            config.difficulty,
            config.num_questions,
            config.max_tokens,
            config.num_options,
            config.num_correct_answers,
        )

        if not questions:
            logger.error("Question generation failed: no questions returned")
            raise RuntimeError("Failed to create questions from LLM")

        print(f"✓ Created {len(questions)} questions\n")
        logger.info(f"Successfully created {len(questions)} questions")

        filepath = self._save_questions(questions, config.field, filename, config.subfield)
        return filepath

    def _save_questions(
        self, questions: list, field: str, filename: str = None, subfield: str = None
    ) -> str:
        """Save questions to JSON file (internal method).

        Args:
            questions: List of question dictionaries
            field: Subject field
            filename: Output filename (auto-generated if not provided)
            subfield: Optional sub-category

        Returns:
            Path to saved file

        Raises:
            ValueError: If questions list is empty
            IOError: If file cannot be written
        """
        if not questions:
            raise ValueError("Cannot save: questions list is empty")

        if not filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            field_part = f"{field}_{subfield}" if subfield else field
            filename = f"mcq_{field_part}_{ts}.json"

        data = {
            "field": field,
            "subfield": subfield,
            "generated_at": datetime.now().isoformat(),
            "question_count": len(questions),
            "questions": questions,
        }

        try:
            filepath = Path(filename)
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Questions saved to {filename}")
            print(f"✓ Saved to '{filename}'")
            return str(filepath)
        except IOError as e:
            logger.error(f"Failed to save file {filename}: {e}")
            raise IOError(f"Cannot write to file '{filename}': {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to serialize questions: {e}")
            raise ValueError(f"Cannot serialize questions to JSON: {e}")

    def _print_options(self, options: dict) -> None:
        """Print question options.

        Args:
            options: Dictionary of option letter: text pairs
        """
        if isinstance(options, dict):
            for key, val in options.items():
                print(f"  {key}. {val}")
        else:
            for idx, val in enumerate(options, 1):
                print(f"  {chr(64+idx)}. {val}")

    def _print_answer(self, ans) -> None:
        """Print correct answer(s).

        Args:
            ans: Single answer string or list of answers
        """
        if isinstance(ans, list):
            print(f"\n✓ Answer: {', '.join(ans)}")
        else:
            print(f"\n✓ Answer: {ans}")

    def load_questions(self, filepath: str) -> list:
        """Load questions from a JSON file.

        Args:
            filepath: Path to the JSON file

        Returns:
            List of question dictionaries

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not valid JSON
        """
        try:
            with open(filepath) as f:
                data = json.load(f)
            return data.get("questions", [])
        except FileNotFoundError as e:
            logger.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"Questions file not found: {filepath}") from e
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file: {filepath}")
            raise ValueError(f"Invalid JSON in file '{filepath}': {e}") from e

    def display_questions(self, questions: list) -> None:
        """Display questions in formatted output with progress tracking.

        Args:
            questions: List of question dictionaries

        Each question includes: question text, options, and correct answer(s)
        """
        if not questions:
            print("No questions to display")
            return

        for idx, q in tqdm(
            enumerate(questions, 1), total=len(questions), desc="Displaying questions", unit="q"
        ):
            print(f"\n{'='*70}")
            print(f"Q{idx}: {q.get('question', 'N/A')}")
            print("\nOptions:")
            self._print_options(q.get("options", {}))
            self._print_answer(q.get("correct_answer", "N/A"))
            print(f"{'='*70}")
