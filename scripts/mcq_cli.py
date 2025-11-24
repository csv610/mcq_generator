#!/usr/bin/env python3
"""
MCQ Generator CLI - Generate multiple-choice questions from the command line
"""

import argparse
import json
import logging
import sys
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import litellm
from mcq_generator import QuestionGenerator
from binary_question_generator import BinaryQuestionGenerator, BinaryQuestionConfig
from question_translator import QuestionTranslator
from question_prerequsite import QuestionPrerequisite
from similar_question_generator import SimilarQuestionGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcq_cli.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MCQGeneratorCLI:
    """Handles MCQ generation and management via CLI"""

    def __init__(self):
        self.model = None

    def set_model(self, provider: str, model_name: str):
        """Initialize the LLM model based on provider"""
        try:
            # Store provider and model for later use with LiteLLM
            self.provider = provider
            self.model_name = model_name
            # For OpenAI, prepend 'openai/' to model name if not already present
            if provider.lower() == "openai":
                self.model = f"openai/{model_name}" if not model_name.startswith("openai/") else model_name
            else:
                self.model = f"{provider}/{model_name}" if "/" not in model_name else model_name

            print(f"✓ Model '{model_name}' initialized ({provider})")
            logger.info(f"Model initialized: {provider} - {model_name}")
        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            raise Exception(f"Failed to initialize model: {e}")

    def generate_questions(self, specialization: str, difficulty: str,
                          num_questions: int, max_tokens: int) -> List[Dict]:
        """Generate MCQ questions"""
        if not self.model:
            raise Exception("Model not initialized. Please set up a model first.")

        try:
            generator = QuestionGenerator(self.model)
            print(f"\n📚 Generating {num_questions} {difficulty} questions on '{specialization}'...")

            questions = generator.generate_questions(
                specialization, difficulty, num_questions, max_tokens
            )

            if questions:
                print(f"✓ Successfully generated {len(questions)} questions\n")
                logger.info(f"Generated {len(questions)} questions for {specialization}")
                return questions
            else:
                raise Exception("Failed to generate questions. Check logs for details.")

        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            raise Exception(f"Error generating questions: {e}")

    def generate_binary_questions(self, specialization: str, difficulty: str,
                                 num_questions: int, question_type: str = "true_false",
                                 max_tokens: int = 2000) -> List[Dict]:
        """Generate binary choice questions (True/False or Yes/No)"""
        if not self.model:
            raise Exception("Model not initialized. Please set up a model first.")

        try:
            generator = BinaryQuestionGenerator(self.model)
            question_type_label = "True/False" if question_type == "true_false" else "Yes/No"
            print(f"\n📚 Generating {num_questions} {difficulty} {question_type_label} questions on '{specialization}'...")

            config = BinaryQuestionConfig(
                field=specialization,
                difficulty=difficulty,
                num_questions=num_questions,
                question_type=question_type,
                max_tokens=max_tokens
            )
            questions = generator.generate_questions(config)

            if questions:
                print(f"✓ Successfully generated {len(questions)} {question_type_label} questions\n")
                logger.info(f"Generated {len(questions)} {question_type_label} questions for {specialization}")
                return questions
            else:
                raise Exception(f"Failed to generate {question_type_label} questions. Check logs for details.")

        except Exception as e:
            logger.error(f"Error generating {question_type} questions: {e}")
            raise Exception(f"Error generating questions: {e}")

    def display_questions(self, questions: List[Dict], show_answers: bool = False, is_binary: bool = False):
        """Display questions in a formatted way"""
        if not questions:
            print("No questions to display.")
            return

        for idx, q in enumerate(questions, 1):
            print(f"Question {idx}:")
            print(f"{q.get('question', 'N/A')}")

            if is_binary:
                # For binary questions, show explanation
                if show_answers:
                    print(f"\n✓ Answer: {q.get('correct_answer', 'N/A')}")
                    print(f"\nExplanation: {q.get('explanation', 'N/A')}")
            else:
                # For MCQ, show options
                print(f"\nOptions:")
                options = q.get('options', {})
                if isinstance(options, dict):
                    for key, option in options.items():
                        print(f"  {key}. {option}")
                else:
                    # Handle list format
                    for i, option in enumerate(options, 1):
                        print(f"  {chr(64+i)}. {option}")

                if show_answers:
                    print(f"\n✓ Correct Answer: {q.get('correct_answer', 'N/A')}")

            print()  # Blank line between questions

    def save_questions(self, questions: List[Dict], specialization: str,
                      filename: str = None):
        """Save questions to JSON file"""
        if not questions:
            raise Exception("No questions to save.")

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mcq_{specialization}_{timestamp}.json"

        try:
            filepath = Path(filename)
            data = {
                "specialization": specialization,
                "generated_at": datetime.now().isoformat(),
                "question_count": len(questions),
                "questions": questions
            }

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"✓ Questions saved to '{filename}'")
            logger.info(f"Questions saved to {filename}")

        except Exception as e:
            logger.error(f"Error saving questions: {e}")
            raise Exception(f"Error saving questions: {e}")

    def load_questions(self, filename: str) -> Dict:
        """Load questions from JSON file"""
        try:
            filepath = Path(filename)
            if not filepath.exists():
                raise Exception(f"File '{filename}' not found.")

            with open(filepath, 'r') as f:
                data = json.load(f)

            print(f"✓ Loaded {len(data.get('questions', []))} questions from '{filename}'")
            logger.info(f"Loaded questions from {filename}")
            return data

        except Exception as e:
            logger.error(f"Error loading questions: {e}")
            raise Exception(f"Error loading questions: {e}")


