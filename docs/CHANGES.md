# MCQ Generator - Recent Changes

## Overview
Refactored and enhanced the MCQ Generator with improved architecture, configuration management, retry logic, and progress tracking.

## New Files Created

### 1. `mcq_generator.py`
Core module containing:
- **`QuestionConfig` dataclass** - Configuration for MCQ generation with fields:
  - Required: `field`, `difficulty`, `num_questions`, `num_options`
  - Optional: `num_correct_answers` (default: 1), `max_tokens` (default: 3000), `subfield` (default: None)

- **`MCQGenerator` class** - Renamed from `MCQGenerationEngine`, handles:
  - Question generation with automatic JSON file saving
  - Question parsing and validation
  - Question storage to JSON format
  - Question loading from JSON files
  - Question display with formatted output
  - All methods use tenacity for retry logic on transient failures

### 2. `requirements.txt`
Dependencies for the project:
- `litellm` - LLM API client
- `tenacity` - Retry mechanism library
- `tqdm` - Progress bar library

### 3. `Makefile`
Project automation with targets:
- `make help` - Show available commands
- `make venv` - Create Python virtual environment (mcqenv)
- `make install` - Install dependencies in venv
- `make test` - Run unit tests
- `make run` - Run the CLI
- `make clean` - Remove generated files and cache
- `make lint` - Run code linting
- `make format` - Format code with black

## Modified Files

### 1. `mcq_generate_cli.py`
- Imports `MCQGenerator`, `QuestionConfig`, and `setup_logger` from `mcq_generator.py`
- Removed duplicate class definitions and logging setup
- Updated to use `QuestionConfig` dataclass for configuration
- Updated to call `engine.generate(config, filename)` which returns filepath
- Loads and displays questions from the saved JSON file

### 2. `question_generator.py`
Enhanced with:
- **Tenacity integration** for retry logic:
  - `_call_llm()` method with retry decorator
  - Max 3 attempts with exponential backoff (2-10 seconds)
  - Gracefully handles transient API failures
- **Tqdm progress tracking**:
  - Progress bar while parsing LLM response into questions
  - Description: "Parsing questions"
  - Unit: "q" (questions)

## Key Improvements

### 1. Architecture
- **Separation of Concerns**: Business logic in `mcq_generator.py`, CLI in `mcq_generate_cli.py`
- **Reusability**: Core functionality can be imported and used by other modules
- **Testability**: Separated logic makes unit testing easier

### 2. Configuration Management
- **QuestionConfig dataclass**: Type-safe, self-documenting configuration
- **Single parameter passing**: `generate(config)` instead of 7 parameters
- **Easy to extend**: Add new fields without changing function signatures

### 3. Reliability
- **Tenacity retry logic**: Automatic retries with exponential backoff
- **Graceful error handling**: Returns empty list on failure instead of raising
- **Comprehensive logging**: All operations logged for debugging

### 4. User Experience
- **Progress tracking with tqdm**:
  - Visual feedback during question parsing
  - Visual feedback during question display
  - Smooth, non-intrusive progress bars
- **Mandatory file storage**: Questions always persisted to JSON
- **Auto-generated filenames**: Timestamps included by default

### 5. Development Experience
- **Makefile**: Convenient commands for common tasks
- **Virtual environment management**: `make venv` and `make install`
- **Code quality tools**: Lint and format targets included
- **Clean installation**: All dependencies in requirements.txt

## Usage

### Setup
```bash
make venv
make install
```

### Generate Questions
```bash
python mcq_generate_cli.py \
  --field "Physics" \
  --difficulty medium \
  --count 5 \
  --options 4 \
  --save physics_questions.json
```

### Using the Library
```python
from mcq_generator import MCQGenerator, QuestionConfig

config = QuestionConfig(
    field="Biology",
    difficulty="Hard",
    num_questions=10,
    num_options=5,
    num_correct_answers=1
)

generator = MCQGenerator("openai/gpt-4o-mini")
filepath = generator.generate(config)
questions = generator.load_questions(filepath)
generator.display_questions(questions)
```

## Technical Details

### Retry Strategy (Tenacity)
- **Strategy**: Exponential backoff
- **Max Attempts**: 3
- **Wait Time**: 2-10 seconds between retries
- **Exception Handling**: Retries on all exceptions
- **Re-raise**: Raises exception after all retries exhausted

### Progress Tracking (Tqdm)
- **Parsing Progress**: Shows progress while parsing LLM response
- **Display Progress**: Shows progress while displaying questions
- **Unit**: "q" (questions)
- **Format**: Standard tqdm format with ETA

### File Storage
- **Format**: JSON with metadata
- **Structure**:
  ```json
  {
    "field": "...",
    "subfield": "...",
    "generated_at": "ISO timestamp",
    "question_count": N,
    "questions": [...]
  }
  ```
- **Auto-filename**: `mcq_{field}_{timestamp}.json`
- **Custom filename**: Supported via optional parameter

## Testing

Run unit tests:
```bash
make test
```

Or directly:
```bash
python -m unittest discover tests -v
```

## Code Quality

Lint code:
```bash
make lint
```

Format code:
```bash
make format
```

## Summary

The refactoring improves code maintainability, reliability, and user experience while introducing modern Python best practices. The separation of concerns makes the code easier to test, extend, and integrate into other projects.
