"""
Unit tests for binary_question_cli module
Tests CLI argument parsing, validation, file operations, and integration
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import io

from binary_question_cli import (
    _format_model_id,
    setup_model,
    _validate_cli_args,
    _generate_output_filename,
    _save_questions,
    _display_questions,
)


class TestFormatModelId(unittest.TestCase):
    """Tests for _format_model_id function."""

    def test_format_with_provider_and_model(self):
        """Test formatting provider and model name."""
        result = _format_model_id("openai", "gpt-4o")
        self.assertEqual(result, "openai/gpt-4o")

    def test_format_with_existing_slash(self):
        """Test that existing slash format is returned as-is."""
        result = _format_model_id("openai", "openai/gpt-4o")
        self.assertEqual(result, "openai/gpt-4o")

    def test_format_perplexity(self):
        """Test formatting Perplexity model."""
        result = _format_model_id("perplexity", "sonar")
        self.assertEqual(result, "perplexity/sonar")

    def test_format_claude(self):
        """Test formatting Claude model."""
        result = _format_model_id("claude", "claude-3-opus")
        self.assertEqual(result, "claude/claude-3-opus")


class TestSetupModel(unittest.TestCase):
    """Tests for setup_model function."""

    @patch("builtins.print")
    def test_setup_model_prints_confirmation(self, mock_print):
        """Test that setup_model prints model confirmation."""
        result = setup_model("openai", "gpt-4o")
        self.assertEqual(result, "openai/gpt-4o")
        mock_print.assert_called_with("✓ Model: gpt-4o (openai)")

    def test_setup_model_returns_formatted_id(self):
        """Test that setup_model returns properly formatted model ID."""
        result = setup_model("perplexity", "sonar-pro")
        self.assertEqual(result, "perplexity/sonar-pro")


class TestValidateCliArgs(unittest.TestCase):
    """Tests for _validate_cli_args function."""

    def setUp(self):
        """Create mock args object for testing."""
        self.valid_args = MagicMock()
        self.valid_args.field = "Biology"
        self.valid_args.subfield = "Genetics"
        self.valid_args.count = 5
        self.valid_args.max_tokens = 2000
        self.valid_args.question_type = "true_false"

    def test_valid_args_pass_validation(self):
        """Test that valid arguments pass validation."""
        _validate_cli_args(self.valid_args)

    def test_empty_field_raises_error(self):
        """Test that empty field raises ValueError."""
        self.valid_args.field = ""
        with self.assertRaises(ValueError) as cm:
            _validate_cli_args(self.valid_args)
        self.assertIn("Field must be a non-empty string", str(cm.exception))

    def test_none_field_raises_error(self):
        """Test that None field raises ValueError."""
        self.valid_args.field = None
        with self.assertRaises(ValueError):
            _validate_cli_args(self.valid_args)

    def test_whitespace_field_raises_error(self):
        """Test that whitespace-only field raises ValueError."""
        self.valid_args.field = "   "
        with self.assertRaises(ValueError) as cm:
            _validate_cli_args(self.valid_args)
        self.assertIn("Field must be a non-empty string", str(cm.exception))

    def test_empty_subfield_raises_error(self):
        """Test that empty subfield (when provided) raises ValueError."""
        self.valid_args.subfield = ""
        with self.assertRaises(ValueError) as cm:
            _validate_cli_args(self.valid_args)
        self.assertIn("Subfield must be a non-empty string", str(cm.exception))

    def test_none_subfield_is_valid(self):
        """Test that None subfield is valid (optional)."""
        self.valid_args.subfield = None
        _validate_cli_args(self.valid_args)

    def test_zero_count_raises_error(self):
        """Test that count < 1 raises ValueError."""
        self.valid_args.count = 0
        with self.assertRaises(ValueError) as cm:
            _validate_cli_args(self.valid_args)
        self.assertIn("at least 1", str(cm.exception))

    def test_negative_count_raises_error(self):
        """Test that negative count raises ValueError."""
        self.valid_args.count = -5
        with self.assertRaises(ValueError):
            _validate_cli_args(self.valid_args)

    def test_low_max_tokens_raises_error(self):
        """Test that max_tokens < 100 raises ValueError."""
        self.valid_args.max_tokens = 50
        with self.assertRaises(ValueError) as cm:
            _validate_cli_args(self.valid_args)
        self.assertIn("at least 100", str(cm.exception))

    def test_invalid_question_type_raises_error(self):
        """Test that invalid question type raises ValueError."""
        self.valid_args.question_type = "invalid_type"
        with self.assertRaises(ValueError) as cm:
            _validate_cli_args(self.valid_args)
        self.assertIn("true_false", str(cm.exception))
        self.assertIn("yes_no", str(cm.exception))

    def test_true_false_type_is_valid(self):
        """Test that true_false type is valid."""
        self.valid_args.question_type = "true_false"
        _validate_cli_args(self.valid_args)

    def test_yes_no_type_is_valid(self):
        """Test that yes_no type is valid."""
        self.valid_args.question_type = "yes_no"
        _validate_cli_args(self.valid_args)


class TestGenerateOutputFilename(unittest.TestCase):
    """Tests for _generate_output_filename function."""

    def test_generates_valid_filename(self):
        """Test that function generates a valid filename."""
        filename = _generate_output_filename("Biology", "true_false")
        self.assertTrue(filename.startswith("binary_questions_"))
        self.assertTrue(filename.endswith(".json"))
        self.assertIn("biology", filename)
        self.assertIn("true_false", filename)

    def test_replaces_spaces_with_underscores(self):
        """Test that spaces in field name are replaced with underscores."""
        filename = _generate_output_filename("Computer Science", "yes_no")
        self.assertIn("computer_science", filename)
        self.assertNotIn("Computer Science", filename)

    def test_includes_timestamp(self):
        """Test that filename includes a timestamp."""
        filename = _generate_output_filename("Math", "true_false")
        # Check for date format YYYYMMDD
        self.assertRegex(filename, r"\d{8}_\d{6}")

    def test_consistent_format(self):
        """Test that all filenames follow the same format."""
        filename1 = _generate_output_filename("Physics", "true_false")
        filename2 = _generate_output_filename("Chemistry", "yes_no")

        # Both should start and end the same way
        self.assertTrue(filename1.startswith("binary_questions_"))
        self.assertTrue(filename2.startswith("binary_questions_"))
        self.assertTrue(filename1.endswith(".json"))
        self.assertTrue(filename2.endswith(".json"))


class TestSaveQuestions(unittest.TestCase):
    """Tests for _save_questions function."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_saves_questions_to_json(self):
        """Test that questions are saved to a JSON file."""
        questions = [
            {
                "question": "Is water essential for life?",
                "correct_answer": "Yes",
                "explanation": "Water is crucial for all living organisms."
            }
        ]
        filepath = _save_questions(questions, "Biology", "yes_no")
        self.assertTrue(Path(filepath).exists())

    def test_saved_json_has_correct_structure(self):
        """Test that saved JSON has required metadata and questions."""
        questions = [
            {
                "question": "Test question?",
                "correct_answer": "True",
                "explanation": "Test explanation."
            }
        ]
        filepath = _save_questions(questions, "Test Field", "true_false")

        with open(filepath, "r") as f:
            data = json.load(f)

        self.assertIn("metadata", data)
        self.assertIn("questions", data)
        self.assertEqual(data["metadata"]["field"], "Test Field")
        self.assertEqual(data["metadata"]["question_type"], "true_false")
        self.assertEqual(data["metadata"]["count"], 1)
        self.assertEqual(len(data["questions"]), 1)

    def test_metadata_includes_timestamp(self):
        """Test that metadata includes generated_at timestamp."""
        questions = []
        filepath = _save_questions(questions, "Math", "yes_no")

        with open(filepath, "r") as f:
            data = json.load(f)

        self.assertIn("generated_at", data["metadata"])
        # Verify it's a valid ISO format datetime
        datetime.fromisoformat(data["metadata"]["generated_at"])

    def test_custom_filename_is_used(self):
        """Test that custom filename is respected."""
        questions = []
        custom_filename = "my_custom_questions.json"
        filepath = _save_questions(questions, "Field", "true_false", custom_filename)
        self.assertEqual(filepath, custom_filename)
        self.assertTrue(Path(custom_filename).exists())

    def test_auto_generated_filename_when_none_provided(self):
        """Test that filename is auto-generated when not provided."""
        questions = []
        filepath = _save_questions(questions, "Physics", "yes_no", None)
        self.assertIn("binary_questions_", filepath)
        self.assertTrue(Path(filepath).exists())

    def test_multiple_questions_saved(self):
        """Test that multiple questions are saved correctly."""
        questions = [
            {
                "question": "Q1?",
                "correct_answer": "Yes",
                "explanation": "E1."
            },
            {
                "question": "Q2?",
                "correct_answer": "No",
                "explanation": "E2."
            },
            {
                "question": "Q3?",
                "correct_answer": "True",
                "explanation": "E3."
            }
        ]
        filepath = _save_questions(questions, "Test", "true_false")

        with open(filepath, "r") as f:
            data = json.load(f)

        self.assertEqual(data["metadata"]["count"], 3)
        self.assertEqual(len(data["questions"]), 3)


