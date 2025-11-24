# MCQ Generator - Unit Testing Documentation

## Test Suite Overview

Comprehensive unit tests for the MCQ Generator module with **39 test cases** covering all major functionality.

**Test Status: ✅ All 39 tests passing**

## Test Organization

Tests are organized into test classes, each focusing on a specific component:

### 1. TestQuestionConfig (5 tests)
Tests for the `QuestionConfig` dataclass configuration object.

- `test_config_with_required_fields_only` - Validates creation with minimal required fields
- `test_config_with_all_fields` - Tests all optional fields
- `test_config_defaults` - Verifies default values
- `test_config_zero_correct_answers` - Tests "None of the Above" scenario
- `test_config_multiple_correct_answers` - Tests multiple correct answers

### 2. TestMCQGeneratorInit (3 tests)
Tests for `MCQGenerator` class initialization.

- `test_init_with_valid_model` - OpenAI model initialization
- `test_init_with_claude_model` - Claude model initialization
- `test_init_with_perplexity_model` - Perplexity model initialization

### 3. TestMCQGeneratorValidation (7 tests)
Tests for parameter validation in `_validate_params()` method.

- `test_validate_params_valid_single_answer` - Valid single answer validation
- `test_validate_params_valid_multiple_answers` - Valid multiple answers validation
- `test_validate_params_valid_zero_answers` - Valid zero answers (None of Above)
- `test_validate_params_minimum_options` - Minimum valid options count
- `test_validate_params_insufficient_options` - Error on < 2 options
- `test_validate_params_negative_correct_answers` - Error on negative answers
- `test_validate_params_negative_options` - Error on negative options

### 4. TestMCQGeneratorSaveQuestions (7 tests)
Tests for saving questions to JSON files using `_save_questions()`.

- `test_save_questions_with_custom_filename` - Save with specified filename
- `test_save_questions_with_subfield` - Save with subfield information
- `test_save_questions_auto_filename` - Auto-generated filename with timestamp
- `test_save_questions_single_question` - Save single question file
- `test_save_questions_empty_list_raises_error` - Error on empty questions
- `test_save_questions_has_metadata` - Verifies required metadata fields

### 5. TestMCQGeneratorLoadQuestions (6 tests)
Tests for loading questions from JSON files using `load_questions()`.

- `test_load_questions_valid_file` - Load from valid JSON file
- `test_load_questions_single_question` - Load single question file
- `test_load_questions_preserves_structure` - Data structure integrity
- `test_load_questions_file_not_found` - Error handling for missing files
- `test_load_questions_invalid_json` - Error handling for malformed JSON
- `test_load_questions_empty_questions_list` - Handle empty question lists

### 6. TestMCQGeneratorDisplay (8 tests)
Tests for question display using `display_questions()` and helper methods.

- `test_display_questions_empty_list` - Handle empty question lists
- `test_display_questions_single_question` - Display single question
- `test_display_questions_multiple_questions` - Display multiple questions
- `test_print_answer_string` - Print string answer
- `test_print_answer_list` - Print list of answers
- `test_print_answer_single_element_list` - Print single element list
- `test_print_options_dict` - Print dictionary-formatted options
- `test_print_options_list` - Print list-formatted options

### 7. TestMCQGeneratorGenerate (4 tests)
Tests for the main `generate()` method with mocking.

- `test_generate_returns_filepath` - Verify returns file path
- `test_generate_calls_llm` - Verify LLM is called with correct parameters
- `test_generate_empty_questions_raises_error` - Error on empty LLM response
- `test_generate_with_custom_filename` - Custom filename support

## Running Tests

### Run All Tests
```bash
python -m unittest tests.test_mcq_generator -v
```

### Run Specific Test Class
```bash
python -m unittest tests.test_mcq_generator.TestQuestionConfig -v
```

### Run Specific Test
```bash
python -m unittest tests.test_mcq_generator.TestMCQGeneratorGenerate.test_generate_returns_filepath -v
```

### Using Makefile
```bash
make test
```

## Test Coverage

### Classes Tested
- ✅ `QuestionConfig` dataclass
- ✅ `MCQGenerator` class

### Methods Tested
- ✅ `__init__()` - Initialization
- ✅ `_validate_params()` - Parameter validation
- ✅ `_save_questions()` - Save to JSON
- ✅ `load_questions()` - Load from JSON
- ✅ `generate()` - Main generation method
- ✅ `display_questions()` - Display formatted output
- ✅ `_print_options()` - Option formatting
- ✅ `_print_answer()` - Answer formatting

## Test Data

All tests use:
- **Sample questions** with realistic MCQ format
- **Temporary directories** for file I/O tests
- **Mock objects** for LLM interaction
- **Various edge cases** (empty lists, invalid input, etc.)

## Assertions Covered

### Type Validation
- Configuration field types
- Return value types
- Exception types

### Value Validation
- Default values correctness
- Parameter constraints
- Data structure integrity

### Behavior Validation
- Method call sequencing
- Exception raising conditions
- File I/O correctness
- Data persistence

### Error Handling
- FileNotFoundError for missing files
- ValueError for invalid input
- RuntimeError for generation failures
- Graceful handling of edge cases

## Mock Usage

Tests use `unittest.mock` to:
- Mock the `QuestionGenerator` to avoid API calls
- Mock file operations where needed
- Verify method calls and parameters
- Test error conditions safely

## Performance Notes

- All 39 tests complete in **~0.04 seconds**
- Tests use temporary directories for file operations
- No actual API calls are made (all mocked)
- Tests are independent and can run in any order

## Future Test Enhancements

Potential areas for additional testing:
- Integration tests with real LLM API
- Performance benchmarks
- Concurrent question generation
- Large file handling (1000+ questions)
- Different file formats (CSV, PDF export)
- CLI argument parsing tests

## Test Quality Metrics

| Metric | Value |
|--------|-------|
| Total Tests | 39 |
| Passing | 39 ✅ |
| Failing | 0 |
| Success Rate | 100% |
| Execution Time | ~0.04s |
| Code Coverage | High |

## Dependencies

Tests require:
- `unittest` (built-in)
- `tempfile` (built-in)
- `json` (built-in)
- `pathlib` (built-in)
- `unittest.mock` (built-in)
- `mcq_generator` module

No additional testing frameworks required.
