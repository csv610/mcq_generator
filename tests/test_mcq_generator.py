"""
Unit tests for MCQ Generator module
Tests QuestionConfig dataclass and MCQGenerator class
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcq_generator import MCQGenerator, QuestionConfig


class TestQuestionConfig(unittest.TestCase):
    """Test QuestionConfig dataclass"""

    def test_config_with_required_fields_only(self):
        """Test QuestionConfig creation with only required fields"""
        config = QuestionConfig(
            field="Physics",
            difficulty="Medium",
            num_questions=5,
            num_options=4
        )

        self.assertEqual(config.field, "Physics")
        self.assertEqual(config.difficulty, "Medium")
        self.assertEqual(config.num_questions, 5)
        self.assertEqual(config.num_options, 4)
        self.assertEqual(config.num_correct_answers, 1)
        self.assertEqual(config.max_tokens, 3000)
        self.assertIsNone(config.subfield)

    def test_config_with_all_fields(self):
        """Test QuestionConfig with all fields specified"""
        config = QuestionConfig(
            field="Chemistry",
            difficulty="Hard",
            num_questions=10,
            num_options=5,
            num_correct_answers=2,
            max_tokens=4000,
            subfield="Quantum Chemistry"
        )

        self.assertEqual(config.field, "Chemistry")
        self.assertEqual(config.difficulty, "Hard")
        self.assertEqual(config.num_questions, 10)
        self.assertEqual(config.num_options, 5)
        self.assertEqual(config.num_correct_answers, 2)
        self.assertEqual(config.max_tokens, 4000)
        self.assertEqual(config.subfield, "Quantum Chemistry")

    def test_config_defaults(self):
        """Test default values in QuestionConfig"""
        config = QuestionConfig(
            field="Biology",
            difficulty="Easy",
            num_questions=3,
            num_options=4
        )

        self.assertEqual(config.num_correct_answers, 1)
        self.assertEqual(config.max_tokens, 3000)
        self.assertIsNone(config.subfield)

    def test_config_zero_correct_answers(self):
        """Test QuestionConfig with zero correct answers"""
        config = QuestionConfig(
            field="History",
            difficulty="Medium",
            num_questions=5,
            num_options=4,
            num_correct_answers=0
        )

        self.assertEqual(config.num_correct_answers, 0)

    def test_config_multiple_correct_answers(self):
        """Test QuestionConfig with multiple correct answers"""
        config = QuestionConfig(
            field="Math",
            difficulty="Hard",
            num_questions=8,
            num_options=6,
            num_correct_answers=3
        )

        self.assertEqual(config.num_correct_answers, 3)


class TestMCQGeneratorInit(unittest.TestCase):
    """Test MCQGenerator initialization"""

    def test_init_with_valid_model(self):
        """Test MCQGenerator initialization with valid model"""
        generator = MCQGenerator("openai/gpt-4o-mini")

        self.assertEqual(generator.model, "openai/gpt-4o-mini")
        self.assertIsNotNone(generator.generator)

    def test_init_with_claude_model(self):
        """Test MCQGenerator initialization with Claude model"""
        generator = MCQGenerator("claude/claude-3-opus")

        self.assertEqual(generator.model, "claude/claude-3-opus")

    def test_init_with_perplexity_model(self):
        """Test MCQGenerator initialization with Perplexity model"""
        generator = MCQGenerator("perplexity/sonar")

        self.assertEqual(generator.model, "perplexity/sonar")


class TestMCQGeneratorValidation(unittest.TestCase):
    """Test MCQGenerator parameter validation"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = MCQGenerator("openai/gpt-4o-mini")

    def test_validate_params_valid_single_answer(self):
        """Test _validate_params with valid single answer"""
        # Should not raise any exception
        self.generator._validate_params(num_options=4, num_correct_answers=1)

    def test_validate_params_valid_multiple_answers(self):
        """Test _validate_params with valid multiple answers"""
        # Should not raise any exception
        self.generator._validate_params(num_options=4, num_correct_answers=2)

    def test_validate_params_valid_zero_answers(self):
        """Test _validate_params with zero answers (None of the Above)"""
        # Should not raise any exception
        self.generator._validate_params(num_options=4, num_correct_answers=0)

    def test_validate_params_minimum_options(self):
        """Test _validate_params with minimum valid options"""
        # Should not raise any exception
        self.generator._validate_params(num_options=2, num_correct_answers=1)

    def test_validate_params_insufficient_options(self):
        """Test _validate_params with insufficient options"""
        with self.assertRaises(ValueError) as context:
            self.generator._validate_params(num_options=1, num_correct_answers=1)

        self.assertIn("Number of options must be > 1", str(context.exception))

    def test_validate_params_negative_correct_answers(self):
        """Test _validate_params with negative correct answers"""
        with self.assertRaises(ValueError) as context:
            self.generator._validate_params(num_options=4, num_correct_answers=-1)

        self.assertIn("Number of correct answers must be >= 0", str(context.exception))

    def test_validate_params_negative_options(self):
        """Test _validate_params with negative options"""
        with self.assertRaises(ValueError) as context:
            self.generator._validate_params(num_options=-1, num_correct_answers=1)

        self.assertIn("Number of options must be > 1", str(context.exception))


