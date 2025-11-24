"""
Binary Question Generator - Generates True/False and Yes/No type questions

Handles LLM API calls to generate binary choice questions (True/False or Yes/No)
with answers and explanations.
"""

import re
import logging
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import litellm
from tqdm import tqdm
from prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.FileHandler("mcq_generate.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@dataclass
class QuestionConfig:
    """Configuration for binary question generation."""

    field: str
    difficulty: str
    num_questions: int
    question_type: str = "true_false"
    max_tokens: int = 2000
    subfield: str = None


class BinaryQuestionGenerator:
    """Generator for creating binary choice questions (True/False or Yes/No) from LLM responses."""

    VALID_TYPES = ["true_false", "yes_no"]

    def __init__(self, model: str):
        """Initialize with an LLM model.

        Args:
            model: Model identifier for LiteLLM (e.g., 'openai/gpt-4', 'claude/claude-3-opus')
        """
        self.model = model
        self.prompt_builder = PromptBuilder()

    def parse_question(self, response_text: str, question_type: str) -> dict:
        """Parse LLM response into structured binary question format.

        Args:
            response_text: Raw text response from LLM
            question_type: Type of binary question ('true_false' or 'yes_no')

        Returns:
            Dictionary containing 'question', 'correct_answer', and 'explanation' keys,
            or empty dict if parsing fails
        """
        if question_type == "true_false":
            answer_pattern = r"(True|False)"
        elif question_type == "yes_no":
            answer_pattern = r"(Yes|No)"
        else:
            return {}

        pattern = rf"Question:\s*(.+?)(?:\n|$)\s*Answer:\s*{answer_pattern}\s*(?:\n|$)\s*Explanation:\s*(.+?)(?:\n\n|$)"

        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            return {
                "question": match.group(1).strip(),
                "correct_answer": match.group(2).strip(),
                "explanation": match.group(3).strip(),
            }
        return {}

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

    def generate_questions(self, config: QuestionConfig) -> list:
        """Generate binary choice questions using LLM.

        Args:
            config: QuestionConfig with generation parameters

        Returns:
            List of question dictionaries with 'question', 'correct_answer', and 'explanation' keys.
            Returns empty list if generation fails after retries.

        Raises:
            ValueError: If question_type is not valid
        """
        if config.question_type not in self.VALID_TYPES:
            raise ValueError(
                f"question_type must be one of {self.VALID_TYPES}, got '{config.question_type}'"
            )

        if config.question_type == "true_false":
            prompt = self.prompt_builder.get_true_false_question_generation_prompt(
                config.field, config.num_questions, config.difficulty
            )
            desc = "Parsing True/False questions"
        else:  # yes_no
            prompt = self.prompt_builder.get_yes_no_question_generation_prompt(
                config.field, config.num_questions, config.difficulty
            )
            desc = "Parsing Yes/No questions"

        logger.info("Generating %s questions with prompt: %s", config.question_type, prompt)

        try:
            content = self._call_llm(prompt, config.max_tokens)
            response_list = content.strip().split("\n\n")
        except Exception as e:
            logger.error("Error generating %s questions after retries: %s", config.question_type, e)
            return []

        questions = []
        with tqdm(total=len(response_list), desc=desc, unit="q") as pbar:
            for choice in response_list:
                parsed = self.parse_question(choice, config.question_type)
                if parsed:
                    questions.append(parsed)
                pbar.update(1)

        logger.info("Generated %d %s questions", len(questions), config.question_type)
        return questions


if __name__ == "__main__":
    model = "openai/gpt-4o-mini"
    generator = BinaryQuestionGenerator(model)

    tf_config = QuestionConfig(
        field="History",
        difficulty="Easy",
        num_questions=2,
        question_type="true_false"
    )
    tf_questions = generator.generate_questions(tf_config)
    print("True/False Questions:", tf_questions)

    yn_config = QuestionConfig(
        field="Science",
        difficulty="Easy",
        num_questions=2,
        question_type="yes_no"
    )
    yn_questions = generator.generate_questions(yn_config)
    print("Yes/No Questions:", yn_questions)
