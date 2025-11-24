#!/usr/bin/env python3
"""
MCQ Generate CLI - MCQ creation tool
Creates multiple-choice questions using AI with customizable options and difficulty levels
"""

import argparse
import sys
import json
from mcq_generator import MCQGenerator, QuestionConfig, setup_logger

logger = setup_logger()


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
        msg = "Number of correct answers must be at least 0 (0 means 'None of the Above')"
        raise ValueError(msg)

    if args.correct_answers > args.options:
        raise ValueError("Number of correct answers cannot exceed number of options")

    if args.max_tokens < 100:
        raise ValueError("Max tokens must be at least 100")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="mcq_generate_cli", description="Create MCQ questions using AI"
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
        "--count", "-c", type=int, default=5, help="Number of questions (default: 5)"
    )
    parser.add_argument(
        "--options", "-o", type=int, required=True, help="Options per question (must be > 1)"
    )
    parser.add_argument(
        "--correct-answers",
        type=int,
        default=1,
        help='Correct answers per question (0 for "None of the Above", default: 1)',
    )
    parser.add_argument(
        "--max-tokens", type=int, default=3000, help="Max tokens for LLM (default: 3000)"
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "claude", "perplexity", "litellm"],
        default="perplexity",
        help="LLM provider (default: perplexity)",
    )
    parser.add_argument("--model", type=str, default="sonar", help="Model name (default: sonar)")
    parser.add_argument(
        "--save", type=str, help="Save to JSON file (auto-generated if not specified)"
    )

    args = parser.parse_args()

    try:
        _validate_cli_args(args)
        model = setup_model(args.provider, args.model)
        engine = MCQGenerator(model)
        config = QuestionConfig(
            field=args.field,
            difficulty=args.difficulty.capitalize(),
            num_questions=args.count,
            num_options=args.options,
            num_correct_answers=args.correct_answers,
            max_tokens=args.max_tokens,
            subfield=args.subfield,
        )
        filepath = engine.generate(config, args.save)
        with open(filepath) as f:
            data = json.load(f)
        engine.display_questions(data["questions"])
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