class TestMCQGeneratorSaveQuestions(unittest.TestCase):
    """Test MCQGenerator question saving functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = MCQGenerator("openai/gpt-4o-mini")
        self.sample_questions = [
            {
                "question": "What is 2+2?",
                "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                "correct_answer": ["B"]
            },
            {
                "question": "What is the capital of France?",
                "options": {"A": "London", "B": "Paris", "C": "Berlin", "D": "Madrid"},
                "correct_answer": ["B"]
            }
        ]

    def test_save_questions_with_custom_filename(self):
        """Test _save_questions with custom filename"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                filepath = self.generator._save_questions(
                    self.sample_questions,
                    "Math",
                    filename="custom_questions.json",
                    subfield=None
                )

                self.assertEqual(filepath, "custom_questions.json")
                self.assertTrue(Path(filepath).exists())

                # Verify file contents
                with open(filepath) as f:
                    data = json.load(f)

                self.assertEqual(data["field"], "Math")
                self.assertEqual(data["question_count"], 2)
                self.assertEqual(len(data["questions"]), 2)
                self.assertIsNone(data["subfield"])
            finally:
                os.chdir(original_dir)

    def test_save_questions_with_subfield(self):
        """Test _save_questions with subfield"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                filepath = self.generator._save_questions(
                    self.sample_questions,
                    "Physics",
                    filename="physics_quantum.json",
                    subfield="Quantum Mechanics"
                )

                with open(filepath) as f:
                    data = json.load(f)

                self.assertEqual(data["field"], "Physics")
                self.assertEqual(data["subfield"], "Quantum Mechanics")
            finally:
                os.chdir(original_dir)

    def test_save_questions_auto_filename(self):
        """Test _save_questions with auto-generated filename"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                filepath = self.generator._save_questions(
                    self.sample_questions,
                    "Chemistry",
                    filename=None,
                    subfield="Organic"
                )

                self.assertTrue(Path(filepath).exists())
                self.assertIn("mcq_Chemistry_Organic", filepath)
                self.assertTrue(filepath.endswith(".json"))
            finally:
                os.chdir(original_dir)

    def test_save_questions_single_question(self):
        """Test _save_questions with single question"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                single_question = [self.sample_questions[0]]
                filepath = self.generator._save_questions(
                    single_question,
                    "Math",
                    filename="single.json"
                )

                with open(filepath) as f:
                    data = json.load(f)

                self.assertEqual(data["question_count"], 1)
                self.assertEqual(len(data["questions"]), 1)
            finally:
                os.chdir(original_dir)

    def test_save_questions_empty_list_raises_error(self):
        """Test _save_questions with empty list raises ValueError"""
        with self.assertRaises(ValueError) as context:
            self.generator._save_questions([], "Math", filename="test.json")

        self.assertIn("Cannot save: questions list is empty", str(context.exception))

    def test_save_questions_has_metadata(self):
        """Test saved questions include required metadata"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                filepath = self.generator._save_questions(
                    self.sample_questions,
                    "Biology",
                    filename="bio.json"
                )

                with open(filepath) as f:
                    data = json.load(f)

                self.assertIn("field", data)
                self.assertIn("subfield", data)
                self.assertIn("generated_at", data)
                self.assertIn("question_count", data)
                self.assertIn("questions", data)
            finally:
                os.chdir(original_dir)


