#!/usr/bin/env python3
"""
Binary Question Generator CLI - Create True/False and Yes/No questions using AI
Generates binary choice questions with customizable options and difficulty levels
"""

import argparse
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from binary_question_generator import BinaryQuestionGenerator, QuestionConfig

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.FileHandler("binary_question_cli.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


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

    if args.max_tokens < 100:
        raise ValueError("Max tokens must be at least 100")

    if args.question_type not in ["true_false", "yes_no"]:
        raise ValueError("Question type must be 'true_false' or 'yes_no'")


def _generate_output_filename(field: str, question_type: str) -> str:
    """Generate output filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_field = field.lower().replace(" ", "_")
    return f"binary_questions_{safe_field}_{question_type}_{timestamp}.json"


def _save_questions(questions: list, field: str, question_type: str, filename: str = None) -> str:
    """Save questions to JSON file.

    Args:
        questions: List of question dictionaries
        field: Field/topic for the questions
        question_type: Type of questions (true_false or yes_no)
        filename: Optional custom filename

    Returns:
        Path to saved file
    """
    if not filename:
        filename = _generate_output_filename(field, question_type)

    output = {
        "metadata": {
            "field": field,
            "question_type": question_type,
            "count": len(questions),
            "generated_at": datetime.now().isoformat(),
        },
        "questions": questions,
    }

    filepath = Path(filename)
    with open(filepath, "w") as f:
        json.dump(output, f, indent=2)

    return str(filepath)


def _display_questions(questions: list, question_type: str) -> None:
    """Display questions in a formatted way.

    Args:
        questions: List of question dictionaries
        question_type: Type of questions (true_false or yes_no)
    """
    if not questions:
        print("No questions generated.")
        return

    q_type_label = "True/False" if question_type == "true_false" else "Yes/No"
    print(f"\n{'=' * 80}")
    print(f"{q_type_label} Questions ({len(questions)} total)")
    print(f"{'=' * 80}\n")

    for i, q in enumerate(questions, 1):
        print(f"Question {i}:")
        print(f"  {q['question']}")
        print(f"  Answer: {q['correct_answer']}")
        print(f"  Explanation: {q['explanation']}")
        print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="binary_question_cli",
        description="Create True/False and Yes/No questions using AI",
    )

    parser.add_argument("--field", "-f", type=str, required=True, help="Topic or subject field")
    parser.add_argument("--subfield", "-sf", type=str, help="Sub-category within field (optional)")
    parser.add_argument(
        "--difficulty",
        "-d",
        choices=["easy", "medium", "hard"],
        default="medium",
        help="Difficulty level (default: medium)",
    )
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=5,
        help="Number of questions (default: 5)",
    )
    parser.add_argument(
        "--question-type",
        "-qt",
        choices=["true_false", "yes_no"],
        default="true_false",
        help="Type of binary questions (default: true_false)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2000,
        help="Max tokens for LLM (default: 2000)",
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "claude", "perplexity", "litellm"],
        default="perplexity",
        help="LLM provider (default: perplexity)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="sonar",
        help="Model name (default: sonar)",
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save to JSON file (auto-generated if not specified)",
    )
    parser.add_argument(
        "--display",
        action="store_true",
        help="Display questions after generation (default: True)",
    )

    args = parser.parse_args()

    try:
        _validate_cli_args(args)
        model = setup_model(args.provider, args.model)

        generator = BinaryQuestionGenerator(model)
        config = QuestionConfig(
            field=args.field,
            difficulty=args.difficulty.capitalize(),
            num_questions=args.count,
            question_type=args.question_type,
            max_tokens=args.max_tokens,
            subfield=args.subfield,
        )

        print(f"\n✓ Generating {args.count} {args.question_type.replace('_', '/')} questions for {args.field}...")
        questions = generator.generate_questions(config)

        if not questions:
            print("Failed to generate questions.", file=sys.stderr)
            logger.error("No questions were generated")
            sys.exit(1)

        print(f"✓ Generated {len(questions)} questions")

        # Display questions
        _display_questions(questions, args.question_type)

        # Save to file
        filepath = _save_questions(questions, args.field, args.question_type, args.save)
        print(f"✓ Questions saved to: {filepath}")
        logger.info(f"Generated {len(questions)} {args.question_type} questions, saved to {filepath}")

    except ValueError as e:
        print(f"Invalid input: {e}", file=sys.stderr)
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
