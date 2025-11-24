"""
True/False Question Generator - Generates True/False type questions

Handles LLM API calls to generate True/False statements with answers and explanations.
"""

import re
import logging
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


class TrueFalseQuestionGenerator:
    """Generator for creating True/False questions from LLM responses."""

    def __init__(self, model: str):
        """Initialize with an LLM model.

        Args:
            model: Model identifier for LiteLLM (e.g., 'openai/gpt-4', 'claude/claude-3-opus')
        """
        self.model = model
        self.prompt_builder = PromptBuilder()

    def parse_question(self, response_text: str) -> dict:
        """Parse LLM response into structured True/False question format.

        Args:
            response_text: Raw text response from LLM

        Returns:
            Dictionary containing 'question', 'correct_answer', and 'explanation' keys,
            or empty dict if parsing fails
        """
        pattern = r"Question:\s*(.+?)(?:\n|$)\s*Answer:\s*(True|False)\s*(?:\n|$)\s*Explanation:\s*(.+?)(?:\n\n|$)"

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

    def generate_questions(
        self,
        field: str,
        difficulty: str,
        num_questions: int,
        max_tokens: int = 2000,
    ) -> list:
        """Generate True/False questions using LLM.

        Args:
            field: Subject field for question generation
            difficulty: Difficulty level (Easy, Medium, Hard)
            num_questions: Number of questions to generate
            max_tokens: Maximum tokens for LLM response (default: 2000)

        Returns:
            List of question dictionaries with 'question', 'correct_answer', and 'explanation' keys.
            Returns empty list if generation fails after retries.
        """
        prompt = self.prompt_builder.get_true_false_question_generation_prompt(
            field, num_questions, difficulty
        )
        logger.info("Generating True/False questions with prompt: %s", prompt)

        try:
            content = self._call_llm(prompt, max_tokens)
            response_list = content.strip().split("\n\n")
        except Exception as e:
            logger.error("Error generating True/False questions after retries: %s", e)
            return []

        questions = []
        with tqdm(total=len(response_list), desc="Parsing True/False questions", unit="q") as pbar:
            for choice in response_list:
                parsed = self.parse_question(choice)
                if parsed:
                    questions.append(parsed)
                pbar.update(1)

        logger.info("Generated %d True/False questions", len(questions))
        return questions


if __name__ == "__main__":
    model = "openai/gpt-4o-mini"
    generator = TrueFalseQuestionGenerator(model)
    questions = generator.generate_questions("History", "Easy", 2)
    print(questions)