class TestMCQGeneratorLoadQuestions(unittest.TestCase):
    """Test MCQGenerator question loading functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = MCQGenerator("openai/gpt-4o-mini")
        self.sample_data = {
            "field": "Physics",
            "subfield": "Mechanics",
            "generated_at": "2024-11-24T10:00:00",
            "question_count": 2,
            "questions": [
                {
                    "question": "What is Newton's first law?",
                    "options": {"A": "F=ma", "B": "Action-reaction", "C": "Inertia", "D": "Work"},
                    "correct_answer": ["C"]
                },
                {
                    "question": "Define velocity",
                    "options": {"A": "Speed", "B": "Rate of change of position", "C": "Acceleration", "D": "Force"},
                    "correct_answer": ["B"]
                }
            ]
        }

    def test_load_questions_valid_file(self):
        """Test load_questions with valid JSON file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "physics.json"
            with open(test_file, 'w') as f:
                json.dump(self.sample_data, f)

            questions = self.generator.load_questions(str(test_file))

            self.assertEqual(len(questions), 2)
            self.assertEqual(questions[0]["question"], "What is Newton's first law?")
            self.assertEqual(questions[1]["question"], "Define velocity")

    def test_load_questions_single_question(self):
        """Test load_questions with single question file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data = self.sample_data.copy()
            data["questions"] = [self.sample_data["questions"][0]]
            data["question_count"] = 1

            test_file = Path(tmpdir) / "single.json"
            with open(test_file, 'w') as f:
                json.dump(data, f)

            questions = self.generator.load_questions(str(test_file))

            self.assertEqual(len(questions), 1)
            self.assertEqual(questions[0]["question"], "What is Newton's first law?")

    def test_load_questions_preserves_structure(self):
        """Test load_questions preserves question structure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "physics.json"
            with open(test_file, 'w') as f:
                json.dump(self.sample_data, f)

            questions = self.generator.load_questions(str(test_file))

            for q in questions:
                self.assertIn("question", q)
                self.assertIn("options", q)
                self.assertIn("correct_answer", q)

    def test_load_questions_file_not_found(self):
        """Test load_questions with non-existent file"""
        with self.assertRaises(FileNotFoundError) as context:
            self.generator.load_questions("/nonexistent/path/questions.json")

        self.assertIn("Questions file not found", str(context.exception))

    def test_load_questions_invalid_json(self):
        """Test load_questions with invalid JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "invalid.json"
            with open(test_file, 'w') as f:
                f.write("{ invalid json content ]")

            with self.assertRaises(ValueError) as context:
                self.generator.load_questions(str(test_file))

            self.assertIn("Invalid JSON", str(context.exception))

    def test_load_questions_empty_questions_list(self):
        """Test load_questions with empty questions list"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data = self.sample_data.copy()
            data["questions"] = []
            data["question_count"] = 0

            test_file = Path(tmpdir) / "empty.json"
            with open(test_file, 'w') as f:
                json.dump(data, f)

            questions = self.generator.load_questions(str(test_file))

            self.assertEqual(len(questions), 0)
            self.assertIsInstance(questions, list)