def cmd_init_model(args, cli_app):
    """Initialize the AI model"""
    try:
        cli_app.set_model(args.provider, args.model)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_generate(args, cli_app):
    """Generate MCQ questions"""
    try:
        questions = cli_app.generate_questions(
            args.specialization, args.difficulty.capitalize(), args.count, args.max_tokens
        )
        cli_app.display_questions(questions, show_answers=args.show_answers)

        if args.save:
            cli_app.save_questions(questions, args.specialization, args.save)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_load(args, cli_app):
    """Load and display questions from a JSON file"""
    try:
        data = cli_app.load_questions(args.filename)
        questions = data.get('questions', [])
        print(f"\nLoaded from: {args.filename}")
        print(f"Specialization: {data.get('specialization', 'N/A')}")
        print(f"Generated at: {data.get('generated_at', 'N/A')}\n")
        cli_app.display_questions(questions, show_answers=args.show_answers)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_explain(args, cli_app):
    """Get detailed explanation for a specific question"""
    try:
        if not cli_app.model:
            raise Exception("Model not initialized. Use 'init-model' command first.")

        data = cli_app.load_questions(args.filename)
        questions = data.get('questions', [])

        if args.question_num < 1 or args.question_num > len(questions):
            raise Exception(f"Invalid question number. Valid range: 1-{len(questions)}")

        question = questions[args.question_num - 1]

        from prompt_builder import PromptBuilder
        prompt_builder = PromptBuilder()

        # Handle both dict and list formats for options
        options = question['options']
        if isinstance(options, dict):
            options_list = list(options.values())
        else:
            options_list = options

        prompt = prompt_builder.get_explain_answer_prompt(
            question['question'],
            options_list,
            question['correct_answer']
        )

        print(f"\n📖 Generating explanation for Question {args.question_num}...\n")

        try:
            response = litellm.completion(
                model=cli_app.model,
                messages=[
                    {"role": "system", "content": "You are an expert assistant providing detailed explanations for multiple-choice questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=args.max_tokens,
                temperature=0.7
            )
            explanation = response.choices[0].message.content
            print(f"{explanation}\n")
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            print(f"Unable to generate explanation: {e}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_translate(args, cli_app):
    """Translate questions to another language"""
    try:
        if not cli_app.model:
            raise Exception("Model not initialized. Use 'init-model' command first.")

        data = cli_app.load_questions(args.filename)
        questions = data.get('questions', [])
        translator = QuestionTranslator(cli_app.model)

        print(f"\n🌐 Translating questions to {args.language.upper()}...\n")

        translated_questions = []
        for i, q in enumerate(questions, 1):
            print(f"  Translating question {i}/{len(questions)}...", end='\r')
            translated_q = q.copy()
            translated_q['question'] = translator.translate_text(q['question'], args.language.capitalize())

            # Handle both dict and list formats for options
            options = q['options']
            if isinstance(options, dict):
                translated_q['options'] = {
                    key: translator.translate_text(opt, args.language.capitalize())
                    for key, opt in options.items()
                }
            else:
                translated_q['options'] = [
                    translator.translate_text(opt, args.language.capitalize())
                    for opt in options
                ]
            translated_questions.append(translated_q)

        print()  # New line after progress
        cli_app.display_questions(translated_questions)

        if args.save:
            output_file = f"{Path(args.filename).stem}_{args.language}.json"
            cli_app.save_questions(translated_questions, data.get('specialization', 'translated'), output_file)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_prerequisites(args, cli_app):
    """Get prerequisite knowledge for a question"""
    try:
        if not cli_app.model:
            raise Exception("Model not initialized. Use 'init-model' command first.")

        data = cli_app.load_questions(args.filename)
        questions = data.get('questions', [])

        if args.question_num < 1 or args.question_num > len(questions):
            raise Exception(f"Invalid question number. Valid range: 1-{len(questions)}")

        question = questions[args.question_num - 1]

        print(f"\n📚 Fetching prerequisite knowledge for Question {args.question_num}...\n")

        prereq_generator = QuestionPrerequisite(cli_app.model)

        # Handle both dict and list formats for options
        options = question['options']
        if isinstance(options, dict):
            options_list = list(options.values())
        else:
            options_list = options

        prerequisites = prereq_generator.question_prerequisites(
            question['question'],
            options_list
        )
        prerequisite = '\n'.join(prerequisites) if isinstance(prerequisites, list) else prerequisites

        print(f"{prerequisite}\n")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_similar(args, cli_app):
    """Generate a similar question based on an existing one"""
    try:
        if not cli_app.model:
            raise Exception("Model not initialized. Use 'init-model' command first.")

        data = cli_app.load_questions(args.filename)
        questions = data.get('questions', [])

        if args.question_num < 1 or args.question_num > len(questions):
            raise Exception(f"Invalid question number. Valid range: 1-{len(questions)}")

        question = questions[args.question_num - 1]

        print(f"\n✨ Generating similar question based on Question {args.question_num}...\n")

        similar_gen = SimilarQuestionGenerator(cli_app.model)
        similar_question = similar_gen.generate_similar_question(question['question'])

        print(f"{similar_question}\n")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_generate_binary(args, cli_app):
    """Generate binary choice questions (True/False or Yes/No)"""
    try:
        questions = cli_app.generate_binary_questions(
            args.specialization, args.difficulty.capitalize(), args.count,
            args.question_type, args.max_tokens
        )
        cli_app.display_questions(questions, show_answers=args.show_answers, is_binary=True)

        if args.save:
            cli_app.save_questions(questions, args.specialization, args.save)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_info(args, cli_app):
    """Display MCQ Generator CLI information"""
    info_text = """
╔════════════════════════════════════════════════════════════════════╗
║                   MCQ Generator CLI v1.0.0                        ║
║                                                                    ║
║  Generate high-quality multiple choice questions using AI         ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

QUICK START:
  1. Initialize a model (default: Perplexity Sonar):
     $ python cli.py init-model
     or: python cli.py init-model --provider openai --model gpt-4o-mini

  2. Generate MCQ questions:
     $ python cli.py generate --specialization "Python Programming" \\
       --difficulty medium --count 5

  3. Generate True/False questions:
     $ python cli.py generate-binary --specialization "Biology" \\
       --question-type true_false --difficulty easy --count 5

  4. Generate Yes/No questions:
     $ python cli.py generate-binary --specialization "History" \\
       --question-type yes_no --difficulty medium --count 3

  5. Load and view questions:
     $ python cli.py load questions.json --show-answers

  6. Get explanations:
     $ python cli.py explain questions.json --question-num 1

AVAILABLE COMMANDS:
  • init-model       Initialize the AI model
  • generate         Generate MCQ questions
  • generate-binary  Generate True/False or Yes/No questions
  • load             Load questions from file
  • explain          Get explanation for a question
  • translate        Translate questions to another language
  • prerequisites    Get prerequisite knowledge
  • similar          Generate similar question
  • info             Show this information

For more help: python cli.py COMMAND --help
    """
    print(info_text)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='MCQ Generator CLI',
        description='Generate high-quality multiple choice questions using AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py init-model --provider openai --model gpt-4o-mini
  python cli.py generate --specialization "Python" --count 5
  python cli.py load questions.json --show-answers
  python cli.py explain questions.json --question-num 1
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # init-model command
    init_parser = subparsers.add_parser('init-model', help='Initialize the AI model')
    init_parser.add_argument('--provider',
                            choices=['openai', 'claude', 'perplexity', 'litellm'],
                            default='perplexity',
                            help='LLM provider (default: perplexity)')
    init_parser.add_argument('--model',
                            type=str,
                            default='sonar',
                            help='Model name (default: sonar)')
    init_parser.set_defaults(func=cmd_init_model)

    # generate command
    gen_parser = subparsers.add_parser('generate', help='Generate MCQ questions')
    gen_parser.add_argument('--specialization', '-s',
                           type=str,
                           required=True,
                           help='Topic or subject for question generation')
    gen_parser.add_argument('--difficulty', '-d',
                           choices=['easy', 'medium', 'hard'],
                           default='medium',
                           help='Difficulty level (default: medium)')
    gen_parser.add_argument('--count', '-c',
                           type=int,
                           default=5,
                           help='Number of questions to generate (default: 5)')
    gen_parser.add_argument('--max-tokens', '-m',
                           type=int,
                           default=3000,
                           help='Maximum tokens for generation (default: 3000)')
    gen_parser.add_argument('--save', '-o',
                           type=str,
                           help='Save questions to JSON file')
    gen_parser.add_argument('--show-answers', '-a',
                           action='store_true',
                           help='Display correct answers')
    gen_parser.set_defaults(func=cmd_generate)

    # generate-binary command
    binary_parser = subparsers.add_parser('generate-binary', help='Generate True/False or Yes/No questions')
    binary_parser.add_argument('--specialization', '-s',
                              type=str,
                              required=True,
                              help='Topic or subject for question generation')
    binary_parser.add_argument('--question-type', '-t',
                              choices=['true_false', 'yes_no'],
                              default='true_false',
                              help='Type of binary question (default: true_false)')
    binary_parser.add_argument('--difficulty', '-d',
                              choices=['easy', 'medium', 'hard'],
                              default='medium',
                              help='Difficulty level (default: medium)')
    binary_parser.add_argument('--count', '-c',
                              type=int,
                              default=5,
                              help='Number of questions to generate (default: 5)')
    binary_parser.add_argument('--max-tokens', '-m',
                              type=int,
                              default=2000,
                              help='Maximum tokens for generation (default: 2000)')
    binary_parser.add_argument('--save', '-o',
                              type=str,
                              help='Save questions to JSON file')
    binary_parser.add_argument('--show-answers', '-a',
                              action='store_true',
                              help='Display correct answers and explanations')
    binary_parser.set_defaults(func=cmd_generate_binary)

    # load command
    load_parser = subparsers.add_parser('load', help='Load questions from file')
    load_parser.add_argument('filename',
                            type=str,
                            help='JSON file containing questions')
    load_parser.add_argument('--show-answers',
                            action='store_true',
                            help='Display correct answers')
    load_parser.set_defaults(func=cmd_load)

    # explain command
    explain_parser = subparsers.add_parser('explain', help='Explain a question')
    explain_parser.add_argument('filename',
                               type=str,
                               help='JSON file containing questions')
    explain_parser.add_argument('--question-num', '-q',
                               type=int,
                               required=True,
                               help='Question number to explain (1-based index)')
    explain_parser.add_argument('--max-tokens',
                               type=int,
                               default=1500,
                               help='Maximum tokens for explanation (default: 1500)')
    explain_parser.set_defaults(func=cmd_explain)

    # translate command
    trans_parser = subparsers.add_parser('translate', help='Translate questions')
    trans_parser.add_argument('filename',
                             type=str,
                             help='JSON file containing questions')
    trans_parser.add_argument('--language', '-l',
                             choices=['hindi', 'spanish', 'french'],
                             default='hindi',
                             help='Target language (default: hindi)')
    trans_parser.add_argument('--save',
                             action='store_true',
                             help='Save translated questions')
    trans_parser.set_defaults(func=cmd_translate)

    # prerequisites command
    prereq_parser = subparsers.add_parser('prerequisites', help='Get prerequisite knowledge')
    prereq_parser.add_argument('filename',
                              type=str,
                              help='JSON file containing questions')
    prereq_parser.add_argument('--question-num', '-q',
                              type=int,
                              required=True,
                              help='Question number (1-based index)')
    prereq_parser.set_defaults(func=cmd_prerequisites)

    # similar command
    sim_parser = subparsers.add_parser('similar', help='Generate similar question')
    sim_parser.add_argument('filename',
                           type=str,
                           help='JSON file containing questions')
    sim_parser.add_argument('--question-num', '-q',
                           type=int,
                           required=True,
                           help='Question number to use as reference (1-based index)')
    sim_parser.set_defaults(func=cmd_similar)

    # info command
    info_parser = subparsers.add_parser('info', help='Show information')
    info_parser.set_defaults(func=cmd_info)

    args = parser.parse_args()

    # Initialize CLI
    cli_app = MCQGeneratorCLI()

    # Execute command
    if hasattr(args, 'func'):
        args.func(args, cli_app)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == '__main__':
    main()
