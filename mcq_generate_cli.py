#!/usr/bin/env python3
"""
MCQ Generate CLI - MCQ creation tool
Creates multiple-choice questions using AI with customizable options and difficulty levels
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from question_generator import QuestionGenerator

# Constants
LOG_FILE = 'mcq_generate.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Configure logging
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


class MCQGenerationEngine:
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

    def generate(self, field: str, difficulty: str, num_questions: int, num_options: int,
                num_correct_answers: int = 1, max_tokens: int = 3000, subfield: str = None) -> list:
        """Create MCQ questions.

        Args:
            field: Subject field
            difficulty: Easy, Medium, or Hard
            num_questions: Number of questions to create
            num_options: Options per question (must be > 1)
            num_correct_answers: Correct answers per question (default: 1)
            max_tokens: Max tokens for LLM response (default: 3000)
            subfield: Optional sub-category

        Returns:
            List of generated questions

        Raises:
            ValueError: If parameters are invalid
            Exception: If question generation fails
        """
        self._validate_params(num_options, num_correct_answers)
        topic = f"{field} - {subfield}" if subfield else field

        print(f"\n📚 Creating {num_questions} {difficulty} questions on '{topic}' ({num_options} options)...")
        logger.info(f"Starting creation: {num_questions} {difficulty} questions on {topic}")

        questions = self.generator.generate_questions(
            field, difficulty, num_questions, max_tokens, num_options, num_correct_answers
        )

        if not questions:
            logger.error("Question generation failed: no questions returned")
            raise RuntimeError("Failed to create questions from LLM")

        print(f"✓ Created {len(questions)} questions\n")
        logger.info(f"Successfully created {len(questions)} questions")
        return questions

    def save_questions(self, questions: list, field: str, filename: str = None, subfield: str = None) -> str:
        """Save questions to JSON file.

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
            "questions": questions
        }

        try:
            filepath = Path(filename)
            with open(filepath, 'w') as f:
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

    def display_questions(self, questions: list) -> None:
        """Display questions in formatted output.

        Args:
            questions: List of question dictionaries

        Each question includes: question text, options, and correct answer(s)
        """
        if not questions:
            print("No questions to display")
            return

        for idx, q in enumerate(questions, 1):
            print(f"\n{'='*70}")
            print(f"Q{idx}: {q.get('question', 'N/A')}")
            print("\nOptions:")
            self._print_options(q.get('options', {}))
            self._print_answer(q.get('correct_answer', 'N/A'))
            print(f"{'='*70}")


def _format_model_id(provider: str, model_name: str) -> str:
    """Format model ID for LiteLLM."""
    if "/" in model_name:
        return model_name
    return f"{provider}/{model_name}"

def setup_model(provider: str, model_name: str) -> str:
    """Setup LLM model."""
    model = _format_model_id(provider, model_name)
    print(f"✓ Model: {model_name} ({provider})")
    return model




def _validate_cli_args(args) -> None:
    """Validate command-line arguments.

    Args:
        args: Parsed command-line arguments

    Raises:
        ValueError: If any argument value is invalid
    """
    if not args.field or not args.field.strip():
        raise ValueError("Field must be a non-empty string")

    if args.subfield is not None and not args.subfield.strip():
        raise ValueError("Subfield must be a non-empty string if provided")

    if args.count < 1:
        raise ValueError("Number of questions (--count) must be at least 1")

    if args.options < 2:
        raise ValueError("Number of options (--options) must be greater than 1")

    if args.correct_answers < 0:
        raise ValueError("Number of correct answers must be at least 0 (0 means 'None of the Above')")

    if args.correct_answers > args.options:
        raise ValueError("Number of correct answers cannot exceed number of options")

    if args.max_tokens < 100:
        raise ValueError("Max tokens must be at least 100")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='mcq_generate_cli',
        description='Create MCQ questions using AI'
    )

    parser.add_argument(
        '--field', '-f',
        type=str,
        required=True,
        help='Topic or subject field'
    )
    parser.add_argument(
        '--subfield', '-sf',
        type=str,
        help='Sub-category within field (optional)'
    )
    parser.add_argument(
        '--difficulty', '-d',
        choices=['easy', 'medium', 'hard'],
        default='medium',
        help='Difficulty level (default: medium)'
    )
    parser.add_argument(
        '--count', '-c',
        type=int,
        default=5,
        help='Number of questions (default: 5)'
    )
    parser.add_argument(
        '--options', '-o',
        type=int,
        required=True,
        help='Options per question (must be > 1)'
    )
    parser.add_argument(
        '--correct-answers',
        type=int,
        default=1,
        help='Correct answers per question (0 for "None of the Above", default: 1)'
    )
    parser.add_argument(
        '--max-tokens',
        type=int,
        default=3000,
        help='Max tokens for LLM (default: 3000)'
    )
    parser.add_argument(
        '--provider',
        choices=['openai', 'claude', 'perplexity', 'litellm'],
        default='perplexity',
        help='LLM provider (default: perplexity)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='sonar',
        help='Model name (default: sonar)'
    )
    parser.add_argument(
        '--save',
        type=str,
        help='Save to JSON file (auto-generated if not specified)'
    )

    args = parser.parse_args()

    try:
        _validate_cli_args(args)
        model = setup_model(args.provider, args.model)
        engine = MCQGenerationEngine(model)
        questions = engine.generate(
            args.field,
            args.difficulty.capitalize(),
            args.count,
            args.options,
            args.correct_answers,
            args.max_tokens,
            args.subfield
        )
        engine.display_questions(questions)
        if args.save:
            engine.save_questions(questions, args.field, args.save, args.subfield)
    except ValueError as e:
        print(f"Invalid input: {e}", file=sys.stderr)
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