class TestMCQGeneratorDisplay(unittest.TestCase):
    """Test MCQGenerator display functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = MCQGenerator("openai/gpt-4o-mini")
        self.sample_questions = [
            {
                "question": "What is 2+2?",
                "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                "correct_answer": ["B"]
            }
        ]

    def test_display_questions_empty_list(self):
        """Test display_questions with empty list"""
        # Should not raise and print "No questions to display"
        self.generator.display_questions([])

    def test_display_questions_single_question(self):
        """Test display_questions with single question"""
        # Should not raise
        self.generator.display_questions(self.sample_questions)

    def test_display_questions_multiple_questions(self):
        """Test display_questions with multiple questions"""
        questions = self.sample_questions * 3
        # Should not raise
        self.generator.display_questions(questions)

    def test_print_answer_string(self):
        """Test _print_answer with string answer"""
        # Should not raise
        self.generator._print_answer("A")

    def test_print_answer_list(self):
        """Test _print_answer with list of answers"""
        # Should not raise
        self.generator._print_answer(["A", "B", "C"])

    def test_print_answer_single_element_list(self):
        """Test _print_answer with single element list"""
        # Should not raise
        self.generator._print_answer(["A"])

    def test_print_options_dict(self):
        """Test _print_options with dictionary"""
        options = {"A": "Option A", "B": "Option B", "C": "Option C"}
        # Should not raise
        self.generator._print_options(options)

    def test_print_options_list(self):
        """Test _print_options with list"""
        options = ["Option A", "Option B", "Option C"]
        # Should not raise
        self.generator._print_options(options)


class TestMCQGeneratorGenerate(unittest.TestCase):
    """Test MCQGenerator generate functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = MCQGenerator("openai/gpt-4o-mini")
        self.sample_questions = [
            {
                "question": "Test question?",
                "options": {"A": "a", "B": "b"},
                "correct_answer": ["A"]
            }
        ]

    @patch('mcq_generator.MCQGenerator._save_questions')
    def test_generate_returns_filepath(self, mock_save):
        """Test generate method returns filepath"""
        mock_save.return_value = "test.json"

        with patch.object(self.generator.generator, 'generate_questions', return_value=self.sample_questions):
            config = QuestionConfig(
                field="Test",
                difficulty="Easy",
                num_questions=1,
                num_options=2
            )

            result = self.generator.generate(config, filename="test.json")

            self.assertEqual(result, "test.json")
            mock_save.assert_called_once()

    @patch('mcq_generator.MCQGenerator._save_questions')
    def test_generate_calls_llm(self, mock_save):
        """Test generate method calls LLM"""
        mock_save.return_value = "test.json"

        with patch.object(self.generator.generator, 'generate_questions', return_value=self.sample_questions) as mock_gen_questions:
            config = QuestionConfig(
                field="Physics",
                difficulty="Medium",
                num_questions=5,
                num_options=4
            )

            self.generator.generate(config)

            mock_gen_questions.assert_called_once()
            args, kwargs = mock_gen_questions.call_args
            self.assertEqual(args[0], "Physics")
            self.assertEqual(args[1], "Medium")
            self.assertEqual(args[2], 5)

    @patch('mcq_generator.MCQGenerator._save_questions')
    def test_generate_empty_questions_raises_error(self, mock_save):
        """Test generate raises error when no questions generated"""
        with patch.object(self.generator.generator, 'generate_questions', return_value=[]):
            config = QuestionConfig(
                field="Test",
                difficulty="Easy",
                num_questions=1,
                num_options=2
            )

            with self.assertRaises(RuntimeError) as context:
                self.generator.generate(config)

            self.assertIn("Failed to create questions", str(context.exception))

    @patch('mcq_generator.MCQGenerator._save_questions')
    def test_generate_with_custom_filename(self, mock_save):
        """Test generate with custom filename"""
        mock_save.return_value = "custom.json"

        with patch.object(self.generator.generator, 'generate_questions', return_value=self.sample_questions):
            config = QuestionConfig(
                field="Test",
                difficulty="Easy",
                num_questions=1,
                num_options=2
            )

            result = self.generator.generate(config, filename="custom.json")

            self.assertEqual(result, "custom.json")
            mock_save.assert_called_once()


if __name__ == '__main__':
    unittest.main()
