"""
Unit tests for MCQ Generator modules
"""

import unittest
from prompt_builder import PromptBuilder
from question_generator import QuestionGenerator


class TestPromptBuilder(unittest.TestCase):
    """Test PromptBuilder class"""

    def setUp(self):
        self.builder = PromptBuilder()

    def test_mcq_generation_prompt_single_answer(self):
        """Test MCQ prompt generation with single correct answer"""
        prompt = self.builder.get_mcq_generation_prompt(
            "Physics", "Medium", 2, 4, num_correct_answers=1
        )
        self.assertIn("Physics", prompt)
        self.assertIn("Medium", prompt)
        self.assertIn("with only one correct answer", prompt)
        self.assertIn("A. [Option A]", prompt)
        self.assertIn("B. [Option B]", prompt)
        self.assertIn("C. [Option C]", prompt)
        self.assertIn("D. [Option D]", prompt)

    def test_mcq_generation_prompt_multiple_answers(self):
        """Test MCQ prompt generation with multiple correct answers"""
        prompt = self.builder.get_mcq_generation_prompt(
            "Chemistry", "Hard", 3, 5, num_correct_answers=2
        )
        self.assertIn("Chemistry", prompt)
        self.assertIn("Hard", prompt)
        self.assertIn("with 2 correct answer(s)", prompt)
        self.assertIn("A. [Option A]", prompt)
        self.assertIn("E. [Option E]", prompt)

    def test_mcq_generation_prompt_dynamic_options(self):
        """Test dynamic option generation for different option counts"""
        for num_opts in [2, 3, 4, 5, 6]:
            prompt = self.builder.get_mcq_generation_prompt(
                "History", "Easy", 1, num_opts
            )
            # Verify correct number of options generated
            expected_letters = [chr(65 + i) for i in range(num_opts)]
            for letter in expected_letters:
                self.assertIn(f"{letter}. [Option {letter}]", prompt)

    def test_text_translation_prompt(self):
        """Test translation prompt generation"""
        prompt = self.builder.get_text_translation_prompt(
            "Hello World", "French"
        )
        self.assertIn("Hello World", prompt)
        self.assertIn("French", prompt)
        self.assertIn("Translate", prompt)

    def test_explain_answer_prompt_with_options(self):
        """Test explanation prompt with options"""
        prompt = self.builder.get_explain_answer_prompt(
            "What is X?", ["Option A", "Option B"], "A"
        )
        self.assertIn("What is X?", prompt)
        self.assertIn("A", prompt)
        self.assertIn("Explain", prompt)

    def test_prerequisites_prompt(self):
        """Test prerequisites prompt generation"""
        prompt = self.builder.get_prerequisites_prompt(
            "Newton's Laws", None
        )
        self.assertIn("Newton's Laws", prompt)
        self.assertIn("background material", prompt)

    def test_similar_question_prompt(self):
        """Test similar question generation prompt"""
        prompt = self.builder.get_similar_question_generation_prompt(
            "What is gravity?", num_questions=2, with_options=True
        )
        self.assertIn("What is gravity?", prompt)
        self.assertIn("2", prompt)

    def test_true_false_prompt(self):
        """Test True/False question prompt"""
        prompt = self.builder.get_true_false_question_generation_prompt(
            "Earth is flat", num_questions=1
        )
        self.assertIn("Earth is flat", prompt)
        self.assertIn("True/False", prompt)

    def test_yes_no_prompt(self):
        """Test Yes/No question prompt"""
        prompt = self.builder.get_yes_no_question_generation_prompt(
            "Do plants need water?", num_questions=1
        )
        self.assertIn("Do plants need water?", prompt)
        self.assertIn("Yes/No", prompt)

    def test_mcq_generation_prompt_zero_answers(self):
        """Test MCQ prompt with 0 correct answers (None of the Above)"""
        prompt = self.builder.get_mcq_generation_prompt(
            "Biology", "Easy", 1, 4, num_correct_answers=0
        )
        self.assertIn("'None of the Above' as the only correct answer", prompt)
        self.assertIn("None of the Above", prompt)

    def test_mcq_generation_prompt_all_answers(self):
        """Test MCQ prompt with all options as correct (All of the Above)"""
        prompt = self.builder.get_mcq_generation_prompt(
            "Chemistry", "Medium", 1, 4, num_correct_answers=4
        )
        self.assertIn("'All of the Above' as the only correct answer", prompt)
        self.assertIn("All of the Above", prompt)