class TestDisplayQuestions(unittest.TestCase):
    """Tests for _display_questions function."""

    def test_displays_no_questions_message(self):
        """Test that empty questions list displays appropriate message."""
        captured_output = io.StringIO()
        sys.stdout = captured_output

        _display_questions([], "true_false")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("No questions generated", output)

    def test_displays_true_false_questions(self):
        """Test that True/False questions are displayed correctly."""
        questions = [
            {
                "question": "Is the Earth flat?",
                "correct_answer": "False",
                "explanation": "The Earth is spherical."
            }
        ]
        captured_output = io.StringIO()
        sys.stdout = captured_output

        _display_questions(questions, "true_false")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("True/False Questions", output)
        self.assertIn("Is the Earth flat?", output)
        self.assertIn("False", output)
        self.assertIn("The Earth is spherical", output)

    def test_displays_yes_no_questions(self):
        """Test that Yes/No questions are displayed correctly."""
        questions = [
            {
                "question": "Can birds fly?",
                "correct_answer": "Yes",
                "explanation": "Most birds have evolved for flight."
            }
        ]
        captured_output = io.StringIO()
        sys.stdout = captured_output

        _display_questions(questions, "yes_no")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("Yes/No Questions", output)
        self.assertIn("Can birds fly?", output)
        self.assertIn("Yes", output)

    def test_displays_question_count(self):
        """Test that total question count is displayed."""
        questions = [
            {"question": "Q1?", "correct_answer": "Yes", "explanation": "E1"},
            {"question": "Q2?", "correct_answer": "No", "explanation": "E2"},
        ]
        captured_output = io.StringIO()
        sys.stdout = captured_output

        _display_questions(questions, "yes_no")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("2 total", output)

    def test_displays_all_question_components(self):
        """Test that all question components are displayed."""
        questions = [
            {
                "question": "Test Q?",
                "correct_answer": "True",
                "explanation": "Test explanation here."
            }
        ]
        captured_output = io.StringIO()
        sys.stdout = captured_output

        _display_questions(questions, "true_false")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("Question 1:", output)
        self.assertIn("Test Q?", output)
        self.assertIn("Answer:", output)
        self.assertIn("True", output)
        self.assertIn("Explanation:", output)
        self.assertIn("Test explanation here.", output)


if __name__ == "__main__":
    unittest.main()
