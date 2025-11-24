# MCQ Generator CLI - Setup Guide

Complete step-by-step setup instructions to get started with the MCQ Generator CLI.

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- An API key from one of:
  - OpenAI (for GPT models)
  - Anthropic (for Claude models)
  - Other LiteLLM providers

## Step 1: Verify Python Installation

```bash
python --version
# or
python3 --version
```

Should show Python 3.7 or higher.

## Step 2: Navigate to Project Directory

```bash
cd path/to/mcq_generator
```

## Step 3: Set Up Virtual Environment (Recommended)

If you haven't created a virtual environment yet:

```bash
python -m venv venv
```

Activate the virtual environment:

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal.

## Step 4: Install Dependencies

With the virtual environment activated:

```bash
pip install openai litellm python-dotenv requests
```

Or use the venv already present:
```bash
source venv/bin/activate  # macOS/Linux
pip install openai litellm python-dotenv requests
```

## Step 5: Configure API Keys

### Option A: Using .env File (Recommended)

Create a `.env` file in the project directory:

```bash
touch .env
```

Add your API key(s):

**For OpenAI:**
```
OPENAI_API_KEY=sk-...
```

**For Claude/Anthropic:**
```
ANTHROPIC_API_KEY=sk-ant-...
```

**For other providers**, check LiteLLM documentation.

### Option B: Using Environment Variables

Set environment variables directly in your shell:

**macOS/Linux:**
```bash
export OPENAI_API_KEY="sk-..."
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-..."
```

## Step 6: Verify Installation

Test that everything is set up correctly:

```bash
python cli.py --help
```

You should see the help message with available commands.

Test with the info command:
```bash
python cli.py info
```

## Step 7: Initialize a Model

Before generating questions, initialize your AI model:

```bash
python cli.py init-model --provider openai --model gpt-4o-mini
```

This should output:
```
✓ OpenAI model 'gpt-4o-mini' initialized
```

## Step 8: Generate Your First Questions

```bash
python cli.py generate --specialization "Python Programming" --count 3 --save first_questions.json
```

You should see:
```
📚 Generating 3 medium questions on 'Python Programming'...
✓ Successfully generated 3 questions

✓ Questions saved to 'first_questions.json'
```

## Step 9: View Generated Questions

```bash
python cli.py load first_questions.json --show-answers
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'openai'"

**Solution:** Make sure you activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate  # Activate venv
pip install openai litellm python-dotenv requests
```

### Issue: "Error: Failed to initialize model"

**Solution:** Check your API key:
1. Verify the key is correctly set in `.env`
2. Check the key is valid and has credits
3. Make sure you're using the correct provider

For OpenAI:
```bash
# Get key from https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-..."
```

### Issue: "File 'questions.json' not found"

**Solution:** Make sure the file exists:
```bash
python cli.py generate -s "Python" --save questions.json
python cli.py load questions.json
```

### Issue: "Invalid question number. Valid range: 1-5"

**Solution:** The question number must be within the range of generated questions. Check how many questions exist:
```bash
python cli.py load questions.json
# Count the questions, then use a number within that range
python cli.py explain questions.json -q 1
```

### Issue: "Command not found" or "No module named 'question_generator'"

**Solution:** Make sure you're in the correct directory:
```bash
# Navigate to the project directory
cd path/to/mcq_generator
python cli.py --help
```

## API Key Acquisition

### OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key and save it to `.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```

### Anthropic API Key (Claude)

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API keys section
4. Create a new key
5. Save it to `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

## Next Steps

1. Read `QUICK_START.md` for common usage patterns
2. Check `CLI_USAGE.md` for detailed command documentation
3. Review `CLI_FEATURES.md` for all available features

## Common Usage Patterns

### Generate and Save Questions
```bash
python cli.py generate -s "Biology" -c 5 --save biology.json
```

### View with Answers
```bash
python cli.py load biology.json --show-answers
```

### Get Explanations
```bash
python cli.py explain biology.json -q 1
```

### Translate to Hindi
```bash
python cli.py translate biology.json -l hindi --save
```

## Tips for Best Results

1. **Model Selection**: `gpt-4o-mini` is fast and affordable; `gpt-4o` is more accurate
2. **Difficulty Levels**: Start with "easy" or "medium" for testing
3. **Token Limits**: Increase max-tokens for more detailed questions
4. **Question Count**: Start with 3-5 to test before generating large batches
5. **Specialization**: Be specific (e.g., "Python List Comprehension" vs "Python")

## Getting Help

```bash
# General help
python cli.py --help

# Command-specific help
python cli.py generate --help
python cli.py explain --help

# Show information and quick start
python cli.py info
```

## Next: Create a Test Question

Once set up, try this complete workflow:

```bash
# 1. Initialize model
python cli.py init-model --provider openai

# 2. Generate 2 easy questions on History
python cli.py generate -s "Ancient Egypt" -d easy -c 2 --save egypt.json

# 3. View them with answers
python cli.py load egypt.json --show-answers

# 4. Get explanation for first question
python cli.py explain egypt.json -q 1

# 5. Generate similar question
python cli.py similar egypt.json -q 1
```

Congratulations! You're now set up to use the MCQ Generator CLI. Happy question generating! 🎉
