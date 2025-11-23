# MCQ Generator CLI - Quick Start

## Installation (One-time setup)

```bash
pip install openai python-dotenv litellm requests
```

Create `.env` file with your API key:
```
OPENAI_API_KEY=your_key_here
```

## Basic Usage

### 1️⃣ Initialize Model
```bash
python cli.py init-model --provider openai --model gpt-4o-mini
```

### 2️⃣ Generate Questions
```bash
# Simple - generate 5 medium questions
python cli.py generate -s "Python" -c 5 --save python.json

# Advanced - specify difficulty and show answers
python cli.py generate --specialization "History" -d hard -c 3 --show-answers
```

### 3️⃣ View Questions
```bash
python cli.py load python.json --show-answers
```

### 4️⃣ Get Explanation
```bash
python cli.py explain python.json -q 1
```

### 5️⃣ Translate
```bash
python cli.py translate python.json -l hindi --save
```

### 6️⃣ Get Prerequisites
```bash
python cli.py prerequisites python.json -q 2
```

### 7️⃣ Similar Question
```bash
python cli.py similar python.json -q 1
```

## Common Patterns

```bash
# Generate and save in one go
python cli.py generate -s "Biology" -c 5 --save biology.json

# Get answers while viewing
python cli.py load biology.json --show-answers

# Explain multiple questions quickly
python cli.py explain biology.json -q 1
python cli.py explain biology.json -q 2
python cli.py explain biology.json -q 3
```

## Help & Support

```bash
python cli.py --help              # General help
python cli.py generate --help      # Command-specific help
python cli.py info                 # Show info page
```

## File Structure

After generation, you'll have `questions.json`:
```json
{
  "specialization": "Python",
  "generated_at": "2024-11-23T...",
  "question_count": 5,
  "questions": [
    {
      "question": "...",
      "options": {"A": "...", "B": "...", ...},
      "correct_answer": "A"
    }
  ]
}
```

## Difficulty Levels
- `easy` - Basic concepts
- `medium` - Application of concepts
- `hard` - Complex, multi-step reasoning

## Providers
- `openai` - GPT models (gpt-4o-mini, gpt-4o, gpt-4)
- `claude` - Claude models via LiteLLM
- `litellm` - Other providers (ollama, cohere, etc.)

---

For detailed documentation, see `CLI_USAGE.md`
