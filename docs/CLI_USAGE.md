# MCQ Generator CLI - Usage Guide

A command-line interface for generating multiple-choice questions using AI models (OpenAI, Claude, or any LiteLLM provider).

## Installation

Make sure you have Python 3.7+ installed. Install dependencies:

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install openai python-dotenv litellm requests
```

## Setup

### 1. Set API Keys

Create a `.env` file in the project directory with your API keys:

```bash
# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# For Claude (if using LiteLLM)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 2. Initialize the Model

Before generating questions, you need to initialize the AI model:

```bash
python cli.py init-model --provider openai --model gpt-4o-mini
```

**Provider options:**
- `openai` - Use OpenAI models
- `claude` - Use Claude models via LiteLLM
- `litellm` - Use other LiteLLM providers

**Example models:**
- OpenAI: `gpt-4o-mini`, `gpt-4o`, `gpt-4`
- Claude: `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`

## Commands

### 1. Generate Questions

Generate MCQ questions on any topic:

```bash
python cli.py generate --specialization "Python Programming" --count 5
```

**Options:**
- `--specialization, -s` (required) - Topic/subject
- `--difficulty, -d` - Level: `easy`, `medium`, `hard` (default: medium)
- `--count, -c` - Number of questions (default: 5)
- `--max-tokens` - Maximum tokens for generation (default: 3000)
- `--save` - Save to file (provide filename)
- `--show-answers` - Display correct answers

**Examples:**
```bash
# Generate 3 hard questions on Biology
python cli.py generate --specialization "Biology" --difficulty hard --count 3

# Generate 5 questions and save to file
python cli.py generate -s "History" -c 5 --save history_questions.json

# Generate questions and show answers
python cli.py generate --specialization "Math" --show-answers --save math.json
```

### 2. Load Questions

Load and display previously saved questions:

```bash
python cli.py load questions.json
```

**Options:**
- `filename` (required) - Path to JSON file
- `--show-answers` - Display correct answers

**Example:**
```bash
python cli.py load my_questions.json --show-answers
```

### 3. Explain a Question

Get a detailed explanation for a specific question:

```bash
python cli.py explain questions.json --question-num 1 --max-tokens 1500
```

**Options:**
- `filename` (required) - Path to JSON file
- `--question-num, -q` (required) - Question number (1-based index)
- `--max-tokens` - Maximum tokens for explanation (default: 1500)

**Example:**
```bash
python cli.py explain history.json -q 2
```

### 4. Translate Questions

Translate questions to another language:

```bash
python cli.py translate questions.json --language hindi --save
```

**Options:**
- `filename` (required) - Path to JSON file
- `--language, -l` - Target language: `hindi`, `spanish`, `french` (default: hindi)
- `--save` - Save translated questions to file

**Examples:**
```bash
# Translate to Hindi
python cli.py translate questions.json --language hindi

# Translate to Spanish and save
python cli.py translate questions.json -l spanish --save
```

### 5. Get Prerequisites

Get prerequisite knowledge for understanding a question:

```bash
python cli.py prerequisites questions.json --question-num 1
```

**Options:**
- `filename` (required) - Path to JSON file
- `--question-num, -q` (required) - Question number (1-based index)

**Example:**
```bash
python cli.py prerequisites physics.json -q 3
```

### 6. Generate Similar Question

Generate a similar question based on an existing one:

```bash
python cli.py similar questions.json --question-num 2
```

**Options:**
- `filename` (required) - Path to JSON file
- `--question-num, -q` (required) - Question number to use as reference (1-based index)

**Example:**
```bash
python cli.py similar math.json -q 1
```

### 7. Show Information

Display general information about the CLI:

```bash
python cli.py info
```

## Complete Workflow Example

```bash
# Step 1: Initialize OpenAI model
python cli.py init-model --provider openai --model gpt-4o-mini

# Step 2: Generate 5 medium difficulty questions on Python
python cli.py generate --specialization "Python Programming" --count 5 --save python_questions.json

# Step 3: View questions with answers
python cli.py load python_questions.json --show-answers

# Step 4: Get explanation for question 1
python cli.py explain python_questions.json -q 1

# Step 5: Get prerequisites for question 3
python cli.py prerequisites python_questions.json -q 3

# Step 6: Generate similar question to question 2
python cli.py similar python_questions.json -q 2

# Step 7: Translate to Hindi
python cli.py translate python_questions.json -l hindi --save
```

## JSON File Format

Questions are saved in the following format:

```json
{
  "specialization": "Python Programming",
  "generated_at": "2024-11-23T10:30:45.123456",
  "question_count": 5,
  "questions": [
    {
      "question": "What is the output of print(2 ** 3)?",
      "options": {
        "A": "6",
        "B": "8",
        "C": "9",
        "D": "5"
      },
      "correct_answer": "B"
    }
  ]
}
```

## Logging

All CLI operations are logged to `mcq_cli.log`. Check this file for debugging information.

## Troubleshooting

### Model Not Initialized
```
Error: Model not initialized. Please set up a model first.
```
**Solution:** Run `python cli.py init-model` before other commands.

### File Not Found
```
Error: File 'questions.json' not found.
```
**Solution:** Make sure the filename is correct and the file exists.

### API Key Issues
```
Error: Failed to initialize model
```
**Solution:** Check your `.env` file has the correct API key for your chosen provider.

### Invalid Question Number
```
Error: Invalid question number. Valid range: 1-5
```
**Solution:** Use a valid question number based on the total questions in your file.

## Getting Help

```bash
# General help
python cli.py --help

# Command-specific help
python cli.py generate --help
python cli.py explain --help
python cli.py translate --help
```

## Features

✅ Multiple AI providers (OpenAI, Claude, LiteLLM)
✅ Customizable difficulty levels (Easy, Medium, Hard)
✅ Generate 1 to 100+ questions at once
✅ Save questions to JSON format
✅ Load and review saved questions
✅ Get detailed explanations
✅ Translate to multiple languages
✅ Get prerequisite knowledge
✅ Generate similar questions
✅ Full CLI with help text
✅ Comprehensive logging

## Notes

- Questions are generated using AI models; ensure you review them for accuracy
- Keep your API keys secure and never commit them to version control
- Larger token values allow longer, more detailed questions
- Each command run is logged for reference