class TestQuestionGenerator(unittest.TestCase):
    """Test QuestionGenerator class"""

    def setUp(self):
        self.generator = QuestionGenerator("openai/gpt-4o-mini")

    def test_parse_correct_answers_single(self):
        """Test parsing single correct answer"""
        result = self.generator._parse_correct_answers("A")
        self.assertEqual(result, ["A"])

    def test_parse_correct_answers_multiple_comma(self):
        """Test parsing multiple answers separated by commas"""
        result = self.generator._parse_correct_answers("A, B, C")
        self.assertEqual(result, ["A", "B", "C"])

    def test_parse_correct_answers_multiple_and(self):
        """Test parsing multiple answers separated by 'and'"""
        result = self.generator._parse_correct_answers("A and B")
        self.assertEqual(result, ["A", "B"])

    def test_parse_correct_answers_all_of_above(self):
        """Test parsing 'All of the Above'"""
        result = self.generator._parse_correct_answers("All of the Above")
        self.assertEqual(result, ["All of the Above"])

    def test_parse_correct_answers_none_of_above(self):
        """Test parsing 'None of the Above'"""
        result = self.generator._parse_correct_answers("None of the Above")
        self.assertEqual(result, ["None of the Above"])

    def test_parse_correct_answers_case_insensitive(self):
        """Test case insensitivity"""
        result1 = self.generator._parse_correct_answers("all of the above")
        result2 = self.generator._parse_correct_answers("NONE OF THE ABOVE")
        self.assertEqual(result1, ["All of the Above"])
        self.assertEqual(result2, ["None of the Above"])

    def test_parse_question_basic(self):
        """Test basic question parsing"""
        response = """Question: What is 2 + 2?
A. 3
B. 4
C. 5
D. 6
Correct Answer: B"""
        result = self.generator.parse_question(response, 4)
        self.assertEqual(result["question"], "What is 2 + 2?")
        self.assertEqual(result["options"]["A"], "3")
        self.assertEqual(result["options"]["B"], "4")
        self.assertEqual(result["options"]["C"], "5")
        self.assertEqual(result["options"]["D"], "6")
        self.assertEqual(result["correct_answer"], ["B"])

    def test_parse_question_multiple_answers(self):
        """Test parsing question with multiple correct answers"""
        response = """Question: Which are prime numbers?
A. 2
B. 3
C. 4
D. 5
Correct Answer: A, B, D"""
        result = self.generator.parse_question(response, 4)
        self.assertEqual(result["question"], "Which are prime numbers?")
        self.assertEqual(result["correct_answer"], ["A", "B", "D"])

    def test_parse_question_empty_response(self):
        """Test parsing returns empty dict for invalid response"""
        response = "This is not a valid question format"
        result = self.generator.parse_question(response, 4)
        self.assertEqual(result, {})

    def test_parse_question_five_options(self):
        """Test parsing with 5 options"""
        response = """Question: What is the capital of France?
A. London
B. Berlin
C. Paris
D. Madrid
E. Rome
Correct Answer: C"""
        result = self.generator.parse_question(response, 5)
        self.assertIn("E", result["options"])
        self.assertEqual(result["options"]["E"], "Rome")

    def test_question_generator_initialization(self):
        """Test QuestionGenerator initialization"""
        gen = QuestionGenerator("claude/claude-3-opus")
        self.assertEqual(gen.model, "claude/claude-3-opus")
        self.assertIsNotNone(gen.prompt_builder)


class TestMCQGenerationEngine(unittest.TestCase):
    """Test MCQGenerationEngine class"""

    def setUp(self):
        from mcq_generate_cli import MCQGenerationEngine
        self.engine = MCQGenerationEngine("openai/gpt-4o-mini")

    def test_validate_params_valid(self):
        """Test parameter validation with valid inputs"""
        # Should not raise
        self.engine._validate_params(4, 1)
        self.engine._validate_params(5, 2)

    def test_validate_params_invalid_options(self):
        """Test parameter validation with invalid option count"""
        with self.assertRaises(ValueError) as context:
            self.engine._validate_params(1, 1)
        self.assertIn("options must be > 1", str(context.exception))

    def test_validate_params_valid_zero_correct_answers(self):
        """Test parameter validation allows 0 correct answers (None of the Above)"""
        # Should not raise - 0 is valid for "None of the Above"
        self.engine._validate_params(4, 0)

    def test_validate_params_invalid_negative_correct_answers(self):
        """Test parameter validation with negative correct answer count"""
        with self.assertRaises(ValueError) as context:
            self.engine._validate_params(4, -1)
        self.assertIn("correct answers must be >= 0", str(context.exception))

    def test_display_questions_empty(self):
        """Test displaying empty question list"""
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.engine.display_questions([])
        sys.stdout = sys.__stdout__
        self.assertIn("No questions to display", captured_output.getvalue())

    def test_display_questions_with_data(self):
        """Test displaying questions with data"""
        import io
        import sys
        questions = [{
            "question": "What is 2+2?",
            "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
            "correct_answer": ["B"]
        }]
        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.engine.display_questions(questions)
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("What is 2+2?", output)
        self.assertIn("Answer: B", output)


if __name__ == '__main__':
    unittest.main()
